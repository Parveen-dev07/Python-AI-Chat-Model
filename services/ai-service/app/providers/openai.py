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

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str, timeout: float = 120.0) -> None:
        self._api_key = api_key
        self._model = model
        self._timeout = timeout

    def supports_tool_calling(self) -> bool:
        return True

    async def check_ready(self) -> tuple[bool, str]:
        if not self._api_key.strip():
            return False, "OPENAI_API_KEY is not configured"
        return True, "OpenAI API key is configured"

    def _to_openai_messages(self, messages: list[ChatMessage]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for msg in messages:
            if msg.role == "tool" and msg.tool_call_id:
                out.append(
                    {
                        "role": "tool",
                        "tool_call_id": msg.tool_call_id,
                        "content": msg.content,
                    }
                )
            else:
                out.append({"role": msg.role, "content": msg.content})
        return out

    def _to_openai_tools(self, tools: list[ToolDefinition]) -> list[dict[str, Any]]:
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
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": self._to_openai_messages(messages),
        }
        if tools:
            payload["tools"] = self._to_openai_tools(tools)
            payload["tool_choice"] = "auto"

        timeout = httpx.Timeout(self._timeout, connect=10.0)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(OPENAI_CHAT_URL, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.TimeoutException as exc:
            from app.providers.errors import AIProviderTimeoutError

            raise AIProviderTimeoutError(
                "OpenAI did not respond in time; try a shorter question or increase "
                "AI_REQUEST_TIMEOUT_SECONDS"
            ) from exc
        except httpx.HTTPError as exc:
            from app.providers.errors import AIProviderError

            raise AIProviderError("OpenAI request failed") from exc

        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        content = message.get("content")

        tool_calls: list[ToolCall] = []
        for tc in message.get("tool_calls") or []:
            fn = tc.get("function") or {}
            raw_args = fn.get("arguments", "{}")
            try:
                arguments = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
            except json.JSONDecodeError:
                arguments = {}
            tool_calls.append(
                ToolCall(
                    id=tc.get("id", ""),
                    name=fn.get("name", ""),
                    arguments=arguments if isinstance(arguments, dict) else {},
                )
            )

        return ProviderResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=choice.get("finish_reason"),
        )
