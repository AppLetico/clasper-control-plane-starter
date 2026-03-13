import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class PluginConfig:
    enabled: bool
    allow: List[str]
    deny: List[str]
    entries: Dict[str, Dict[str, Any]]
    slots: Dict[str, str]
    load_paths: List[str]


@dataclass
class AppConfig:
    port: int
    agent_jwt_secret: str
    plugin_config_path: Optional[str]
    plugin_paths: List[str]
    plugins: PluginConfig


def _load_plugin_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {}
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_config() -> AppConfig:
    port = int(os.getenv("CONTROL_PLANE_PORT", "9001"))
    agent_jwt_secret = os.getenv("AGENT_JWT_SECRET", "")
    plugin_config_path = os.getenv("CONTROL_PLANE_PLUGIN_CONFIG_PATH")
    plugin_paths = [
        p.strip()
        for p in os.getenv("CONTROL_PLANE_PLUGIN_PATHS", "./plugins").split(",")
        if p.strip()
    ]

    raw = _load_plugin_config(plugin_config_path).get("plugins", {})
    plugins = PluginConfig(
        enabled=bool(raw.get("enabled", True)),
        allow=list(raw.get("allow", [])),
        deny=list(raw.get("deny", [])),
        entries=dict(raw.get("entries", {})),
        slots=dict(raw.get("slots", {})),
        load_paths=list(raw.get("load", {}).get("paths", [])),
    )

    return AppConfig(
        port=port,
        agent_jwt_secret=agent_jwt_secret,
        plugin_config_path=plugin_config_path,
        plugin_paths=plugin_paths,
        plugins=plugins,
    )
