import json
from dataclasses import asdict
from typing import Any

from .activities.base import ActivityBase, ActivityStep
from .activities.emotions import EmotionsActivity
from .activities.preferences import PreferencesActivity


class ActivityEngine:
    def __init__(self) -> None:
        self._activities: dict[str, ActivityBase] = {}
        self.register(EmotionsActivity())
        self.register(PreferencesActivity())

    def register(self, activity: ActivityBase) -> None:
        if activity.key in self._activities:
            raise ValueError(f"La actividad '{activity.key}' ya está registrada.")
        self._activities[activity.key] = activity

    def list_activities(self) -> list[dict[str, str]]:
        return [
            activity.serialize()
            for activity in sorted(
                self._activities.values(),
                key=lambda item: item.title,
            )
        ]

    def get(self, key: str) -> ActivityBase:
        activity = self._activities.get(key)
        if activity is None:
            raise KeyError(key)
        return activity

    def start(self, key: str, context: dict[str, Any]) -> ActivityStep:
        return self.get(key).start(context)

    def evaluate(
        self,
        key: str,
        current_step: int,
        answer: str,
        context: dict[str, Any],
    ) -> ActivityStep:
        return self.get(key).evaluate(current_step, answer, context)

    @staticmethod
    def step_to_dict(step: ActivityStep) -> dict[str, Any]:
        return asdict(step)

    @staticmethod
    def metadata_from_event(event: Any) -> dict[str, Any]:
        if not event.metadata_json:
            return {}
        try:
            value = json.loads(event.metadata_json)
            return value if isinstance(value, dict) else {}
        except (json.JSONDecodeError, TypeError):
            return {}


activity_engine = ActivityEngine()
