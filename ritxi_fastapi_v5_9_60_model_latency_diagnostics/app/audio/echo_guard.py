from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from app.models.schemas import EchoGuardStatus
from app.core.logging import log_event

logger = logging.getLogger(__name__)


@dataclass
class EchoGuard:
    enabled: bool = True
    cooldown_s: float = 0.8

    def __post_init__(self) -> None:
        self.microphone_enabled = True
        self.speaking = False
        self.reason: str | None = None
        self._lock = asyncio.Lock()

    async def mute(self, reason: str = "turn") -> None:
        if not self.enabled:
            return
        async with self._lock:
            self.microphone_enabled = False
            self.reason = reason
            logger.info("EchoGuard: micro OFF (%s)", reason)
            log_event("micro_off", reason=reason)

    async def mark_speaking(self, speaking: bool) -> None:
        if not self.enabled:
            return
        async with self._lock:
            self.speaking = speaking
            if speaking:
                self.microphone_enabled = False
                self.reason = "speaking"
            logger.info("EchoGuard: speaking=%s", speaking)
            log_event("speaking_state", speaking=speaking, microphone_enabled=self.microphone_enabled, reason=self.reason)

    async def cooldown_and_unmute(self, reason: str = "turn-complete") -> None:
        if not self.enabled:
            return
        if self.cooldown_s > 0:
            await asyncio.sleep(self.cooldown_s)
        async with self._lock:
            self.speaking = False
            self.microphone_enabled = True
            self.reason = reason
            logger.info("EchoGuard: micro ON (%s)", reason)
            log_event("micro_on", reason=reason)


    async def force_unmute(self, reason: str = "manual-force") -> None:
        async with self._lock:
            self.speaking = False
            self.microphone_enabled = True
            self.reason = reason
            logger.info("EchoGuard: micro FORCE ON (%s)", reason)
            log_event("micro_force_on", reason=reason)

    def status(self) -> EchoGuardStatus:
        return EchoGuardStatus(
            enabled=self.enabled,
            microphone_enabled=self.microphone_enabled,
            speaking=self.speaking,
            cooldown_s=self.cooldown_s,
            reason=self.reason,
        )
