import jwt
from fastapi import Header, HTTPException
from typing import Optional, TypedDict

from .config import load_config


class Actor(TypedDict):
    user_id: str
    agent_role: str


def require_actor(x_agent_token: Optional[str] = Header(default=None)) -> Actor:
    if not x_agent_token:
        raise HTTPException(status_code=401, detail="Missing X-Agent-Token")

    cfg = load_config()
    if not cfg.agent_jwt_secret:
        raise HTTPException(status_code=500, detail="AGENT_JWT_SECRET is required")

    try:
        payload = jwt.decode(x_agent_token, cfg.agent_jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid agent token") from exc

    if payload.get("type") != "agent" or not payload.get("user_id") or not payload.get("agent_role"):
        raise HTTPException(status_code=401, detail="Invalid agent token")

    return {"user_id": payload["user_id"], "agent_role": payload["agent_role"]}
