from __future__ import annotations

import asyncio
import logging
from dataclasses import asdict

from app.core.logging import log_event
from app.robot.base import PoseCommand
from app.robot.motion_library import idle_pose, poses_for_emotion

logger = logging.getLogger(__name__)


class SimulatedRobotClient:
    kind = "internal_simulation"

    def __init__(self) -> None:
        self.connected = False
        self.last_emotion = "neutral"
        self.last_pose = PoseCommand()
        self.layers: dict[str, PoseCommand | str | None] = {"idle": None, "emotion": None, "speech": None, "manual": None}

    async def connect(self) -> bool:
        self.connected = True
        logger.info("Robot simulado interno conectado")
        log_event("sim_robot_connect")
        return True

    async def close(self) -> None:
        self.connected = False
        logger.info("Robot simulado interno cerrado")
        log_event("sim_robot_close")

    async def is_connected(self) -> bool:
        return self.connected

    async def perform_emotion(self, emotion: str, layer: str = "emotion") -> None:
        self.last_emotion = emotion
        self.layers[layer] = emotion
        logger.info("[SIM ROBOT] layer=%s emotion=%s", layer, emotion)
        log_event("sim_robot_emotion", layer=layer, emotion=emotion)
        for pose in poses_for_emotion(emotion):
            await self.set_pose(pose, layer=layer)

    async def set_pose(self, pose: PoseCommand, layer: str = "manual") -> None:
        self.last_pose = pose
        self.layers[layer] = pose
        logger.info("[SIM ROBOT] layer=%s pose=%s", layer, asdict(pose))
        log_event("sim_robot_pose", layer=layer, pose=asdict(pose))
        await asyncio.sleep(min(max(pose.duration_s, 0.05), 2.0))

    async def neutral(self) -> None:
        await self.set_pose(PoseCommand(), layer="emotion")
        self.last_emotion = "neutral"
        self.layers["emotion"] = "neutral"

    def random_idle_pose(self) -> PoseCommand:
        return idle_pose()
