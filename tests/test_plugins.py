import json
import os
import sys
import tempfile
from typing import Optional

sys.path.append("src")

from control_plane.config import load_config
from control_plane.plugins.loader import load_plugins
from control_plane.plugins.runtime import PluginBlocked


def _write_plugin(root: str, plugin_id: str, kind: Optional[str] = None):
    os.makedirs(root, exist_ok=True)
    manifest = {
        "id": plugin_id,
        "name": "Test Plugin",
        "version": "0.1.0",
        "entry": "plugin.py",
    }
    if kind:
        manifest["kind"] = kind
    with open(os.path.join(root, "openclaw.plugin.json"), "w", encoding="utf-8") as handle:
        json.dump(manifest, handle)
    with open(os.path.join(root, "plugin.py"), "w", encoding="utf-8") as handle:
        handle.write(
            "def register(api):\n"
            f"    api.register_tool('{plugin_id}_tool', {{'name': '{plugin_id}_tool'}})\n"
        )


def test_plugin_discovery_and_allowlist():
    with tempfile.TemporaryDirectory() as temp_dir:
        plugin_dir = os.path.join(temp_dir, "plugin-a")
        _write_plugin(plugin_dir, "plugin-a")

        config_path = os.path.join(temp_dir, "config.json")
        with open(config_path, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "plugins": {
                        "enabled": True,
                        "allow": ["plugin-a"],
                        "deny": [],
                        "entries": {"plugin-a": {"enabled": True}},
                        "slots": {},
                        "load": {"paths": [plugin_dir]},
                    }
                },
                handle,
            )

        os.environ["CONTROL_PLANE_PLUGIN_CONFIG_PATH"] = config_path
        os.environ["CONTROL_PLANE_PLUGIN_PATHS"] = ""
        cfg = load_config()
        registry = load_plugins(cfg)
        assert "plugin-a_tool" in registry.tools


def test_plugin_slots():
    with tempfile.TemporaryDirectory() as temp_dir:
        plugin_a = os.path.join(temp_dir, "plugin-a")
        plugin_b = os.path.join(temp_dir, "plugin-b")
        _write_plugin(plugin_a, "plugin-a", kind="memory")
        _write_plugin(plugin_b, "plugin-b", kind="memory")

        config_path = os.path.join(temp_dir, "config.json")
        with open(config_path, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "plugins": {
                        "enabled": True,
                        "allow": [],
                        "deny": [],
                        "entries": {},
                        "slots": {"memory": "plugin-b"},
                        "load": {"paths": [plugin_a, plugin_b]},
                    }
                },
                handle,
            )

        os.environ["CONTROL_PLANE_PLUGIN_CONFIG_PATH"] = config_path
        os.environ["CONTROL_PLANE_PLUGIN_PATHS"] = ""
        cfg = load_config()
        registry = load_plugins(cfg)
        assert "plugin-b_tool" in registry.tools


def test_prompt_guard_blocks():
    with tempfile.TemporaryDirectory() as temp_dir:
        plugin_dir = os.path.join(temp_dir, "prompt_guard")
        os.makedirs(plugin_dir, exist_ok=True)
        manifest = {
            "id": "prompt-guard",
            "name": "Prompt Guard",
            "version": "0.1.0",
            "entry": "plugin.py",
        }
        with open(os.path.join(plugin_dir, "openclaw.plugin.json"), "w", encoding="utf-8") as handle:
            json.dump(manifest, handle)
        with open(os.path.join(plugin_dir, "plugin.py"), "w", encoding="utf-8") as handle:
            handle.write(
                "def register(api):\n"
                "    def hook(payload):\n"
                "        raise api.PluginBlocked('blocked')\n"
                "    api.register_hook('before_message_post', hook)\n"
            )

        config_path = os.path.join(temp_dir, "config.json")
        with open(config_path, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "plugins": {
                        "enabled": True,
                        "allow": [],
                        "deny": [],
                        "entries": {"prompt-guard": {"enabled": True}},
                        "slots": {},
                        "load": {"paths": [plugin_dir]},
                    }
                },
                handle,
            )

        os.environ["CONTROL_PLANE_PLUGIN_CONFIG_PATH"] = config_path
        os.environ["CONTROL_PLANE_PLUGIN_PATHS"] = ""
        cfg = load_config()
        registry = load_plugins(cfg)
        hook = registry.hooks["before_message_post"][0]
        try:
            hook({"payload": {"content": "secret"}})
            assert False, "expected PluginBlocked"
        except PluginBlocked:
            assert True
