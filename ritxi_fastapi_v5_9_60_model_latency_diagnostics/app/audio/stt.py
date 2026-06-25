from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import Settings
from app.models.schemas import STTStatus, TranscribeResponse


@dataclass
class PersistentSTTService:
    """STT persistente.

    En modo browser/mock devuelve el texto que llega desde la UI.
    En modo http espera un servidor local mantenido caliente, por ejemplo Whisper/Faster-Whisper.
    """

    settings: Settings

    def __post_init__(self) -> None:
        self.provider = self.settings.stt_provider
        self.warm = False
        self.available = self.provider in {"mock", "browser", "local_whisper"}
        self.last_latency_ms = 0.0

    async def start(self) -> None:
        if self.provider in {"mock", "browser", "local_whisper"}:
            self.warm = True
            self.available = True
            return
        self.available = await self._ping()
        self.warm = self.available

    async def stop(self) -> None:
        self.warm = False

    async def is_available(self) -> bool:
        if self.provider in {"mock", "browser", "local_whisper"}:
            return True
        self.available = await self._ping()
        return self.available

    async def transcribe_text(self, text: str) -> TranscribeResponse:
        start = time.perf_counter()
        # Este endpoint sirve para probar el ciclo completo aunque todavía no mandemos audio binario.
        if self.provider in {"mock", "browser", "local_whisper"}:
            await self._keep_warm_tick()
            latency = (time.perf_counter() - start) * 1000
            self.last_latency_ms = latency
            return TranscribeResponse(text=text, provider=self.provider, warm=self.warm, latency_ms=latency)

        # Contrato simple para un stt_server propio: POST /transcribe_text {"text":"..."}
        payload: dict[str, Any] = {"text": text}
        async with httpx.AsyncClient(timeout=self.settings.stt_timeout_s) as client:
            response = await client.post(f"{self.settings.stt_server_url.rstrip('/')}/transcribe_text", json=payload)
            response.raise_for_status()
            data = response.json()
        latency = (time.perf_counter() - start) * 1000
        self.last_latency_ms = latency
        return TranscribeResponse(
            text=str(data.get("text", text)),
            provider="http",
            warm=True,
            latency_ms=latency,
            metadata={"server": self.settings.stt_server_url},
        )

    async def _ping(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{self.settings.stt_server_url.rstrip('/')}/health")
                return response.status_code == 200
        except Exception:
            return False

    async def _keep_warm_tick(self) -> None:
        if self.settings.stt_keep_warm:
            self.warm = True

    def status(self) -> STTStatus:
        return STTStatus(provider=self.provider, available=self.available, warm=self.warm, server_url=self.settings.stt_server_url)
