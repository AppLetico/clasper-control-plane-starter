import json
import subprocess
from typing import Any, Dict


def _run_qmd(command: str, args: list[str], timeout: float) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            [command] + args,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return {"error": "qmd not installed or not in PATH"}
    except subprocess.TimeoutExpired:
        return {"error": "qmd command timed out"}

    if proc.returncode != 0:
        return {"error": proc.stderr.strip() or "qmd command failed"}

    return {"output": proc.stdout.strip()}


def register(api) -> None:
    command = api.config.get("command", "qmd")
    default_mode = api.config.get("default_mode", "search")
    timeout = float(api.config.get("timeout_seconds", 30))

    def qmd_search(args: Dict[str, Any]) -> Dict[str, Any]:
        query = args.get("query")
        if not query:
            return {"error": "query is required"}
        mode = args.get("mode", default_mode)
        collection = args.get("collection")
        limit = args.get("limit")
        as_json = args.get("json", True)

        cmd = [mode, query]
        if collection:
            cmd += ["-c", collection]
        if limit:
            cmd += ["-n", str(limit)]
        if as_json:
            cmd += ["--json"]
        return _run_qmd(command, cmd, timeout)

    api.register_tool(
        "qmd_search",
        {
            "name": "qmd_search",
            "description": "Search local markdown collections using qmd.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "mode": {"type": "string", "enum": ["search", "vsearch", "query"]},
                    "collection": {"type": "string"},
                    "limit": {"type": "integer"},
                    "json": {"type": "boolean"},
                },
                "required": ["query"],
            },
            "handler": qmd_search,
        },
    )
