import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PluginManifest:
    id: str
    name: str
    version: str
    entry: str
    kind: Optional[str]
    config_schema: Dict[str, Any]
    ui_hints: Dict[str, Any]


def load_manifest(path: str) -> PluginManifest:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Manifest not found: {path}")
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    for key in ("id", "name", "version", "entry"):
        if key not in data:
            raise ValueError(f"Manifest missing required field: {key}")

    return PluginManifest(
        id=data["id"],
        name=data["name"],
        version=data["version"],
        entry=data["entry"],
        kind=data.get("kind"),
        config_schema=data.get("configSchema", {}),
        ui_hints=data.get("uiHints", {}),
    )
