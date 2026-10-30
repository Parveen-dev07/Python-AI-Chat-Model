# What to do next

## 1. Daily development (two terminals)

**Backend**

```bash
cd services/ai-service
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Widget**

```bash
cd ../..   # repo root
npm run dev
```

Open http://localhost:5173 and ask natural-language questions (no table names required).

## 2. Verify stack

```bash
curl -s http://localhost:8000/health/database
curl -s http://localhost:8000/api/v1/health/ai
```

Set `AI_PROVIDER` and the matching API key in `.env`; model name must match your provider (e.g. `GEMINI_MODEL`).

## 3. Try good test questions

- How many rows are in community_posts?
- Show name and role from profiles limit 5
- What are the titles of the latest community posts?

Schema metadata (including PostgreSQL enum values) is sent to the model automatically.

## 4. Harden for real use

- [ ] Create a **read-only** PostgreSQL user (not `postgres` superuser)
- [ ] Rotate `API_KEY`; use a **backend proxy** instead of exposing the key in the widget
- [ ] Restrict `DB_ALLOWED_SCHEMAS` to only what the chat may read
- [ ] Add git remote and CI (`.github/workflows/ci.yml` is ready)

## 5. Optional product work

- Multi-tenant config in a platform database (instead of single `.env` tenant)
- Node adapter in `apps/api` to proxy chat from customer sites
- Deploy API (Docker/VPS) and host `apps/widget/dist/ai-chat-widget.js` on a CDN

See [security.md](security.md) before public deployment.
