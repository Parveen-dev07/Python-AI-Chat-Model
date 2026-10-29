# Widget integration

## Build

```bash
cd apps/widget
npm install
npm run build
```

Host `apps/widget/dist/ai-chat-widget.js` on your CDN or static file server.

## Accessibility Platform admin (automatic, no manual `cp`)

The admin app at `accessibility-app/apps/admin` includes a Vite plugin that:

- Builds the widget from `../AI-Chat-Model/apps/widget` if `dist/` is missing
- Serves `/ai-chat-widget.js` and `/ai-chat-widget.css` during `npm run dev`
- Copies those files into `public/` on `npm run build` for production

Keep only these lines in `index.html`:

```html
<link rel="stylesheet" href="/ai-chat-widget.css" />
<script>
  window.AiChatWidgetConfig = { widgetId, apiBaseUrl, apiKey, title, theme };
</script>
<script src="/ai-chat-widget.js"></script>
```

Override widget location with env: `AI_CHAT_WIDGET_ROOT=/path/to/AI-Chat-Model/apps/widget`

Ensure `CORS_ORIGINS` on the AI service includes `http://localhost:3000`.

## Embed snippet

```html
<script>
  window.AiChatWidgetConfig = {
    widgetId: "demo-widget",
    apiBaseUrl: "https://your-api.example.com",
    apiKey: "YOUR_SERVER_ISSUED_KEY",
    title: "Ask us anything",
    theme: "light",
  };
</script>
<script src="https://your-cdn.example.com/ai-chat-widget.js"></script>
```

Or call explicitly after load:

```html
<script src=".../ai-chat-widget.js"></script>
<script>
  window.AiChatWidget.init({ ... });
</script>
```

## CORS

Configure `CORS_ORIGINS` on the API to include your site origin. CORS restricts browser origins only; it is **not** authentication. Always use `X-API-Key` (or a backend proxy) for authorization.

## Production recommendation

Avoid embedding long-lived API keys in public JavaScript. Prefer:

1. Your website backend holds the API key.
2. The widget calls your backend; your backend forwards to `ai-service`.

The optional `apps/api` Node adapter can be added for this pattern.
