from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PoseCommand:
    yaw: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0
    left_antenna: float = 0.0
    right_antenna: float = 0.0
    duration_s: float = 0.35


class RobotClient(Protocol):
    kind: str

    async def connect(self) -> bool: ...

    async def close(self) -> None: ...

    async def is_connected(self) -> bool: ...

    async def perform_emotion(self, emotion: str, layer: str = "emotion") -> None: ...

    async def set_pose(self, pose: PoseCommand, layer: str = "manual") -> None: ...

    async def neutral(self) -> None: ...
