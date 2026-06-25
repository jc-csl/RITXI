from __future__ import annotations

import asyncio

from app.core.config import Settings
from app.llm.base import LLMProvider, LLMResult
from app.llm.mock_provider import MockLLMProvider
from app.services.character import CharacterManager


class ConversationMemory:
    def __init__(self, settings: Settings, llm_provider: LLMProvider, character_manager: CharacterManager):
        self.settings = settings
        self.llm_provider = llm_provider
        self.character_manager = character_manager
        self._histories: dict[str, list[dict[str, str]]] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def messages_for(self, session_id: str, user_text: str) -> list[dict[str, str]]:
        session_id = session_id.strip() or self.settings.default_session_id
        history = self._histories.setdefault(session_id, [])
        system_prompt = self.character_manager.build_system_prompt()
        return [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_text}]

    def commit(self, session_id: str, user_text: str, assistant_text: str) -> None:
        session_id = session_id.strip() or self.settings.default_session_id
        history = self._histories.setdefault(session_id, [])
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": assistant_text})
        max_items = self.settings.max_history_messages
        if max_items > 0 and len(history) > max_items:
            self._histories[session_id] = history[-max_items:]

    def lock_for(self, session_id: str) -> asyncio.Lock:
        if session_id not in self._locks:
            self._locks[session_id] = asyncio.Lock()
        return self._locks[session_id]

    def reset(self, session_id: str) -> None:
        self._histories.pop(session_id, None)


def fallback_result(exc: Exception, messages: list[dict[str, str]]) -> LLMResult:
    mock = MockLLMProvider()
    last_user = ""
    for message in reversed(messages):
        if message.get("role") == "user":
            last_user = message.get("content", "")
            break
    content = mock._response_for([{"role": "user", "content": last_user}])  # noqa: SLF001
    return LLMResult(content=content, provider="mock", model="mock-ritxi-v5", warnings=[f"Fallo LLM real; fallback mock. Detalle: {exc}"])
