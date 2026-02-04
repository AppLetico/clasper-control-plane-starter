import json
import re
from typing import Dict, Any


def register(api) -> None:
    denylist = api.config.get("denylist", [])
    case_sensitive = bool(api.config.get("case_sensitive", False))
    flags = 0 if case_sensitive else re.IGNORECASE
    patterns = [re.compile(pattern, flags=flags) for pattern in denylist]

    def _check(payload: Dict[str, Any]) -> None:
        body = payload.get("payload", {})
        text = json_dump(body)
        for pattern in patterns:
            if pattern.search(text):
                raise api.PluginBlocked("Blocked by prompt guard policy")

    api.register_hook("before_task_create", _check)
    api.register_hook("before_message_post", _check)
    api.register_hook("before_document_post", _check)


def json_dump(payload: Dict[str, Any]) -> str:
    try:
        return json.dumps(payload)
    except Exception:
        return str(payload)
