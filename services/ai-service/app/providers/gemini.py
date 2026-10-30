import json
import uuid
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

DEFAULT_GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


class GeminiProvider(AIProvider):
    def __init__(
        self,
        api_key: str,
        model: str,
        api_base: str = DEFAULT_GEMINI_API_BASE,
        timeout: float = 120.0,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._api_base = api_base.rstrip("/")
        self._timeout = timeout

    def supports_tool_calling(self) -> bool:
        return True

    async def check_ready(self) -> tuple[bool, str]:
        if not self._api_key.strip():
            return False, "GEMINI_API_KEY is not configured"
        url = f"{self._api_base}/models/{self._model}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params={"key": self._api_key})
                if resp.status_code == 200:
                    return True, f"Gemini model '{self._model}' is available"
                if resp.status_code in (401, 403):
                    return False, "Gemini API rejected the key (check GEMINI_API_KEY)"
                if resp.status_code == 404:
                    return False, f"Unknown Gemini model '{self._model}'"
                return False, f"Gemini API returned status {resp.status_code}"
        except httpx.HTTPError as exc:
            return False, f"Cannot reach Gemini API: {exc}"

    def _split_system_instruction(
        self, messages: list[ChatMessage]
    ) -> tuple[str | None, list[ChatMessage]]:
        system_parts: list[str] = []
        rest: list[ChatMessage] = []
        for msg in messages:
            if msg.role == "system":
                system_parts.append(msg.content)
            else:
                rest.append(msg)
        if not system_parts:
            return None, rest
        return "\n\n".join(system_parts), rest

    def _to_gemini_contents(self, messages: list[ChatMessage]) -> list[dict[str, Any]]:
        contents: list[dict[str, Any]] = []
        for msg in messages:
            if msg.role == "user":
                contents.append({"role": "user", "parts": [{"text": msg.content}]})
            elif msg.role == "assistant":
                parts: list[dict[str, Any]] = []
                if msg.content.strip():
                    parts.append({"text": msg.content})
                if parts:
                    contents.append({"role": "model", "parts": parts})
            elif msg.role == "tool":
                fn_name = msg.name or "run_readonly_sql"
                try:
                    response_body: dict[str, Any] = json.loads(msg.content)
                except json.JSONDecodeError:
                    response_body = {"result": msg.content}
                contents.append(
                    {
                        "role": "user",
                        "parts": [
                            {
                                "functionResponse": {
                                    "name": fn_name,
                                    "response": response_body,
                                }
                            }
                        ],
                    }
                )
        return contents

    def _to_gemini_tools(self, tools: list[ToolDefinition]) -> list[dict[str, Any]]:
        return [
            {
                "functionDeclarations": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters,
                    }
                    for t in tools
                ]
            }
        ]

    async def chat(
        self,
        messages: list[ChatMessage],
        tools: list[ToolDefinition] | None = None,
    ) -> ProviderResponse:
        system_instruction, convo = self._split_system_instruction(messages)
        payload: dict[str, Any] = {
            "contents": self._to_gemini_contents(convo),
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        if tools:
            payload["tools"] = self._to_gemini_tools(tools)

        url = f"{self._api_base}/models/{self._model}:generateContent"
        timeout = httpx.Timeout(self._timeout, connect=10.0)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, params={"key": self._api_key}, json=payload)
                if resp.status_code >= 400:
                    from app.providers.errors import AIProviderError

                    detail = resp.text[:500]
                    try:
                        api_message = resp.json().get("error", {}).get("message")
                        if api_message:
                            detail = str(api_message)
                    except (json.JSONDecodeError, AttributeError, TypeError):
                        pass
                    raise AIProviderError(
                        f"Gemini API error ({resp.status_code}): {detail}"
                    )
                data = resp.json()
        except httpx.TimeoutException as exc:
            from app.providers.errors import AIProviderTimeoutError

            raise AIProviderTimeoutError(
                "Gemini did not respond in time; try a shorter question or increase "
                "AI_REQUEST_TIMEOUT_SECONDS"
            ) from exc
        except httpx.HTTPError as exc:
            from app.providers.errors import AIProviderError

            raise AIProviderError("Gemini request failed") from exc

        candidate = (data.get("candidates") or [{}])[0]
        content_obj = candidate.get("content") or {}
        parts = content_obj.get("parts") or []

        text_parts: list[str] = []
        tool_calls: list[ToolCall] = []
        for part in parts:
            if "text" in part and part["text"]:
                text_parts.append(part["text"])
            fn_call = part.get("functionCall")
            if fn_call:
                args = fn_call.get("args") or {}
                tool_calls.append(
                    ToolCall(
                        id=str(uuid.uuid4()),
                        name=str(fn_call.get("name", "")),
                        arguments=args if isinstance(args, dict) else {},
                    )
                )

        finish_reason = candidate.get("finishReason")
        combined = "\n".join(text_parts).strip() if text_parts else None
        return ProviderResponse(
            content=combined,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
        )
