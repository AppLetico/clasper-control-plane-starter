# Contributing

Thanks for helping improve the Control Plane starter.

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Tests

```bash
pytest
```

## Code Style

- Keep modules small and focused.
- Prefer pure functions for plugin utilities.
- Avoid introducing heavy dependencies in the starter.

## Adding Plugins

1. Add a new plugin folder under `plugins/`.
2. Include `openclaw.plugin.json` and a `plugin.py` entrypoint.
3. Add a README note or doc entry in `docs/PLUGIN_SYSTEM.md` if needed.

## Reporting Issues

Please include:
- OS and Python version
- Steps to reproduce
- Logs or traceback

