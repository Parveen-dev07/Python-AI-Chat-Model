import { createRoot } from "react-dom/client";
import { ChatWidget, WidgetConfig } from "./ChatWidget";

declare global {
  interface Window {
    AiChatWidget?: {
      init: (config: WidgetConfig) => void;
    };
    AiChatWidgetConfig?: WidgetConfig;
  }
}

function mount(config: WidgetConfig) {
  let container = document.getElementById("ai-chat-widget-root");
  if (!container) {
    container = document.createElement("div");
    container.id = "ai-chat-widget-root";
    document.body.appendChild(container);
  }
  createRoot(container).render(<ChatWidget config={config} />);
}

window.AiChatWidget = {
  init: mount,
};

if (window.AiChatWidgetConfig) {
  mount(window.AiChatWidgetConfig);
}
