from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class TaskIn(BaseModel):
    title: str
    status: str = "in_progress"
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    idempotency_key: Optional[str] = None


class TaskOut(BaseModel):
    id: str
    user_id: str
    title: str
    status: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MessageIn(BaseModel):
    task_id: str
    content: str
    actor_type: Optional[str] = None
    agent_role: Optional[str] = None
    attachments: Optional[Dict[str, Any]] = None
    idempotency_key: Optional[str] = None


class MessageOut(BaseModel):
    id: str
    user_id: str
    task_id: str
    content: str
    actor_type: Optional[str] = None
    agent_role: Optional[str] = None
    attachments: Optional[Dict[str, Any]] = None


class DocumentIn(BaseModel):
    task_id: str
    title: str
    content: str
    doc_type: Optional[str] = Field(default="note")
    idempotency_key: Optional[str] = None


class DocumentOut(BaseModel):
    id: str
    user_id: str
    task_id: str
    title: str
    content: str
    doc_type: Optional[str] = None
