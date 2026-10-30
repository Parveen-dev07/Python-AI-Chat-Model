# API reference

Base URL example: `http://localhost:8000`

## Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health |
| GET | `/health/database` | PostgreSQL connectivity |
| GET | `/api/v1/health/ai` | AI provider readiness |

## Chat

**POST** `/api/v1/chat`

Headers:

- `Content-Type: application/json`
- `X-API-Key: <server-configured key>`

Body:

```json
{
  "widget_id": "demo-widget",
  "message": "What is the price of Demo Burger?"
}
```

Response:

```json
{
  "answer": "...",
  "request_id": "uuid"
}
```

## Widget config

**GET** `/api/v1/widget/config?widget_id=demo-widget`

Headers: `X-API-Key`

Returns public UI settings only (title, theme). No database or provider secrets.
