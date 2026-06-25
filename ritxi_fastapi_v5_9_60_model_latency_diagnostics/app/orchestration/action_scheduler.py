"""
v5.9.42 · Comentarios de arquitectura

Planificador de acciones de Ritxi.

Responsabilidades:
- recibir acciones desde la interfaz;
- coordinar movimiento, voz y retorno a neutral;
- evitar solapes de movimiento;
- ejecutar secuencias cuando una actividad tiene varios pasos.

Importante:
Las acciones de robot no deben lanzarse todas en paralelo si hay riesgo de que
Reachy/MuJoCo esté ejecutando un movimiento anterior.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Literal
from uuid import uuid4

from app.audio.tts_queue import TTSQueue
from app.core.config import Settings
from app.models.schemas import QueueStatus
from app.core.logging import log_event
from app.robot.base import PoseCommand, RobotClient
from app.robot.motion_library import speech_reactive_pose

logger = logging.getLogger(__name__)

Layer = Literal["speech", "emotion", "idle", "manual"]

PRIORITY_BY_LAYER: dict[str, int] = {
    "manual": 0,
    "speech": 10,
    "emotion": 20,
    "idle": 80,
}


@dataclass
class ActionIntent:
    emotion: str = "neutral"
    text: str | None = None
    motion_enabled: bool = True
    audio_enabled: bool = False
    return_to_neutral: bool = True
    layer: Layer = "emotion"
    reason: str = "chat"
    pose: PoseCommand | None = None
    speech_motion: bool = True
    action_id: str = field(default_factory=lambda: uuid4().hex)
    done: asyncio.Event = field(default_factory=asyncio.Event, compare=False)
    error: str | None = field(default=None, compare=False)

    @property
    def priority(self) -> int:
        return PRIORITY_BY_LAYER.get(self.layer, 50)


class ActionScheduler:
    """Scheduler con prioridades y capas de movimiento.

    Capas:
    - manual: prioridad máxima, ajustes desde panel.
    - speech: voz + movimiento reactivo durante la voz.
    - emotion: gesto principal asociado a emoción.
    - idle: respiración/idle suave, solo cuando no hay nada más.
    """

    def __init__(self, settings: Settings, robot: RobotClient, tts: TTSQueue, idle_enabled: bool = False):
        self.settings = settings
        self.robot = robot
        self.tts = tts
        self.idle_enabled = idle_enabled
        self.speech_motion_enabled = settings.speech_motion_enabled_default
        self.speech_motion_intensity = settings.speech_motion_intensity_default
        self._queue: asyncio.PriorityQueue[tuple[int, int, ActionIntent]] = asyncio.PriorityQueue()
        self._counter = 0
        self._worker_task: asyncio.Task[None] | None = None
        self._idle_task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()
        self._exec_lock = asyncio.Lock()
        self._busy = False
        self._current_action: str | None = None
        self._last_action: str | None = None
        self._last_layer: str | None = None

    async def start(self) -> None:
        self._stop_event.clear()
        self._worker_task = asyncio.create_task(self._worker(), name="ritxi-action-worker")
        self._idle_task = asyncio.create_task(self._idle_loop(), name="ritxi-idle-loop")

    async def stop(self) -> None:
        self._stop_event.set()
        for task in [self._worker_task, self._idle_task]:
            if task:
                task.cancel()
        await asyncio.gather(*[task for task in [self._worker_task, self._idle_task] if task], return_exceptions=True)

    async def enqueue(self, action: ActionIntent, wait: bool = False) -> ActionIntent:
        self._counter += 1
        action.enqueued_at = time.perf_counter()
        await self._queue.put((action.priority, self._counter, action))
        logger.info("Acción encolada id=%s layer=%s emotion=%s reason=%s", action.action_id, action.layer, action.emotion, action.reason)
        log_event("action_enqueue", action_id=action.action_id, layer=action.layer, emotion=action.emotion, reason=action.reason, priority=action.priority, text_len=len(action.text or ""), audio=action.audio_enabled, motion=action.motion_enabled, queue_size=self._queue.qsize())
        if wait:
            await action.done.wait()
        return action

    def set_idle(self, enabled: bool) -> None:
        self.idle_enabled = enabled

    def set_speech_motion(self, enabled: bool, intensity: float) -> None:
        self.speech_motion_enabled = enabled
        self.speech_motion_intensity = max(0.0, min(1.0, intensity))

    def status(self) -> QueueStatus:
        return QueueStatus(
            queue_size=self._queue.qsize(),
            busy=self._busy,
            idle_enabled=self.idle_enabled,
            current_action=self._current_action,
            last_action=self._last_action,
            last_layer=self._last_layer,
            speech_motion_enabled=self.speech_motion_enabled,
            speech_motion_intensity=self.speech_motion_intensity,
        )

    async def _worker(self) -> None:
        while not self._stop_event.is_set():
            _, _, action = await self._queue.get()
            try:
                await self._execute(action)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                action.error = str(exc)
                logger.exception("Error ejecutando acción %s: %s", action.action_id, exc)
            finally:
                action.done.set()
                self._queue.task_done()

    async def _execute(self, action: ActionIntent) -> None:
        async with self._exec_lock:
            start = time.perf_counter()
            queue_wait_ms = (start - getattr(action, "enqueued_at", start)) * 1000
            log_event("action_start", action_id=action.action_id, layer=action.layer, emotion=action.emotion, reason=action.reason, queue_wait_ms=round(queue_wait_ms, 2))
            self._busy = True
            self._current_action = f"{action.layer}:{action.reason}:{action.emotion}"
            self._last_layer = action.layer
            try:
                if action.pose is not None and action.motion_enabled:
                    await self.robot.set_pose(action.pose, layer=action.layer)
                    if getattr(self.robot, "last_error", None):
                        action.error = getattr(self.robot, "last_error", None)
                elif action.layer == "speech" and action.audio_enabled and action.text:
                    await self._execute_speech_action(action)
                else:
                    # v5.9.25: evitar solapes de movimiento.
                    # Antes se lanzaba motion+audio en paralelo y el retorno a neutral podía entrar
                    # mientras play_move() seguía activo en el daemon.
                    if action.motion_enabled:
                        await self.robot.perform_emotion(action.emotion, layer=action.layer)
                    if action.audio_enabled and action.text:
                        await self.tts.speak(action.text, wait=True)

                if action.motion_enabled and action.return_to_neutral and action.layer in {"emotion", "manual"} and action.pose is None:
                    await asyncio.sleep(0.15)
                    await self.robot.neutral()
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000
                log_event("action_end", action_id=action.action_id, layer=action.layer, emotion=action.emotion, reason=action.reason, elapsed_ms=round(elapsed_ms, 2), error=action.error, robot_connected=await self.robot.is_connected())
                self._last_action = self._current_action
                self._current_action = None
                self._busy = False

    async def _execute_speech_action(self, action: ActionIntent) -> None:
        """Habla y mueve el robot de forma suave mientras dura el TTS.

        El fallo de robot no debe bloquear la voz: si Reachy/daemon no está conectado,
        se registra el error y el TTS continúa.
        """
        if action.motion_enabled and action.emotion != "neutral":
            try:
                await self.robot.perform_emotion(action.emotion, layer="emotion")
            except Exception as exc:  # noqa: BLE001
                action.error = f"robot_emotion_failed: {exc}"
                log_event("robot_motion_error", action_id=action.action_id, stage="pre_speech_emotion", error=str(exc))

        tts_task = asyncio.create_task(self.tts.speak(action.text, wait=True))
        motion_task: asyncio.Task[None] | None = None
        if action.motion_enabled and action.speech_motion and self.speech_motion_enabled:
            motion_task = asyncio.create_task(self._speech_motion_loop(tts_task, action), name="ritxi-speech-motion")

        await tts_task
        if motion_task:
            motion_task.cancel()
            await asyncio.gather(motion_task, return_exceptions=True)
        if action.motion_enabled and action.return_to_neutral:
            try:
                await self.robot.neutral()
            except Exception as exc:  # noqa: BLE001
                action.error = action.error or f"robot_neutral_failed: {exc}"
                log_event("robot_motion_error", action_id=action.action_id, stage="neutral", error=str(exc))

    async def _speech_motion_loop(self, tts_task: asyncio.Task[object], action: ActionIntent) -> None:
        while not tts_task.done():
            try:
                await self.robot.set_pose(speech_reactive_pose(self.speech_motion_intensity), layer="speech")
            except Exception as exc:  # noqa: BLE001
                action.error = action.error or f"robot_speech_motion_failed: {exc}"
                log_event("robot_motion_error", action_id=action.action_id, stage="speech_motion", error=str(exc))
                return
            await asyncio.sleep(self.settings.speech_motion_interval_s)

    async def _idle_loop(self) -> None:
        while not self._stop_event.is_set():
            await asyncio.sleep(2.5)
            if not self.idle_enabled or self._busy or self._queue.qsize() > 0:
                continue
            if not hasattr(self.robot, "random_idle_pose"):
                continue
            if not await self.robot.is_connected():
                continue
            action = ActionIntent(
                emotion="neutral",
                pose=self.robot.random_idle_pose(),  # type: ignore[attr-defined]
                motion_enabled=True,
                audio_enabled=False,
                return_to_neutral=False,
                layer="idle",
                reason="idle",
            )
            await self.enqueue(action, wait=False)
