from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActivityStep:
    step: int
    action: str
    text: str
    completed: bool = False
    success: bool | None = None
    expected_answer: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ActivityBase(ABC):
    """Interfaz común de todas las actividades Ahootsa."""

    key: str
    title: str
    description: str
    version: str = "1.0"

    @abstractmethod
    def start(self, context: dict[str, Any]) -> ActivityStep:
        raise NotImplementedError

    @abstractmethod
    def next_step(
        self,
        current_step: int,
        context: dict[str, Any],
    ) -> ActivityStep:
        raise NotImplementedError

    @abstractmethod
    def evaluate(
        self,
        current_step: int,
        answer: str,
        context: dict[str, Any],
    ) -> ActivityStep:
        raise NotImplementedError

    def serialize(self) -> dict[str, str]:
        return {
            "key": self.key,
            "title": self.title,
            "description": self.description,
            "version": self.version,
        }
