from __future__ import annotations

import json
import logging
import time
from typing import Any, AsyncIterator

import httpx

from app.core.config import Settings
from app.llm.base import LLMChunk, LLMResult

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider:
    """Proveedor para APIs compatibles con OpenAI.

    Sirve para Ollama / LM Studio / llama.cpp / MLX server si exponen /v1/chat/completions.
    """

    provider_name = "openai_compatible"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.base_url = settings.openai_base_url.rstrip("/")
        self.model_name = settings.openai_model
        self.headers = {"Authorization": f"Bearer {settings.openai_api_key}"}

    async def is_available(self) -> bool:
        # Algunos servidores compatibles no implementan /models. Probamos /models y si falla no bloqueamos.
        try:
            async with httpx.AsyncClient(timeout=2.5, headers=self.headers) as client:
                response = await client.get(f"{self.base_url}/models")
                return response.status_code < 500
        except Exception:
            return False

    async def chat(self, messages: list[dict[str, str]]) -> LLMResult:
        start = time.perf_counter()
        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "temperature": self.settings.llm_temperature,
            "max_tokens": self.settings.llm_max_tokens,
        }
        async with httpx.AsyncClient(timeout=self.settings.llm_timeout_s, headers=self.headers) as client:
            response = await client.post(f"{self.base_url}/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        if not content:
            raise RuntimeError("El proveedor compatible con OpenAI respondió sin contenido")
        total_ms = (time.perf_counter() - start) * 1000
        return LLMResult(content=content, provider=self.provider_name, model=self.model_name, total_ms=total_ms)

    async def chat_stream(self, messages: list[dict[str, str]]) -> AsyncIterator[LLMChunk]:
        start = time.perf_counter()
        first_token_ms: float | None = None
        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
            "temperature": self.settings.llm_temperature,
            "max_tokens": self.settings.llm_max_tokens,
        }
        async with httpx.AsyncClient(timeout=self.settings.llm_timeout_s, headers=self.headers) as client:
            async with client.stream("POST", f"{self.base_url}/chat/completions", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        line = line[6:]
                    if line.strip() == "[DONE]":
                        yield LLMChunk(
                            content="",
                            provider=self.provider_name,
                            model=self.model_name,
                            done=True,
                            first_token_ms=first_token_ms,
                            total_ms=(time.perf_counter() - start) * 1000,
                        )
                        return
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        logger.debug("Línea streaming OpenAI-compatible no JSON: %s", line)
                        continue
                    delta = data.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content and first_token_ms is None:
                        first_token_ms = (time.perf_counter() - start) * 1000
                    yield LLMChunk(
                        content=content,
                        provider=self.provider_name,
                        model=self.model_name,
                        first_token_ms=first_token_ms,
                    )
        yield LLMChunk(
            content="",
            provider=self.provider_name,
            model=self.model_name,
            done=True,
            first_token_ms=first_token_ms,
            total_ms=(time.perf_counter() - start) * 1000,
        )
