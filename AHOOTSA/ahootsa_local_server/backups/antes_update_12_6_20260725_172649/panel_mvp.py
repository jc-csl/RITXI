from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .database import get_db
from .session_preparation_service import session_preparation_service


PANEL_STATIC_DIR = Path(__file__).resolve().parent / "static" / "panel"
router = APIRouter(tags=["panel-mvp"])


class PanelPrepareRequest(BaseModel):
    user_external_id: str = Field(min_length=1, max_length=50)
    activity: str = Field(min_length=1, max_length=120)
    level: Literal["initial", "intermediate", "advanced"]
    started_by: str = Field(default="Monitor/a", min_length=1, max_length=120)


class PanelQuickEventRequest(BaseModel):
    action: Literal[
        "adequate",
        "partial",
        "incorrect",
        "no_response",
        "hint",
        "repeat",
        "example",
    ]
    note: str | None = Field(default=None, max_length=1000)


class PanelFinishRequest(BaseModel):
    note: str | None = Field(default=None, max_length=4000)
    decision: Literal[
        "maintain",
        "raise",
        "lower_temporarily",
        "repeat_session",
        "no_decision",
    ] = "no_decision"


class ExampleUserRequest(BaseModel):
    external_id: str = Field(default="ALEX-EJEMPLO", min_length=1, max_length=50)
    name: str = Field(default="Álex", min_length=1, max_length=120)


@router.get("/panel", include_in_schema=False)
def panel_page() -> FileResponse:
    return FileResponse(PANEL_STATIC_DIR / "panel.html", media_type="text/html")


def _active_session(db: Session) -> models.SessionRecord | None:
    return db.scalar(
        select(models.SessionRecord).where(models.SessionRecord.status == "active")
    )


def _event_metadata(event: models.SessionEvent) -> dict[str, Any]:
    if not event.metadata_json:
        return {}
    try:
        value = json.loads(event.metadata_json)
        return value if isinstance(value, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def _current_activity(session: models.SessionRecord) -> dict[str, Any] | None:
    for event in reversed(session.events):
        if event.event_type == "activity_started":
            data = _event_metadata(event)
            return {
                "key": event.activity,
                "title": event.value_text or event.activity,
                "level": data.get("level"),
                "level_title": data.get("level_title"),
            }
    return None


def _panel_summary(session: models.SessionRecord) -> dict[str, Any]:
    counts = {
        "adequate": 0,
        "partial": 0,
        "incorrect": 0,
        "no_response": 0,
        "hint": 0,
        "repeat": 0,
        "example": 0,
    }
    decision = None
    for event in session.events:
        metadata = _event_metadata(event)
        rating = metadata.get("rating")
        if event.event_type == "user_response":
            if rating == "partial":
                counts["partial"] += 1
            elif event.success is True:
                counts["adequate"] += 1
            elif event.success is False:
                counts["incorrect"] += 1
        elif event.event_type == "silence_detected":
            counts["no_response"] += 1
        elif event.event_type == "hint_given":
            counts["hint"] += 1
        elif event.event_type == "instruction_repeated":
            counts["repeat"] += 1
        elif event.event_type == "example_given":
            counts["example"] += 1
        elif event.event_type == "professional_decision":
            decision = metadata.get("decision") or event.value_text

    timing = session_preparation_service.timing_summary(
        session.id,
        fallback_started_at=session.started_at,
        fallback_finished_at=session.finished_at,
    )
    evaluated = counts["adequate"] + counts["partial"] + counts["incorrect"]
    return {
        "session_id": session.id,
        "status": session.status,
        "user": {
            "external_id": session.user.external_id,
            "name": session.user.name,
            "preferred_name": session.user.preferred_name or session.user.name,
        },
        "activity": _current_activity(session),
        "started_at": session.started_at.isoformat(),
        "finished_at": session.finished_at.isoformat() if session.finished_at else None,
        **timing,
        "counts": counts,
        "evaluated_responses": evaluated,
        "professional_decision": decision,
        "summary": session.summary,
    }


@router.get("/panel/api/bootstrap")
def panel_bootstrap(db: Session = Depends(get_db)) -> dict[str, Any]:
    users = list(
        db.scalars(
            select(models.User)
            .where(models.User.active.is_(True))
            .order_by(models.User.name)
        ).all()
    )
    active = _active_session(db)
    active_summary = _panel_summary(active) if active else None
    if active_summary is not None:
        session_preparation_service.sync_running_status(active.id)
        active_summary = _panel_summary(active)
        active_summary["profile_prepared"] = (
            session_preparation_service.active_profile_is_prepared_for(active.id)
        )

    return {
        "version": "0.12.5",
        "users": [
            {
                "external_id": user.external_id,
                "name": user.name,
                "preferred_name": user.preferred_name or user.name,
                "language": user.language,
            }
            for user in users
        ],
        "activities": session_preparation_service.list_activities(),
        "services": session_preparation_service.service_status(),
        "active_session": active_summary,
    }


@router.get("/panel/api/config/check")
def check_panel_configuration() -> dict[str, Any]:
    try:
        return session_preparation_service.validate_configuration()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/panel/api/conversation-profile")
def conversation_profile_status() -> dict[str, Any]:
    return session_preparation_service.official_profile_status()


@router.post("/panel/api/example-user", status_code=201)
def create_example_user(
    payload: ExampleUserRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    existing = db.scalar(
        select(models.User).where(models.User.external_id == payload.external_id)
    )
    if existing is not None:
        return {
            "created": False,
            "external_id": existing.external_id,
            "preferred_name": existing.preferred_name or existing.name,
        }

    user = models.User(
        external_id=payload.external_id.strip(),
        name=payload.name.strip(),
        preferred_name=payload.name.strip(),
        language="es",
        notes="Usuario de ejemplo creado desde el panel MVP.",
    )
    user.profile = models.UserProfile(
        communication_style="simple",
        speech_speed="slow",
        response_wait_seconds=8.0,
        preferred_interaction_mode="voice",
        preferred_reinforcement="refuerzo verbal positivo",
        interests="música y actividades cotidianas",
        max_instructions_per_turn=1,
    )
    db.add(user)
    db.commit()
    return {
        "created": True,
        "external_id": user.external_id,
        "preferred_name": user.preferred_name or user.name,
    }


@router.post("/panel/api/session/prepare", status_code=201)
def prepare_panel_session(
    payload: PanelPrepareRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    user = db.scalar(
        select(models.User).where(
            models.User.external_id == payload.user_external_id,
            models.User.active.is_(True),
        )
    )
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o inactivo.")

    try:
        return session_preparation_service.prepare_session(
            db=db,
            user=user,
            activity_key=payload.activity,
            level=payload.level,
            started_by=payload.started_by,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Actividad no encontrada.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/panel/api/launch/daemon")
def launch_daemon() -> dict[str, Any]:
    try:
        return session_preparation_service.launch_daemon()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/panel/api/launch/conversation-app")
def launch_conversation_app(db: Session = Depends(get_db)) -> dict[str, Any]:
    session = _active_session(db)
    if session is None:
        raise HTTPException(status_code=404, detail="No hay sesión preparada.")
    try:
        return session_preparation_service.launch_conversation_app(session.id)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/panel/api/session/event", status_code=201)
def register_quick_event(
    payload: PanelQuickEventRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    session = _active_session(db)
    if session is None:
        raise HTTPException(status_code=404, detail="No hay ninguna sesión activa.")

    activity = _current_activity(session)
    activity_key = activity["key"] if activity else None
    mapping: dict[str, tuple[str, bool | None, dict[str, Any]]] = {
        "adequate": ("user_response", True, {"rating": "adequate"}),
        "partial": ("user_response", None, {"rating": "partial"}),
        "incorrect": ("user_response", False, {"rating": "incorrect"}),
        "no_response": ("silence_detected", None, {"rating": "no_response"}),
        "hint": ("hint_given", None, {"support": "hint"}),
        "repeat": ("instruction_repeated", None, {"support": "repeat"}),
        "example": ("example_given", None, {"support": "example"}),
    }
    event_type, success, metadata = mapping[payload.action]
    event = models.SessionEvent(
        session_id=session.id,
        event_type=event_type,
        source="panel",
        activity=activity_key,
        value_text=payload.note.strip() if payload.note else None,
        success=success,
        metadata_json=json.dumps(metadata, ensure_ascii=False),
    )
    db.add(event)
    db.commit()
    db.refresh(session)
    return {
        "registered": True,
        "event_id": event.id,
        "action": payload.action,
        "summary": _panel_summary(session),
    }


@router.get("/panel/api/session/summary")
def get_panel_session_summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    session = _active_session(db)
    if session is None:
        latest = db.scalar(
            select(models.SessionRecord).order_by(models.SessionRecord.id.desc())
        )
        if latest is None:
            raise HTTPException(status_code=404, detail="No existen sesiones.")
        session = latest
    return _panel_summary(session)


@router.post("/panel/api/session/finish")
def finish_panel_session(
    payload: PanelFinishRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    session = _active_session(db)
    if session is None:
        raise HTTPException(status_code=404, detail="No hay ninguna sesión activa.")

    activity = _current_activity(session)
    activity_key = activity["key"] if activity else None
    db.add(
        models.SessionEvent(
            session_id=session.id,
            event_type="activity_completed",
            source="panel",
            activity=activity_key,
            value_text="Actividad finalizada desde el panel profesional.",
            metadata_json=json.dumps(
                {"level": activity.get("level") if activity else None},
                ensure_ascii=False,
            ),
        )
    )
    db.add(
        models.SessionEvent(
            session_id=session.id,
            event_type="professional_decision",
            source="panel",
            activity=activity_key,
            value_text=payload.note.strip() if payload.note else None,
            metadata_json=json.dumps(
                {"decision": payload.decision},
                ensure_ascii=False,
            ),
        )
    )
    session.status = "finished"
    session.finished_at = datetime.utcnow()
    db.flush()

    summary = _panel_summary(session)
    session.summary = payload.note.strip() if payload.note else (
        f"Actividad {activity_key or 'sin actividad'}; "
        f"adecuadas={summary['counts']['adequate']}; "
        f"parciales={summary['counts']['partial']}; "
        f"incorrectas={summary['counts']['incorrect']}; "
        f"sin respuesta={summary['counts']['no_response']}; "
        f"pistas={summary['counts']['hint']}; "
        f"decisión={payload.decision}."
    )
    db.add(
        models.SessionEvent(
            session_id=session.id,
            event_type="session_finished",
            source="panel",
            value_text=session.summary,
        )
    )
    db.commit()
    db.refresh(session)

    result = _panel_summary(session)
    try:
        session_preparation_service.finalize_session_files(
            session.id,
            finished_at=session.finished_at,
            decision=payload.decision,
            summary=result,
        )
        result = _panel_summary(session)
    except Exception as exc:
        result["file_warning"] = str(exc)

    return result
