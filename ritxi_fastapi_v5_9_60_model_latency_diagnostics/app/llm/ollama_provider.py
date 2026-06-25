"""
v5.9.42 · Comentarios de arquitectura

Proveedor LLM para Ollama.

Responsabilidades:
- construir la petición a Ollama;
- enviar prompt de sistema, historial y mensaje de usuario;
- aplicar límites de tokens/contexto para respuestas rápidas;
- devolver texto generado al Runtime/FastAPI.

Modelos previstos:
- qwen3:0.6b      -> rápido;
- gemma3:1b      -> equilibrado recomendado;
- llama3.2:1b    -> llama rápido;
- llama3.2:3b    -> mayor calidad.
"""

from __future__ import annotations

import json
import os
import logging
import time
from typing import Any, AsyncIterator

import httpx

from app.core.config import Settings
from app.core.logging import log_event
from app.llm.base import LLMChunk, LLMResult

logger = logging.getLogger(__name__)


class OllamaProvider:
    provider_name = "ollama"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.base_url = settings.ollama_url.rstrip("/")
        self.model_name = settings.ollama_model

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def chat(self, messages: list[dict[str, str]]) -> LLMResult:
        start = time.perf_counter()
        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.settings.llm_temperature,
                "num_predict": int(os.getenv("RITXI_LLM_MAX_TOKENS", str(self.settings.llm_max_tokens))),
                "num_ctx": int(os.getenv("RITXI_OLLAMA_NUM_CTX", "768")),
                "top_k": int(os.getenv("RITXI_OLLAMA_TOP_K", "20")),
                "top_p": float(os.getenv("RITXI_OLLAMA_TOP_P", "0.85")),
                "repeat_penalty": float(os.getenv("RITXI_OLLAMA_REPEAT_PENALTY", "1.15")),
            },
        }
        log_event("ollama_request", model=self.model_name, stream=False, url=f"{self.base_url}/api/chat", messages=len(messages))
        async with httpx.AsyncClient(timeout=self.settings.llm_timeout_s) as client:
            response = await client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
        content = data.get("message", {}).get("content", "").strip()
        if not content:
            raise RuntimeError("Ollama respondió sin contenido en message.content")
        total_ms = (time.perf_counter() - start) * 1000
        log_event("ollama_response", model=self.model_name, stream=False, total_ms=round(total_ms, 2), content_len=len(content))
        return LLMResult(content=content, provider=self.provider_name, model=self.model_name, total_ms=total_ms)

    async def chat_stream(self, messages: list[dict[str, str]]) -> AsyncIterator[LLMChunk]:
        start = time.perf_counter()
        first_token_ms: float | None = None
        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": self.settings.llm_temperature,
                "num_predict": int(os.getenv("RITXI_LLM_MAX_TOKENS", str(self.settings.llm_max_tokens))),
                "num_ctx": int(os.getenv("RITXI_OLLAMA_NUM_CTX", "768")),
                "top_k": int(os.getenv("RITXI_OLLAMA_TOP_K", "20")),
                "top_p": float(os.getenv("RITXI_OLLAMA_TOP_P", "0.85")),
                "repeat_penalty": float(os.getenv("RITXI_OLLAMA_REPEAT_PENALTY", "1.15")),
            },
        }
        log_event("ollama_request", model=self.model_name, stream=True, url=f"{self.base_url}/api/chat", messages=len(messages))
        async with httpx.AsyncClient(timeout=self.settings.llm_timeout_s) as client:
            async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        logger.debug("Línea streaming Ollama no JSON: %s", line)
                        continue
                    content = data.get("message", {}).get("content", "")
                    if content and first_token_ms is None:
                        first_token_ms = (time.perf_counter() - start) * 1000
                        log_event("ollama_first_token", model=self.model_name, first_token_ms=round(first_token_ms, 2))
                    done = bool(data.get("done", False))
                    total_ms = (time.perf_counter() - start) * 1000 if done else 0.0
                    if done:
                        log_event("ollama_response", model=self.model_name, stream=True, total_ms=round(total_ms, 2), first_token_ms=first_token_ms)
                    yield LLMChunk(
                        content=content,
                        provider=self.provider_name,
                        model=self.model_name,
                        done=done,
                        first_token_ms=first_token_ms,
                        total_ms=total_ms,
                    )
                    if done:
                        return
        total_ms = (time.perf_counter() - start) * 1000
        log_event("ollama_response", model=self.model_name, stream=True, total_ms=round(total_ms, 2), first_token_ms=first_token_ms)
        yield LLMChunk(
            content="",
            provider=self.provider_name,
            model=self.model_name,
            done=True,
            first_token_ms=first_token_ms,
            total_ms=total_ms,
        )
