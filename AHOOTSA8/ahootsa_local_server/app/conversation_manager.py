from dataclasses import dataclass
from typing import Any


@dataclass
class ConversationDecision:
    state: str
    action: str
    text: str
    activity: str | None
    reason: str
    wait_seconds: float
    end_activity: bool
    metadata: dict[str, Any]


def _recent_count(events: list[Any], event_type: str, limit: int = 8) -> int:
    return sum(1 for event in events[-limit:] if event.event_type == event_type)


def _last_event(events: list[Any], event_type: str) -> Any | None:
    for event in reversed(events):
        if event.event_type == event_type:
            return event
    return None


def decide_next_action(
    *,
    session: Any,
    user: Any,
    profile: Any,
    memories: list[Any],
    events: list[Any],
) -> ConversationDecision:
    """Decide la siguiente acción sin depender todavía de un LLM.

    Es una primera capa determinista y comprobable. Prioriza seguridad,
    accesibilidad, pausas y finalización correcta de actividades.
    """

    wait_seconds = float(profile.response_wait_seconds or 5.0)
    current_activity_event = _last_event(events, "activity_started")
    completed_activity_event = _last_event(events, "activity_completed")
    current_activity = (
        current_activity_event.activity
        if current_activity_event is not None
        else None
    )

    if (
        current_activity_event is not None
        and completed_activity_event is not None
        and completed_activity_event.occurred_at >= current_activity_event.occurred_at
    ):
        current_activity = None

    recent_errors = _recent_count(events, "error_detected", limit=5)
    recent_silences = _recent_count(events, "silence_detected", limit=5)
    recent_hints = _recent_count(events, "hint_given", limit=6)
    last_response = _last_event(events, "user_response")

    if recent_errors >= 2:
        return ConversationDecision(
            state="technical_pause",
            action="pause_and_notify",
            text="Voy a parar un momento para comprobar que todo funciona bien.",
            activity=current_activity,
            reason="Se han detectado varios errores recientes.",
            wait_seconds=wait_seconds,
            end_activity=False,
            metadata={"recent_errors": recent_errors},
        )

    if recent_silences >= 2:
        return ConversationDecision(
            state="needs_more_time",
            action="wait",
            text="No hay prisa. Tómate el tiempo que necesites.",
            activity=current_activity,
            reason="Se han detectado silencios prolongados recientes.",
            wait_seconds=min(wait_seconds + 5.0, 30.0),
            end_activity=False,
            metadata={"recent_silences": recent_silences},
        )

    if recent_hints >= 2 and current_activity is not None:
        return ConversationDecision(
            state="activity_difficult",
            action="offer_change",
            text="Esta actividad parece difícil. Podemos probar otra diferente.",
            activity=current_activity,
            reason="Se han necesitado varias pistas en la actividad actual.",
            wait_seconds=wait_seconds,
            end_activity=True,
            metadata={"recent_hints": recent_hints},
        )

    if last_response is not None and last_response.success is False:
        return ConversationDecision(
            state="needs_support",
            action="give_hint",
            text="Vamos paso a paso. Te daré una pista.",
            activity=current_activity,
            reason="La última respuesta evaluada no fue correcta.",
            wait_seconds=wait_seconds,
            end_activity=False,
            metadata={"last_response_id": last_response.id},
        )

    if current_activity is None:
        preferred_name = user.preferred_name or user.name
        interest_memory = next(
            (
                memory
                for memory in memories
                if memory.active
                and memory.category in {"interest", "preference"}
            ),
            None,
        )
        memory_text = (
            f" Recuerdo que {interest_memory.content.lower()}"
            if interest_memory is not None
            else ""
        )
        return ConversationDecision(
            state="ready",
            action="offer_activity",
            text=(
                f"Hola, {preferred_name}.{memory_text} "
                "¿Qué actividad te apetece hacer?"
            ).strip(),
            activity=None,
            reason="No hay ninguna actividad activa.",
            wait_seconds=wait_seconds,
            end_activity=False,
            metadata={
                "memory_used_id": (
                    interest_memory.id if interest_memory is not None else None
                )
            },
        )

    return ConversationDecision(
        state="in_activity",
        action="continue",
        text="Muy bien. Seguimos con el siguiente paso.",
        activity=current_activity,
        reason="La actividad está activa y no hay incidencias prioritarias.",
        wait_seconds=wait_seconds,
        end_activity=False,
        metadata={},
    )
