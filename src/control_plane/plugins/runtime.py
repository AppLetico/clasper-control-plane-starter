from dataclasses import dataclass
from typing import Any, Dict

from .registry import PluginRegistry


class PluginBlocked(Exception):
    def __init__(self, message: str, status_code: int = 403):
        super().__init__(message)
        self.status_code = status_code


@dataclass
class PluginRuntime:
    registry: PluginRegistry
    config: Dict[str, Any]

    def register_hook(self, name: str, handler) -> None:
        self.registry.register_hook(name, handler)

    def register_tool(self, name: str, tool: Dict[str, Any]) -> None:
        self.registry.register_tool(name, tool)

    def register_command(self, name: str, handler) -> None:
        self.registry.register_command(name, handler)

    def register_service(self, name: str, handler) -> None:
        self.registry.register_service(name, handler)

    PluginBlocked = PluginBlocked
