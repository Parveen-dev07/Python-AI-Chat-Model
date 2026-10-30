import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ command }) => ({
  plugins: [react()],
  ...(command === "build"
    ? {
        build: {
          lib: {
            entry: "src/embed.tsx",
            name: "AiChatWidget",
            fileName: () => "ai-chat-widget.js",
            formats: ["iife"],
          },
          rollupOptions: {
            output: {
              extend: true,
            },
          },
        },
        define: {
          "process.env.NODE_ENV": JSON.stringify("production"),
        },
      }
    : {}),
}));
