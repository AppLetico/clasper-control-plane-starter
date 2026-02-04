from typing import Dict, Any


def register(api) -> None:
    greeting = api.config.get("greeting", "hello")

    def before_task(payload: Dict[str, Any]) -> None:
        _ = greeting

    api.register_hook("before_task_create", before_task)

    api.register_tool(
        "echo",
        {
            "name": "echo",
            "description": "Echo back a message.",
            "parameters": {"type": "object", "properties": {"message": {"type": "string"}}, "required": ["message"]},
        },
    )
