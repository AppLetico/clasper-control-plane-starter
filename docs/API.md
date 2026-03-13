# Control Plane API (Minimal)

This starter implements the required Control Plane Contract v1 endpoints.

## Authentication

All endpoints require `X-Agent-Token` (JWT) with claims:

```json
{ "type": "agent", "user_id": "user-123", "agent_role": "jarvis" }
```

## Endpoints

### GET /api/mission-control/capabilities

Returns contract version and supported features.

### GET /api/mission-control/tasks

Query params:
- `limit` (default 50, max 100)

Response:

```json
{ "items": [ { "id": "...", "title": "...", "status": "in_progress" } ] }
```

### POST /api/mission-control/tasks

Body:

```json
{
  "title": "Task title",
  "status": "in_progress",
  "description": "optional",
  "metadata": {},
  "idempotency_key": "optional"
}
```

### POST /api/mission-control/messages

Body:

```json
{
  "task_id": "task-uuid",
  "content": "message text",
  "actor_type": "agent",
  "agent_role": "jarvis",
  "attachments": {},
  "idempotency_key": "optional"
}
```

### POST /api/mission-control/documents

Body:

```json
{
  "task_id": "task-uuid",
  "title": "Document title",
  "content": "Document body",
  "doc_type": "note",
  "idempotency_key": "optional"
}
```

