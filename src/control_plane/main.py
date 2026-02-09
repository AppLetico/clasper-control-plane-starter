from contextlib import asynccontextmanager
import logging
import sys

from fastapi import Depends, FastAPI, HTTPException
from loguru import logger
from typing import Dict, Any

from .auth import require_actor
from .config import load_config
from .models import TaskIn, TaskOut, MessageIn, MessageOut, DocumentIn, DocumentOut
from .store import InMemoryStore
from .plugins.loader import load_plugins
from .plugins.runtime import PluginBlocked

# ---------------------------------------------------------------------------
# Loguru — intercept all stdlib logging (uvicorn, etc.) into loguru
# ---------------------------------------------------------------------------

class _InterceptHandler(logging.Handler):
    """Route stdlib log records into loguru."""
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[_InterceptHandler()], level=logging.INFO, force=True)
for _name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
    logging.getLogger(_name).handlers = [_InterceptHandler()]

# ---------------------------------------------------------------------------
# Startup banner
# ---------------------------------------------------------------------------
STARTUP_BANNER = r"""
   ____ _                              ____            _             _   ____  _
  / ___| | __ _ ___ _ __   ___ _ __  / ___|___  _ __ | |_ _ __ ___ | | |  _ \| | __ _ _ __   ___
 | |   | |/ _` / __| '_ \ / _ \ '__|| |   / _ \| '_ \| __| '__/ _ \| | | |_) | |/ _` | '_ \ / _ \
 | |___| | (_| \__ \ |_) |  __/ |   | |__| (_) | | | | |_| | | (_) | | |  __/| | (_| | | | |  __/
  \____|_|\__,_|___/ .__/ \___|_|    \____\___/|_| |_|\__|_|  \___/|_| |_|   |_|\__,_|_| |_|\___|
                   |_|
  🎛️  Mission Control API
  ───────────────────────────────────────────────────────────────────────────────
"""

_is_tty = sys.stdout.isatty()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if _is_tty:
        base = f"http://127.0.0.1:{cfg.port}"
        print("\033[36m" + STARTUP_BANNER + "\033[0m", end="")
        print(f"  \033[1m▶\033[0m  API: \033[4m{base}\033[0m")
        print(f"  \033[1m▶\033[0m  Health: \033[4m{base}/health\033[0m\n")
    logger.info("Control plane ready — {} plugin(s) loaded", len(registry.hooks))
    yield
    logger.info("Shutting down")


app = FastAPI(lifespan=lifespan)
store = InMemoryStore()
cfg = load_config()
registry = load_plugins(cfg)


def _run_hooks(name: str, payload: Dict[str, Any]) -> None:
    for hook in registry.hooks.get(name, []):
        try:
            hook(payload)
        except PluginBlocked as exc:
            raise HTTPException(status_code=exc.status_code, detail=str(exc))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/mission-control/capabilities")
def capabilities(actor=Depends(require_actor)):
    return {
        "contract_version": "v1",
        "features": {
            "tasks": True,
            "messages": True,
            "documents": True,
            "notifications_dispatch": False,
            "events_sse": False,
            "heartbeat": False,
            "standup": False,
            "tool_requests": False,
        },
    }


@app.get("/api/mission-control/tasks", response_model=Dict[str, Any])
def list_tasks(limit: int = 50, actor=Depends(require_actor)):
    items = store.list_tasks(actor["user_id"], min(max(limit, 1), 100))
    return {"items": items}


@app.post("/api/mission-control/tasks", response_model=TaskOut)
def create_task(payload: TaskIn, actor=Depends(require_actor)):
    _run_hooks("before_task_create", {"user_id": actor["user_id"], "payload": payload.model_dump()})
    try:
        task = store.create_task(actor["user_id"], payload.model_dump())
    except ValueError:
        raise HTTPException(status_code=409, detail="idempotency_key conflict")
    _run_hooks("after_task_create", {"user_id": actor["user_id"], "task": task})
    return task


@app.post("/api/mission-control/messages", response_model=MessageOut)
def post_message(payload: MessageIn, actor=Depends(require_actor)):
    _run_hooks("before_message_post", {"user_id": actor["user_id"], "payload": payload.model_dump()})
    try:
        message = store.create_message(actor["user_id"], payload.model_dump())
    except ValueError:
        raise HTTPException(status_code=409, detail="idempotency_key conflict")
    _run_hooks("after_message_post", {"user_id": actor["user_id"], "message": message})
    return message


@app.post("/api/mission-control/documents", response_model=DocumentOut)
def post_document(payload: DocumentIn, actor=Depends(require_actor)):
    _run_hooks("before_document_post", {"user_id": actor["user_id"], "payload": payload.model_dump()})
    try:
        document = store.create_document(actor["user_id"], payload.model_dump())
    except ValueError:
        raise HTTPException(status_code=409, detail="idempotency_key conflict")
    _run_hooks("after_document_post", {"user_id": actor["user_id"], "document": document})
    return document


@app.get("/api/tools")
def list_tools(actor=Depends(require_actor)):
    tools = list(registry.tools.values())
    return {"tools": tools}


@app.post("/api/tools/{name}")
def execute_tool(name: str, payload: Dict[str, Any], actor=Depends(require_actor)):
    if name == "echo":
        args = payload.get("arguments") or {}
        return {"message": args.get("message")}

    raise HTTPException(status_code=404, detail="tool not found")
