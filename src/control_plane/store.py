import hashlib
import json
import uuid
from typing import Any, Dict, List, Optional, Tuple


def hash_payload(payload: Any) -> str:
    raw = json.dumps(payload or {}, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class InMemoryStore:
    def __init__(self) -> None:
        self.tasks: List[Dict[str, Any]] = []
        self.messages: List[Dict[str, Any]] = []
        self.documents: List[Dict[str, Any]] = []
        self.idempotency: Dict[str, Dict[str, Tuple[str, Dict[str, Any]]]] = {
            "tasks": {},
            "messages": {},
            "documents": {},
        }

    def list_tasks(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        return [t for t in self.tasks if t["user_id"] == user_id][:limit]

    def create_task(self, user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        key = payload.get("idempotency_key")
        if key:
            record = self.idempotency["tasks"].get(key)
            req_hash = hash_payload(payload)
            if record:
                if record[0] != req_hash:
                    raise ValueError("idempotency_key conflict")
                return record[1]
        task = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": payload["title"],
            "status": payload.get("status", "in_progress"),
            "description": payload.get("description"),
            "metadata": payload.get("metadata"),
        }
        self.tasks.append(task)
        if key:
            self.idempotency["tasks"][key] = (hash_payload(payload), task)
        return task

    def create_message(self, user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        key = payload.get("idempotency_key")
        if key:
            record = self.idempotency["messages"].get(key)
            req_hash = hash_payload(payload)
            if record:
                if record[0] != req_hash:
                    raise ValueError("idempotency_key conflict")
                return record[1]
        message = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "task_id": payload["task_id"],
            "content": payload["content"],
            "actor_type": payload.get("actor_type"),
            "agent_role": payload.get("agent_role"),
            "attachments": payload.get("attachments"),
        }
        self.messages.append(message)
        if key:
            self.idempotency["messages"][key] = (hash_payload(payload), message)
        return message

    def create_document(self, user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        key = payload.get("idempotency_key")
        if key:
            record = self.idempotency["documents"].get(key)
            req_hash = hash_payload(payload)
            if record:
                if record[0] != req_hash:
                    raise ValueError("idempotency_key conflict")
                return record[1]
        document = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "task_id": payload["task_id"],
            "title": payload["title"],
            "content": payload["content"],
            "doc_type": payload.get("doc_type"),
        }
        self.documents.append(document)
        if key:
            self.idempotency["documents"][key] = (hash_payload(payload), document)
        return document
