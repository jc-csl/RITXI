"""
v5.9.42 · Comentarios de arquitectura

Cliente de robot Reachy Mini / daemon MuJoCo.

Responsabilidades:
- conectar con el daemon de Reachy Mini;
- ejecutar emociones oficiales Pollen/Reachy;
- ejecutar posturas y movimientos propios;
- devolver estado de conexión al panel;
- evitar enviar comandos incompatibles mientras un movimiento sigue activo.

En simulación, el daemon se ejecuta normalmente en:
http://127.0.0.1:8000
"""

from __future__ import annotations

import asyncio
import logging
import math
import random
import time
from typing import Any

from app.core.logging import log_event
from app.robot.base import PoseCommand
from app.robot.motion_library import idle_pose, poses_for_emotion
from app.core.config import get_settings
from app.robot.recorded_emotions import RecordedEmotionLibrary

logger = logging.getLogger(__name__)


class ReachySdkRobotClient:
    """Adaptador opcional para `reachy_mini`.

    Funciona con Reachy real o con `reachy-mini-daemon --sim` cuando RITXI_MODE=reachy_daemon.
    Si el daemon no está arrancado, registra el error pero no bloquea el TTS ni la conversación.
    """

    kind = "reachy_sdk"

    def __init__(self, host: str):
        self.host = host
        self.robot: Any | None = None
        self._np: Any | None = None
        self._create_head_pose: Any | None = None
        self.last_error: str | None = None
        self.last_pose: PoseCommand | None = None
        self.last_connect_attempt_ms: float | None = None
        self.connect_attempts = 0
        self.recorded_library = RecordedEmotionLibrary(get_settings())
        self.last_recorded_result: dict[str, object] | None = None

    async def connect(self) -> bool:
        self.connect_attempts += 1
        self.last_connect_attempt_ms = time.time() * 1000
        log_event("robot_connect_attempt", host=self.host, attempt=self.connect_attempts)

        def _connect() -> bool:
            try:
                import numpy as np  # type: ignore
                from reachy_mini import ReachyMini  # type: ignore
                from reachy_mini.utils import create_head_pose  # type: ignore

                self._np = np
                self._create_head_pose = create_head_pose
                self.robot = ReachyMini(host=self.host, media_backend="no_media")
                self.last_error = None
                return True
            except Exception as exc:  # noqa: BLE001
                self.last_error = str(exc)
                logger.warning("No se pudo conectar con Reachy en %s: %s", self.host, exc)
                self.robot = None
                return False

        ok = await asyncio.to_thread(_connect)
        log_event("robot_connect_result", host=self.host, ok=ok, error=self.last_error)
        return ok

    async def close(self) -> None:
        log_event("robot_close", connected=self.robot is not None)
        self.robot = None

    async def is_connected(self) -> bool:
        return self.robot is not None

    async def set_pose(self, pose: PoseCommand, layer: str = "manual") -> None:
        if not self.robot:
            if layer == "idle":
                self.last_error = "Reachy daemon no conectado; idle omitido."
                return
            ok = await self.connect()
            if not ok:
                # No lanzamos excepción para que la conversación pueda continuar con audio/texto.
                log_event("robot_pose_skipped", layer=layer, reason="not_connected", error=self.last_error)
                return

        def _move() -> None:
            assert self.robot is not None
            assert self._np is not None
            assert self._create_head_pose is not None
            self.robot.goto_target(
                head=self._create_head_pose(
                    yaw=pose.yaw,
                    pitch=pose.pitch,
                    roll=pose.roll,
                    degrees=True,
                ),
                antennas=self._np.deg2rad([pose.left_antenna, pose.right_antenna]),
                duration=pose.duration_s,
            )

        start = time.perf_counter()
        try:
            await asyncio.to_thread(_move)
            self.last_pose = pose
            self.last_error = None
            log_event(
                "robot_pose_sent",
                layer=layer,
                yaw=pose.yaw,
                pitch=pose.pitch,
                roll=pose.roll,
                left_antenna=pose.left_antenna,
                right_antenna=pose.right_antenna,
                duration_s=pose.duration_s,
                elapsed_ms=round((time.perf_counter() - start) * 1000, 2),
            )
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            self.robot = None
            log_event("robot_pose_error", layer=layer, error=self.last_error)

    async def neutral(self) -> None:
        await self.set_pose(PoseCommand(), layer="neutral")

    async def perform_emotion(self, emotion: str, layer: str = "emotion") -> None:
        log_event("robot_emotion_start", emotion=emotion, layer=layer)

        # 1) Primero intentamos reproducir las emociones grabadas oficiales
        # de Pollen Robotics, con movimiento cinemático + audio .wav si está disponible.
        settings = get_settings()
        if settings.use_recorded_moves_default and self.robot is not None:
            ok = await self._try_recorded_move(emotion)
            if ok:
                log_event("robot_emotion_end", emotion=emotion, layer=layer, source="recorded_move", error=self.last_error)
                return

        # 2) Si la librería no existe, no hay conexión, o el ID cambió, usamos
        # movimientos internos como fallback para que Ritxi siga siendo dinámico.
        if emotion == "baile":
            await self._dance_loop(seconds=1.1)
            log_event("robot_emotion_end", emotion=emotion, layer=layer, source="fallback_dance", error=self.last_error)
            return
        if emotion in {"celebracion", "aplauso", "yes1", "cheerful1"}:
            await self._celebration_loop(seconds=0.8)
            log_event("robot_emotion_end", emotion=emotion, layer=layer, source="fallback_celebration", error=self.last_error)
            return
        if emotion in {"asustado", "miedo", "gasp1", "anxiety1"}:
            await self._shake_loop(seconds=0.7, yaw_amp=5, pitch=18, antennas=-45)
            log_event("robot_emotion_end", emotion=emotion, layer=layer, source="fallback_shake", error=self.last_error)
            return
        for pose in poses_for_emotion(emotion):
            await self.set_pose(pose, layer=layer)
        log_event("robot_emotion_end", emotion=emotion, layer=layer, source="fallback_pose", error=self.last_error)

    def _recorded_settle_seconds(self, executed_id: str | None, move: Any | None = None) -> float:
        name = (executed_id or "").lower()
        # Evitar comandos superpuestos mientras el daemon ejecuta play_move().
        # No intentamos ser exactos; solo dar tiempo a que termine la cinemática oficial.
        if any(x in name for x in ["dance", "boredom", "exhausted"]):
            return 3.8
        if any(x in name for x in ["curious", "calming", "anxiety", "sad", "thoughtful"]):
            return 2.4
        if any(x in name for x in ["yes", "no", "cheerful", "attentive", "wake", "welcome", "success"]):
            return 1.5
        return 1.2

    async def _try_recorded_move(self, emotion: str) -> bool:
        self.last_recorded_result = {"ok": False, "requested": emotion, "error": None, "audio_started": False}
        if not self.robot:
            self.last_recorded_result["error"] = "robot_not_connected"
            return False

        def _play() -> bool:
            assert self.robot is not None
            executed_id, move, error = self.recorded_library.get_move(emotion)
            if move is None:
                self.last_error = error
                self.last_recorded_result = {"ok": False, "requested": emotion, "executed_id": None, "error": error, "audio_started": False}
                return False
            # El audio oficial se reproduce desde el navegador.
            # Backend no intenta inicializar pygame/daemon audio para evitar:
            # "Audio system is not initialized".
            audio_path = getattr(move, "audio_path", None)
            start = time.perf_counter()
            self.robot.play_move(move)
            settle_s = self._recorded_settle_seconds(executed_id, move)
            time.sleep(settle_s)
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            self.last_error = None
            self.last_recorded_result = {
                "ok": True,
                "requested": emotion,
                "executed_id": executed_id,
                "audio_path": str(audio_path) if audio_path else None,
                "audio_started": False,
                "elapsed_ms": elapsed_ms,
                "settle_s": settle_s,
                "source": "pollen_recorded_move_browser_audio",
            }
            log_event(
                "recorded_move_played",
                requested=emotion,
                executed_id=executed_id,
                audio_path=audio_path,
                audio_started=False,
                elapsed_ms=elapsed_ms,
                settle_s=settle_s,
            )
            return True

        try:
            return await asyncio.to_thread(_play)
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            self.last_recorded_result = {"ok": False, "requested": emotion, "error": self.last_error, "audio_started": False}
            log_event("recorded_move_play_error", emotion=emotion, error=self.last_error)
            return False

    def random_idle_pose(self) -> PoseCommand:
        return idle_pose()

    async def _shake_loop(self, seconds: float, yaw_amp: float, pitch: float, antennas: float) -> None:
        start = asyncio.get_running_loop().time()
        while asyncio.get_running_loop().time() - start < seconds:
            t = asyncio.get_running_loop().time() - start
            await self.set_pose(
                PoseCommand(
                    yaw=yaw_amp * math.sin(t * 42),
                    pitch=pitch,
                    roll=-4,
                    left_antenna=antennas,
                    right_antenna=antennas,
                    duration_s=0.04,
                )
            )

    async def _dance_loop(self, seconds: float) -> None:
        start = asyncio.get_running_loop().time()
        while asyncio.get_running_loop().time() - start < seconds:
            t = asyncio.get_running_loop().time() - start
            await self.set_pose(
                PoseCommand(
                    yaw=24 * math.sin(t * 5),
                    pitch=-4 + 8 * math.sin(t * 10),
                    roll=13 * math.cos(t * 5),
                    left_antenna=45 * math.cos(t * 8),
                    right_antenna=45 * math.sin(t * 8),
                    duration_s=0.06,
                )
            )

    async def _celebration_loop(self, seconds: float) -> None:
        start = asyncio.get_running_loop().time()
        while asyncio.get_running_loop().time() - start < seconds:
            t = asyncio.get_running_loop().time() - start
            await self.set_pose(
                PoseCommand(
                    yaw=8 * math.sin(t * 8),
                    pitch=-10,
                    roll=6 * math.sin(t * 8),
                    left_antenna=55 + random.uniform(-8, 8),
                    right_antenna=55 + random.uniform(-8, 8),
                    duration_s=0.08,
                )
            )
