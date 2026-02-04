import os
import sys
import jwt
from fastapi.testclient import TestClient

sys.path.append("src")
os.environ["AGENT_JWT_SECRET"] = "test-secret"

from control_plane.main import app  # noqa: E402


def _token():
    payload = {"type": "agent", "user_id": "user-1", "agent_role": "jarvis"}
    return jwt.encode(payload, "test-secret", algorithm="HS256")


def test_capabilities():
    client = TestClient(app)
    response = client.get(
        "/api/mission-control/capabilities",
        headers={"X-Agent-Token": _token()},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["contract_version"] == "v1"
    assert body["features"]["tasks"] is True


def test_task_lifecycle():
    client = TestClient(app)
    headers = {"X-Agent-Token": _token()}

    create = client.post(
        "/api/mission-control/tasks",
        headers=headers,
        json={"title": "Test Task", "status": "in_progress"},
    )
    assert create.status_code == 200
    task_id = create.json()["id"]

    listing = client.get("/api/mission-control/tasks", headers=headers)
    assert listing.status_code == 200
    assert any(item["id"] == task_id for item in listing.json()["items"])

    message = client.post(
        "/api/mission-control/messages",
        headers=headers,
        json={"task_id": task_id, "content": "Hello"},
    )
    assert message.status_code == 200

    document = client.post(
        "/api/mission-control/documents",
        headers=headers,
        json={"task_id": task_id, "title": "Doc", "content": "Body"},
    )
    assert document.status_code == 200
