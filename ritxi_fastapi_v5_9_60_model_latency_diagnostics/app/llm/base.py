from __future__ import annotations

from dataclasses import dataclass, field
from typing import AsyncIterator, Protocol


@dataclass(frozen=True)
class LLMResult:
    content: str
    provider: str
    model: str
    warnings: list[str] = field(default_factory=list)
    first_token_ms: float | None = None
    total_ms: float = 0.0
    streaming_used: bool = False


@dataclass(frozen=True)
class LLMChunk:
    content: str
    provider: str
    model: str
    done: bool = False
    first_token_ms: float | None = None
    total_ms: float = 0.0
    warnings: list[str] = field(default_factory=list)


class LLMProvider(Protocol):
    provider_name: str
    model_name: str

    async def is_available(self) -> bool: ...

    async def chat(self, messages: list[dict[str, str]]) -> LLMResult: ...

    async def chat_stream(self, messages: list[dict[str, str]]) -> AsyncIterator[LLMChunk]: ...
