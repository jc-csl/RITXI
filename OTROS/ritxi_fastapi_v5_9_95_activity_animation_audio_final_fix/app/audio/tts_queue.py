from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from app.audio.echo_guard import EchoGuard
from app.core.config import Settings
from app.core.logging import log_event
from app.models.schemas import TTSStatus

logger = logging.getLogger(__name__)


@dataclass
class TTSTask:
    text: str
    task_id: str = field(default_factory=lambda: uuid4().hex)
    done: asyncio.Event = field(default_factory=asyncio.Event)
    error: str | None = None


class TTSQueue:
    """Cola única de TTS: nunca permite dos voces a la vez."""

    def __init__(self, settings: Settings, echo_guard: EchoGuard):
        self.settings = settings
        self.echo_guard = echo_guard
        self.provider = settings.tts_provider
        self.engine: Any | None = None
        self.available = self.provider in {"none", "mock", "browser"}
        self._queue: asyncio.Queue[TTSTask] = asyncio.Queue()
        self._worker_task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()
        self._speaking = False
        self._init_engine()

    def _init_engine(self) -> None:
        if self.provider != "pyttsx3":
            return
        try:
            import pyttsx3  # type: ignore

            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", self.settings.tts_rate)
            if self.settings.tts_voice:
                self.engine.setProperty("voice", self.settings.tts_voice)
            self.available = True
            logger.info("TTS pyttsx3 inicializado")
        except Exception as exc:  # noqa: BLE001
            self.engine = None
            self.available = False
            logger.warning("TTS pyttsx3 no disponible: %s", exc)

    async def start(self) -> None:
        self._stop_event.clear()
        self._worker_task = asyncio.create_task(self._worker(), name="ritxi-tts-worker")

    async def stop(self) -> None:
        self._stop_event.set()
        if self._worker_task:
            self._worker_task.cancel()
            await asyncio.gather(self._worker_task, return_exceptions=True)

    async def speak(self, text: str | None, wait: bool = True) -> TTSTask | None:
        if not text or self.provider == "none":
            return None
        task = TTSTask(text=text.strip())
        log_event("tts_enqueue", task_id=task.task_id, provider=self.provider, text_len=len(task.text), preview=task.text[:120], wait=wait)
        await self._queue.put(task)
        if wait:
            await task.done.wait()
        return task

    def status(self) -> TTSStatus:
        return TTSStatus(provider=self.provider, available=self.available, queue_size=self._queue.qsize(), speaking=self._speaking)

    async def _worker(self) -> None:
        while not self._stop_event.is_set():
            task = await self._queue.get()
            start = time.perf_counter()
            try:
                self._speaking = True
                log_event("tts_start", task_id=task.task_id, provider=self.provider, text_len=len(task.text), queue_size=self._queue.qsize())
                await self.echo_guard.mark_speaking(True)
                if self.provider == "browser":
                    # La voz real la ejecuta el navegador con Web Speech Synthesis.
                    # El backend solo registra la intención de habla para mantener la cola
                    # y evitar que pyttsx3 bloquee el ciclo de conversación en Windows.
                    logger.info("[TTS BROWSER] Delegado al navegador: %s", task.text)
                    log_event("tts_browser_delegate", task_id=task.task_id, text_len=len(task.text), preview=task.text[:120])
                elif self.provider == "mock":
                    logger.info("[TTS MOCK] %s", task.text)
                    await asyncio.sleep(min(2.0, max(0.25, len(task.text) / 80)))
                elif self.provider == "pyttsx3" and self.engine:
                    await asyncio.wait_for(asyncio.to_thread(self._speak_sync, task.text), timeout=max(4.0, min(25.0, len(task.text) / 8)))
                else:
                    logger.info("[TTS sin salida] %s", task.text)
            except Exception as exc:  # noqa: BLE001
                task.error = str(exc)
                log_event("tts_error", task_id=task.task_id, error=str(exc))
                logger.warning("Error TTS: %s", exc)
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000
                log_event("tts_end", task_id=task.task_id, error=task.error, elapsed_ms=round(elapsed_ms, 2))
                self._speaking = False
                await self.echo_guard.mark_speaking(False)
                task.done.set()
                self._queue.task_done()

    def _speak_sync(self, text: str) -> None:
        assert self.engine is not None
        self.engine.say(text)
        self.engine.runAndWait()
