# AI providers

Set the active provider with `AI_PROVIDER`:

| Value | Description |
|-------|-------------|
| `openai` | OpenAI Chat Completions API |
| `gemini` | Google Gemini (AI Studio API key) |

## OpenAI

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4o-mini
```

If `OPENAI_API_KEY` is empty, the service fails at provider creation with a clear configuration error.

## Gemini

Create an API key in [Google AI Studio](https://aistudio.google.com/apikey).

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini-3.5-flash
```

If `GEMINI_API_KEY` is empty, the service fails at provider creation with a clear configuration error.

Check readiness: `GET /api/v1/health/ai`

## Tool calling

All implemented providers support the `run_readonly_sql` tool. If a future provider does not support tools, the chat service returns HTTP 503 rather than guessing answers.
