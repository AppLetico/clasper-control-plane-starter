from fastapi import Depends, FastAPI, HTTPException
from typing import Dict, Any

from .auth import require_actor
from .config import load_config
from .models import TaskIn, TaskOut, MessageIn, MessageOut, DocumentIn, DocumentOut
from .store import InMemoryStore
from .plugins.loader import load_plugins
from .plugins.runtime import PluginBlocked

app = FastAPI()
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
