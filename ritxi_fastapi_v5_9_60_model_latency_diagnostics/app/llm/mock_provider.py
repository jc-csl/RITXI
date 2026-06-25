from __future__ import annotations

import asyncio
import time
from typing import AsyncIterator

from app.llm.base import LLMChunk, LLMResult


class MockLLMProvider:
    provider_name = "mock"
    model_name = "mock-ritxi-v5"

    async def is_available(self) -> bool:
        return True

    async def chat(self, messages: list[dict[str, str]]) -> LLMResult:
        start = time.perf_counter()
        await asyncio.sleep(0.05)
        content = self._response_for(messages)
        return LLMResult(
            content=content,
            provider=self.provider_name,
            model=self.model_name,
            warnings=["LLM en modo mock."],
            first_token_ms=50.0,
            total_ms=(time.perf_counter() - start) * 1000,
        )

    async def chat_stream(self, messages: list[dict[str, str]]) -> AsyncIterator[LLMChunk]:
        start = time.perf_counter()
        content = self._response_for(messages)
        first_token: float | None = None
        for word in content.split(" "):
            await asyncio.sleep(0.012)
            if first_token is None:
                first_token = (time.perf_counter() - start) * 1000
            yield LLMChunk(
                content=word + " ",
                provider=self.provider_name,
                model=self.model_name,
                first_token_ms=first_token,
                warnings=["LLM en modo mock."],
            )
        yield LLMChunk(
            content="",
            provider=self.provider_name,
            model=self.model_name,
            done=True,
            first_token_ms=first_token,
            total_ms=(time.perf_counter() - start) * 1000,
            warnings=["LLM en modo mock."],
        )

    def _response_for(self, messages: list[dict[str, str]]) -> str:
        last_user = ""
        for message in reversed(messages):
            if message.get("role") == "user":
                last_user = message.get("content", "")
                break

        lowered = last_user.lower()
        if any(word in lowered for word in ["hola", "buenas", "kaixo"]):
            return "[SALUDO] Hola, soy Ritxi. Me alegra verte. ¿Quieres practicar un saludo corto conmigo?"
        if any(word in lowered for word in ["ayuda", "no sé", "no se", "difícil", "dificil"]):
            return "[PACIENCIA] Claro, vamos poco a poco. Puedes empezar con una frase sencilla: necesito ayuda, por favor."
        if any(word in lowered for word in ["triste", "mal", "pena", "nervioso", "nerviosa"]):
            return "[CALMA] Te escucho con calma. Respira un momento y dime una palabra sobre cómo te sientes."
        if any(word in lowered for word in ["bien", "lo hice", "he podido", "genial"]):
            return "[CELEBRACION] ¡Muy bien! Has hecho un buen intento. Ahora vamos a probar una frase un poco más completa."
        if any(word in lowered for word in ["turno", "hablar", "interrumpir"]):
            return "[PEDIR_TURNO] Buena idea. Practicamos así: levanto la mano y digo, ¿puedo hablar ahora?"
        if any(word in lowered for word in ["repite", "otra vez", "no entiendo"]):
            return "[REPETIR] Sin problema. Lo digo más fácil: primero saludas, después dices lo que necesitas."
        if any(word in lowered for word in ["baila", "baile", "música", "musica"]):
            return "[BAILE] Vale, hago un movimiento alegre y seguimos con la actividad."
        if any(word in lowered for word in ["sí", "si", "vale", "correcto"]):
            return "[ASENTIR] De acuerdo. Seguimos despacio y con una sola pregunta."
        if any(word in lowered for word in ["no", "cancelar", "para", "stop"]):
            return "[NEGAR] Entendido. Paramos la actividad y esperamos."
        return "[ESCUCHA_ACTIVA] Te he escuchado. Dime una frase corta: ¿qué quieres practicar ahora?"
