import { FormEvent, useEffect, useRef, useState } from "react";
import "./styles.css";

export type WidgetConfig = {
  widgetId: string;
  apiBaseUrl: string;
  apiKey: string;
  title?: string;
  theme?: "light" | "dark";
};

type Message = {
  id: string;
  role: "user" | "assistant" | "error";
  text: string;
};

async function fetchWidgetTitle(config: WidgetConfig): Promise<string> {
  const url = new URL("/api/v1/widget/config", config.apiBaseUrl);
  url.searchParams.set("widget_id", config.widgetId);
  const resp = await fetch(url.toString(), {
    headers: { "X-API-Key": config.apiKey },
  });
  if (!resp.ok) {
    return config.title ?? "Chat";
  }
  const data = (await resp.json()) as { title?: string; theme?: string };
  return data.title ?? config.title ?? "Chat";
}

export function ChatWidget({ config }: { config: WidgetConfig }) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState(config.title ?? "Chat");
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const listRef = useRef<HTMLDivElement>(null);
  const theme = config.theme ?? "light";

  useEffect(() => {
    if (open) {
      void fetchWidgetTitle(config).then(setTitle).catch(() => undefined);
    }
  }, [open, config]);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight });
  }, [messages, loading]);

  async function sendMessage(event: FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      text,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const resp = await fetch(new URL("/api/v1/chat", config.apiBaseUrl), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": config.apiKey,
        },
        body: JSON.stringify({ widget_id: config.widgetId, message: text }),
      });
      if (!resp.ok) {
        const errText =
          resp.status === 401
            ? "Unauthorized. Check API key configuration."
            : "Something went wrong. Please try again.";
        setMessages((prev) => [
          ...prev,
          { id: crypto.randomUUID(), role: "error", text: errText },
        ]);
        return;
      }
      const data = (await resp.json()) as { answer: string };
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", text: data.answer },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "error",
          text: "Network error. Is the API running?",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={`ai-chat-root theme-${theme}`}>
      {!open && (
        <button
          type="button"
          className="ai-chat-launcher"
          aria-label="Open chat"
          onClick={() => setOpen(true)}
        >
          💬
        </button>
      )}
      {open && (
        <section className="ai-chat-panel" aria-label="Chat panel">
          <header className="ai-chat-header">
            <span>{title}</span>
            <button
              type="button"
              className="ai-chat-close"
              aria-label="Close chat"
              onClick={() => setOpen(false)}
            >
              ×
            </button>
          </header>
          <div className="ai-chat-messages" ref={listRef} role="log" aria-live="polite">
            {messages.length === 0 && (
              <div className="ai-chat-bubble assistant">
                Ask a question about data in the connected database.
              </div>
            )}
            {messages.map((m) => (
              <div key={m.id} className={`ai-chat-bubble ${m.role}`}>
                {m.text}
              </div>
            ))}
            {loading && <div className="ai-chat-status">Thinking…</div>}
          </div>
          <form className="ai-chat-input-row" onSubmit={sendMessage}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your question"
              aria-label="Message"
              disabled={loading}
            />
            <button type="submit" disabled={loading || !input.trim()}>
              Send
            </button>
          </form>
        </section>
      )}
    </div>
  );
}
