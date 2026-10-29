import { createRoot } from "react-dom/client";
import { ChatWidget } from "./ChatWidget";

const root = document.getElementById("root");
if (root) {
  createRoot(root).render(
    <ChatWidget
      config={{
        widgetId: import.meta.env.VITE_WIDGET_ID ?? "demo-widget",
        apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
        apiKey: import.meta.env.VITE_API_KEY ?? "dev-api-key-change-me",
        title: "AI Chat (Dev)",
        theme: "light",
      }}
    />,
  );
}
