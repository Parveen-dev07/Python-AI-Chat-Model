# Development

## Prerequisites

- Python 3.12+
- Node.js 20+ and pnpm 9+
- PostgreSQL (local or remote)
- Ollama (optional, for local AI)

## Backend

```bash
cd services/ai-service
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload --port 8000
pytest -v
ruff check .
```

## Frontend

From repository root (pnpm workspace):

```bash
pnpm install   # if esbuild scripts are blocked, run: pnpm approve-builds
pnpm widget:dev
pnpm demo:dev
```

Alternatively, build the widget with npm:

```bash
cd apps/widget && npm install && npm run build
```

## Switch AI provider

Change `AI_PROVIDER` in `.env` and restart Uvicorn. No code changes required.

## Manual integration test

1. Start PostgreSQL with sample data.
2. Start Ollama with a tool-capable model.
3. Start the API and widget dev server.
4. Ask a question that requires a SQL lookup.

If Ollama is unavailable, `/api/v1/health/ai` reports degraded status; chat may fail until the provider is reachable.
