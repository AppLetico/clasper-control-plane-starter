from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


Hook = Callable[[Dict[str, Any]], None]
Tool = Dict[str, Any]
Command = Callable[[Dict[str, Any]], Any]
Service = Callable[[], None]


@dataclass
class PluginRegistry:
    hooks: Dict[str, List[Hook]] = field(default_factory=dict)
    tools: Dict[str, Tool] = field(default_factory=dict)
    commands: Dict[str, Command] = field(default_factory=dict)
    services: Dict[str, Service] = field(default_factory=dict)

    def register_hook(self, name: str, handler: Hook) -> None:
        self.hooks.setdefault(name, []).append(handler)

    def register_tool(self, name: str, tool: Tool) -> None:
        self.tools[name] = tool

    def register_command(self, name: str, handler: Command) -> None:
        self.commands[name] = handler

    def register_service(self, name: str, handler: Service) -> None:
        self.services[name] = handler
