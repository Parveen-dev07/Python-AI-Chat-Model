# AI providers

Set the active provider with `AI_PROVIDER`:

| Value | Description |
|-------|-------------|
| `ollama` | Local Ollama (default for development) |
| `openai` | OpenAI Chat Completions API |

## Ollama

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

Ensure the model is pulled: `ollama pull llama3.2`

Check readiness: `GET /api/v1/health/ai`

## OpenAI

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4o-mini
```

If `OPENAI_API_KEY` is empty, the service fails at provider creation with a clear configuration error.

## Tool calling

Both implemented providers support the `run_readonly_sql` tool. If a future provider does not support tools, the chat service returns HTTP 503 rather than guessing answers.
