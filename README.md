# Reusable AI Chat Platform

Monorepo for a database-backed AI chat service and embeddable widget.

## Components

| Path | Description |
|------|-------------|
| `services/ai-service` | Python FastAPI backend (AI providers, SQL tools, tenants) |
| `apps/widget` | React + TypeScript embeddable chat widget |
| `apps/demo-website` | Sample site showing widget integration |
| `docs/` | Architecture, API, security, and setup guides |

## Quick start (backend)

```bash
cd services/ai-service
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Edit CUSTOMER_DATABASE_URL, API_KEY, AI provider settings
uvicorn app.main:app --reload --port 8000
```

Health checks:

- `GET http://localhost:8000/health`
- `GET http://localhost:8000/health/database`
- `GET http://localhost:8000/api/v1/health/ai`

Chat (requires `X-API-Key` header):

```bash
curl -s -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-change-me" \
  -d '{"widget_id":"demo-widget","message":"What is the price of Demo Burger?"}'
```

## Quick start (widget)

```bash
pnpm install
pnpm widget:dev
```

Build embeddable bundle:

```bash
pnpm widget:build
# Output: apps/widget/dist/ai-chat-widget.js
```

Demo site:

```bash
pnpm demo:dev
```

## Tests

```bash
cd services/ai-service && pytest -v && ruff check .
```

## Documentation

See [docs/architecture.md](docs/architecture.md) and the other files in `docs/`.

## Status

This is a development prototype. Review [docs/security.md](docs/security.md) before any public deployment.
