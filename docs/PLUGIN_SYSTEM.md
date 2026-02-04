# Plugin System

This starter mirrors the OpenClaw plugin model with manifest-driven plugins, discovery rules, and runtime registration. Reference docs:

- https://docs.openclaw.ai/plugin
- https://docs.clawd.bot/plugins/manifest

## Manifest

Each plugin root must include `openclaw.plugin.json`:

```json
{
  "id": "sample-plugin",
  "name": "Sample Plugin",
  "version": "0.1.0",
  "entry": "plugin.py",
  "kind": "memory",
  "configSchema": {
    "type": "object",
    "properties": {
      "greeting": { "type": "string" }
    },
    "additionalProperties": false
  },
  "uiHints": {
    "greeting": { "label": "Greeting" }
  }
}
```

## Discovery Order

1. Paths in `plugins.load.paths` (from JSON config)
2. Local paths in `CONTROL_PLANE_PLUGIN_PATHS` (comma-separated; default `./plugins`)
3. Python entrypoints group `clasper.plugins`

First match for a plugin ID wins.

## Config

Use `CONTROL_PLANE_PLUGIN_CONFIG_PATH` to point at a JSON config:

```json
{
  "plugins": {
    "enabled": true,
    "allow": ["sample-plugin"],
    "deny": [],
    "entries": {
      "sample-plugin": { "enabled": true, "config": { "greeting": "hello" } }
    },
    "slots": {
      "memory": "sample-plugin"
    },
    "load": {
      "paths": ["./plugins/sample_plugin"]
    }
  }
}
```

## Runtime API

Plugins register hooks/tools/commands/services via the runtime API:

```python
def register(api):
    api.register_hook("before_task_create", hook)
    api.register_tool("echo", {"name": "echo", "parameters": {...}, "handler": handler})
    api.register_command("status", command_handler)
    api.register_service("worker", service_start)
```

## Hooks

Built-in hooks emitted by the starter:

- `before_task_create`
- `after_task_create`
- `before_message_post`
- `after_message_post`
- `before_document_post`
- `after_document_post`

If a hook raises `api.PluginBlocked`, the request is rejected with status 403.

