from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .activity_engine import activity_engine
from .config import DATABASE_PATH


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _metadata(event: models.SessionEvent) -> dict[str, Any]:
    return activity_engine.metadata_from_event(event)


class ContextManager:
    """Construye un contexto coherente para un turno de Ahootsa."""

    def __init__(self) -> None:
        self.snapshot_dir = Path(DATABASE_PATH).parent / "context_snapshots"

    def get_active_session(self, db: Session) -> models.SessionRecord | None:
        return db.scalar(
            select(models.SessionRecord)
            .where(models.SessionRecord.status == "active")
            .order_by(models.SessionRecord.started_at.desc())
        )

    def build(
        self,
        session: models.SessionRecord,
        db: Session,
        *,
        recent_event_limit: int = 20,
    ) -> dict[str, Any]:
        user = session.user
        profile = user.profile

        memories = list(
            db.scalars(
                select(models.MemoryItem)
                .where(
                    models.MemoryItem.user_id == user.id,
                    models.MemoryItem.active.is_(True),
                )
                .order_by(
                    models.MemoryItem.importance.desc(),
                    models.MemoryItem.updated_at.desc(),
                )
            ).all()
        )

        all_events = list(
            db.scalars(
                select(models.SessionEvent)
                .where(models.SessionEvent.session_id == session.id)
                .order_by(models.SessionEvent.occurred_at)
            ).all()
        )
        recent_events = all_events[-recent_event_limit:]

        activity = self._activity_state(all_events)
        conversation_state = self._conversation_state(recent_events, activity)

        return {
            "context_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "session": {
                "id": session.id,
                "status": session.status,
                "started_at": _iso(session.started_at),
                "finished_at": _iso(session.finished_at),
                "started_by": session.started_by,
            },
            "user": {
                "id": user.id,
                "external_id": user.external_id,
                "name": user.name,
                "preferred_name": user.preferred_name or user.name,
                "language": user.language,
                "active": user.active,
            },
            "profile": {
                "communication_level": getattr(profile, "communication_level", None),
                "reading_level": getattr(profile, "reading_level", None),
                "speech_speed": getattr(profile, "speech_speed", None),
                "response_wait_seconds": getattr(profile, "response_wait_seconds", None),
                "uses_pictograms": getattr(profile, "uses_pictograms", None),
                "preferred_topics": getattr(profile, "preferred_topics", None),
                "avoid_topics": getattr(profile, "avoid_topics", None),
                "support_notes": getattr(profile, "support_notes", None),
            },
            "memory": [
                {
                    "id": item.id,
                    "category": item.category,
                    "content": item.content,
                    "source": item.source,
                    "importance": item.importance,
                    "updated_at": _iso(item.updated_at),
                }
                for item in memories
            ],
            "activity": activity,
            "conversation_state": conversation_state,
            "recent_events": [
                {
                    "id": event.id,
                    "event_type": event.event_type,
                    "source": event.source,
                    "activity": event.activity,
                    "value_text": event.value_text,
                    "value_number": event.value_number,
                    "success": event.success,
                    "metadata": _metadata(event),
                    "occurred_at": _iso(event.occurred_at),
                }
                for event in recent_events
            ],
            "counters": {
                "total_events": len(all_events),
                "recent_events": len(recent_events),
                "active_memories": len(memories),
            },
        }

    def save_snapshot(self, context: dict[str, Any]) -> Path:
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        session_id = context["session"]["id"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = self.snapshot_dir / f"session_{session_id}_{timestamp}.json"
        path.write_text(
            json.dumps(context, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    @staticmethod
    def _activity_state(events: list[models.SessionEvent]) -> dict[str, Any] | None:
        last_start_index: int | None = None
        for index, event in enumerate(events):
            if event.event_type == "activity_started":
                last_start_index = index

        if last_start_index is None:
            return None

        relevant = events[last_start_index:]
        if any(event.event_type == "activity_completed" for event in relevant):
            return None

        activity_name = relevant[0].activity
        if not activity_name:
            return None

        current_step = 1
        last_robot_text: str | None = None
        last_action = "ask"

        for event in relevant:
            if event.event_type != "robot_message":
                continue
            data = _metadata(event)
            if isinstance(data.get("step"), int):
                current_step = data["step"]
            if isinstance(data.get("action"), str):
                last_action = data["action"]
            last_robot_text = event.value_text

        return {
            "key": activity_name,
            "step": current_step,
            "last_action": last_action,
            "last_robot_text": last_robot_text,
        }

    @staticmethod
    def _conversation_state(
        events: list[models.SessionEvent],
        activity: dict[str, Any] | None,
    ) -> dict[str, Any]:
        recent_errors = sum(event.event_type == "error_detected" for event in events[-5:])
        recent_silences = sum(event.event_type == "silence_detected" for event in events[-5:])
        recent_hints = sum(event.event_type == "hint_given" for event in events[-6:])

        if recent_errors >= 2:
            state = "technical_pause"
        elif recent_silences >= 2:
            state = "needs_more_time"
        elif recent_hints >= 2 and activity is not None:
            state = "activity_difficult"
        elif activity is not None:
            state = "in_activity"
        else:
            state = "ready"

        return {
            "state": state,
            "recent_errors": recent_errors,
            "recent_silences": recent_silences,
            "recent_hints": recent_hints,
        }


context_manager = ContextManager()
