import json
from typing import Any

import httpx

from app.core.logging import get_logger
from app.providers.base import (
    AIProvider,
    ChatMessage,
    ProviderResponse,
    ToolCall,
    ToolDefinition,
)

logger = get_logger(__name__)


class OllamaProvider(AIProvider):
    def __init__(self, base_url: str, model: str, timeout: float = 120.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout

    def supports_tool_calling(self) -> bool:
        return True

    async def check_ready(self) -> tuple[bool, str]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self._base_url}/api/tags")
                if resp.status_code != 200:
                    return False, f"Ollama returned status {resp.status_code}"
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                if models and not any(self._model.split(":")[0] in m for m in models):
                    return True, f"Ollama reachable; model '{self._model}' may need pulling"
                return True, "Ollama is reachable"
        except httpx.HTTPError as exc:
            return False, f"Cannot reach Ollama at {self._base_url}: {exc}"

    def _to_ollama_messages(self, messages: list[ChatMessage]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for msg in messages:
            entry: dict[str, Any] = {"role": msg.role, "content": msg.content}
            if msg.tool_call_id:
                entry["role"] = "tool"
                entry["content"] = msg.content
            out.append(entry)
        return out

    def _to_ollama_tools(self, tools: list[ToolDefinition]) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in tools
        ]

    async def chat(
        self,
        messages: list[ChatMessage],
        tools: list[ToolDefinition] | None = None,
    ) -> ProviderResponse:
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": self._to_ollama_messages(messages),
            "stream": False,
        }
        if tools:
            payload["tools"] = self._to_ollama_tools(tools)

        timeout = httpx.Timeout(self._timeout, connect=10.0)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(f"{self._base_url}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.TimeoutException as exc:
            from app.providers.errors import AIProviderTimeoutError

            raise AIProviderTimeoutError(
                "Ollama did not respond in time; try a shorter question or increase "
                "AI_REQUEST_TIMEOUT_SECONDS"
            ) from exc
        except httpx.HTTPError as exc:
            from app.providers.errors import AIProviderError

            raise AIProviderError("Ollama request failed") from exc

        message = data.get("message", {})
        content = message.get("content") or None
        tool_calls: list[ToolCall] = []
        for idx, tc in enumerate(message.get("tool_calls") or []):
            fn = tc.get("function") or {}
            raw_args = fn.get("arguments")
            if isinstance(raw_args, str):
                try:
                    arguments = json.loads(raw_args)
                except json.JSONDecodeError:
                    arguments = {}
            elif isinstance(raw_args, dict):
                arguments = raw_args
            else:
                arguments = {}
            tool_calls.append(
                ToolCall(
                    id=tc.get("id") or f"call_{idx}",
                    name=fn.get("name", ""),
                    arguments=arguments,
                )
            )

        return ProviderResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason="tool_calls" if tool_calls else "stop",
        )
