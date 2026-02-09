 # Clasper Control Plane Starter (FastAPI + Plugins)
 
 Minimal Control Plane backend that implements the required Clasper contract endpoints and an OpenClaw-style plugin system.
 
## Quickstart

**This starter implements the Control Plane contract only.**  
**It is not a trust root and is not authoritative for governance.**  
**It cannot mint approval tokens.**  
**It cannot sign evidence or issue externally verifiable attestations (External Proof).**
 
 ```bash
 python -m venv .venv
 source .venv/bin/activate
 pip install -e ".[dev]"
 
 export AGENT_JWT_SECRET="your-secret"
 export CONTROL_PLANE_PORT=9001
 
 uvicorn control_plane.main:app --reload --port 9001
 ```
 
 Health check: `http://localhost:9001/health`
 
 ## Required Endpoints (v1 contract)
 
 - `GET /api/mission-control/capabilities`
 - `GET /api/mission-control/tasks`
 - `POST /api/mission-control/tasks`
 - `POST /api/mission-control/messages`
 - `POST /api/mission-control/documents`
 
 See the contract: `/Users/jasongelinas/workspace/clasper/docs/CONTROL_PLANE_CONTRACT.md`
 
 ## Authentication
 
 Requests must include `X-Agent-Token` JWT with:
 
 ```json
 { "type": "agent", "user_id": "user-123", "agent_role": "jarvis" }
 ```
 
 The token is verified with `AGENT_JWT_SECRET`.
 
 ## Idempotency
 
 Create endpoints accept `idempotency_key`. Reuse with a different payload returns `409`.
 
 ## Plugins (OpenClaw-style)
 
 This starter mirrors the OpenClaw plugin model:
 
 - **Manifest-driven** (`openclaw.plugin.json`)
 - **Discovery**: local `plugins/`, `CONTROL_PLANE_PLUGIN_PATHS`, and pip entrypoints
 - **Registry**: plugins can register hooks, tools, commands, and services
 - **Config**: allow/deny lists, per-plugin config, and optional slots
 
 References:
 - https://docs.openclaw.ai/plugin
 - https://docs.clawd.bot/plugins/manifest
 
 ### Plugin Config
 
 Use a JSON config file and point `CONTROL_PLANE_PLUGIN_CONFIG_PATH` to it:
 
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

Environment variables:
- `CONTROL_PLANE_PLUGIN_CONFIG_PATH` (JSON file with plugin settings)
- `CONTROL_PLANE_PLUGIN_PATHS` (comma-separated local plugin dirs; default `./plugins`)
 
 ### Sample Plugin
 
 See `plugins/sample_plugin/` for a minimal plugin with a manifest and a `register()` entrypoint.

### Sample Plugins

- **QMD plugin** (`plugins/qmd_plugin/`): registers a `qmd_search` tool and includes the `SKILL.md` from https://github.com/levineam/qmd-skill.
- **Prompt Guard** (`plugins/prompt_guard/`): pre‑request hook that blocks payloads matching denylist patterns.

Advanced reference (docs only):
- Graphiti hybrid memory: https://github.com/clawdbrunner/openclaw-graphiti-memory
 
 ## Conformance
 
 From the Clasper repo:
 
 ```bash
 export CONTROL_PLANE_URL=http://localhost:9001
 export AGENT_TOKEN="your-agent-jwt"
 export CONFORMANCE_REPORT_DIR=./conformance-results
 
 npm run conformance
 ```
 
 ## Tests
 
 ```bash
 pytest
 ```

## Documentation

- `docs/README.md`
- `docs/PLUGIN_SYSTEM.md`
- `docs/API.md`
- `CONTRIBUTING.md`
