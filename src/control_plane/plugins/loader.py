import importlib
import importlib.util
import os
from dataclasses import dataclass
from importlib.metadata import entry_points
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..config import AppConfig
from .manifest import PluginManifest, load_manifest
from .registry import PluginRegistry
from .runtime import PluginRuntime


MANIFEST_FILENAME = "openclaw.plugin.json"


@dataclass
class LoadedPlugin:
    manifest: PluginManifest
    register: Callable[[PluginRuntime], None]
    config: Dict[str, Any]


def _load_entry_from_path(root: str, entry: str) -> Callable[[PluginRuntime], None]:
    if entry.endswith(".py"):
        module_path = os.path.join(root, entry)
        spec = importlib.util.spec_from_file_location(f"plugin_{os.path.basename(root)}", module_path)
        if not spec or not spec.loader:
            raise ImportError(f"Unable to load plugin entry: {module_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    else:
        module = importlib.import_module(entry)

    if hasattr(module, "register"):
        return getattr(module, "register")
    if hasattr(module, "plugin") and hasattr(module.plugin, "register"):
        return module.plugin.register
    raise ValueError("Plugin entry must expose register(api)")


def _discover_local_plugins(paths: List[str]) -> List[Tuple[str, PluginManifest, Callable[[PluginRuntime], None]]]:
    results: List[Tuple[str, PluginManifest, Callable[[PluginRuntime], None]]] = []
    for path in paths:
        if not path:
            continue
        if os.path.isfile(path):
            root = os.path.dirname(path)
            manifest_path = os.path.join(root, MANIFEST_FILENAME)
            manifest = load_manifest(manifest_path)
            register = _load_entry_from_path(root, manifest.entry)
            results.append((root, manifest, register))
            continue
        if os.path.isdir(path):
            manifest_path = os.path.join(path, MANIFEST_FILENAME)
            if os.path.exists(manifest_path):
                manifest = load_manifest(manifest_path)
                register = _load_entry_from_path(path, manifest.entry)
                results.append((path, manifest, register))
                continue
            for entry in os.listdir(path):
                child = os.path.join(path, entry)
                child_manifest = os.path.join(child, MANIFEST_FILENAME)
                if os.path.isdir(child) and os.path.exists(child_manifest):
                    manifest = load_manifest(child_manifest)
                    register = _load_entry_from_path(child, manifest.entry)
                    results.append((child, manifest, register))
    return results


def _discover_entrypoint_plugins() -> List[Tuple[str, PluginManifest, Callable[[PluginRuntime], None]]]:
    discovered: List[Tuple[str, PluginManifest, Callable[[PluginRuntime], None]]] = []
    eps = entry_points()
    if hasattr(eps, "select"):
        eps = eps.select(group="clasper.plugins")
    else:
        eps = eps.get("clasper.plugins", [])
    for ep in eps:
        plugin_obj = ep.load()
        if not hasattr(plugin_obj, "manifest") or not hasattr(plugin_obj, "register"):
            raise ValueError(f"Entrypoint {ep.name} must expose manifest and register")
        manifest_data = plugin_obj.manifest
        manifest = PluginManifest(
            id=manifest_data["id"],
            name=manifest_data["name"],
            version=manifest_data["version"],
            entry=manifest_data.get("entry", ep.value),
            kind=manifest_data.get("kind"),
            config_schema=manifest_data.get("configSchema", {}),
            ui_hints=manifest_data.get("uiHints", {}),
        )
        discovered.append((ep.value, manifest, plugin_obj.register))
    return discovered


def load_plugins(config: AppConfig) -> PluginRegistry:
    registry = PluginRegistry()
    if not config.plugins.enabled:
        return registry

    candidates = []
    candidates.extend(_discover_local_plugins(config.plugins.load_paths))
    candidates.extend(_discover_local_plugins(config.plugin_paths))
    candidates.extend(_discover_entrypoint_plugins())

    loaded_ids: Dict[str, LoadedPlugin] = {}
    for _, manifest, register in candidates:
        if manifest.id in loaded_ids:
            continue

        if config.plugins.allow and manifest.id not in config.plugins.allow:
            continue
        if manifest.id in config.plugins.deny:
            continue

        entry_cfg = config.plugins.entries.get(manifest.id, {})
        if entry_cfg.get("enabled") is False:
            continue

        if manifest.kind and manifest.kind in config.plugins.slots:
            slot_owner = config.plugins.slots[manifest.kind]
            if slot_owner != manifest.id and slot_owner != "none":
                continue

        loaded_ids[manifest.id] = LoadedPlugin(
            manifest=manifest,
            register=register,
            config=entry_cfg.get("config", {}),
        )

    for plugin in loaded_ids.values():
        runtime = PluginRuntime(registry=registry, config=plugin.config)
        plugin.register(runtime)

    return registry
