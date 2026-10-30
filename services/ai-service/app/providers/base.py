from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChatMessage:
    role: str
    content: str
    tool_call_id: str | None = None
    name: str | None = None


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ProviderResponse:
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str | None = None


class AIProvider(ABC):
    @abstractmethod
    async def check_ready(self) -> tuple[bool, str]:
        """Return (ready, message)."""

    @abstractmethod
    def supports_tool_calling(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def chat(
        self,
        messages: list[ChatMessage],
        tools: list[ToolDefinition] | None = None,
    ) -> ProviderResponse:
        raise NotImplementedError
