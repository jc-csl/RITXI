from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any, Literal
import unicodedata

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .database import get_db
from .panel_session_completion import panel_session_completion_service
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


class PanelUserCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    preferred_name: str | None = Field(default=None, max_length=120)
    external_id: str | None = Field(default=None, max_length=50)
    language: str = Field(default="es", min_length=2, max_length=10)
    notes: str | None = Field(default=None, max_length=4000)


class PanelUserUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    preferred_name: str | None = Field(default=None, max_length=120)
    external_id: str | None = Field(default=None, max_length=50)
    language: str | None = Field(default=None, min_length=2, max_length=10)
    notes: str | None = Field(default=None, max_length=4000)


class PanelProfileUpdateRequest(BaseModel):
    communication_style: Literal["simple", "standard"] | None = None
    speech_speed: Literal["slow", "normal", "fast"] | None = None
    response_wait_seconds: float | None = Field(default=None, ge=1.0, le=30.0)
    preferred_interaction_mode: Literal["voice", "touch", "mixed"] | None = None
    preferred_reinforcement: str | None = Field(default=None, max_length=200)
    interests: str | None = Field(default=None, max_length=4000)
    avoid_topics: str | None = Field(default=None, max_length=4000)
    accessibility_notes: str | None = Field(default=None, max_length=4000)
    max_instructions_per_turn: int | None = Field(default=None, ge=1, le=5)


class ExampleUserRequest(BaseModel):
    external_id: str = Field(default="ALEX-EJEMPLO", min_length=1, max_length=50)
    name: str = Field(default="Álex", min_length=1, max_length=120)


class PanelTranscriptEventRequest(BaseModel):
    event_type: Literal["user_response", "robot_message"]
    source: Literal["conversation_app"]
    activity: str | None = Field(default=None, max_length=120)
    value_text: str = Field(min_length=1, max_length=20000)
    success: bool | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


REPORT_FILES = {
    "pdf": ("informe_sesion.pdf", "application/pdf"),
    "html": ("informe_sesion.html", "text/html"),
    "json": ("informe_sesion.json", "application/json"),
    "transcript": ("transcripcion_sesion.txt", "text/plain"),
}


def _panel_response() -> FileResponse:
    return FileResponse(
        PANEL_STATIC_DIR / "panel_inline_12_7_2.html",
        media_type="text/html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@router.get("/panel", include_in_schema=False)
def panel_page() -> FileResponse:
    return _panel_response()


@router.get("/panel-12-7-2", include_in_schema=False)
def panel_page_12_7_2() -> FileResponse:
    return _panel_response()


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


def _ensure_profile(user: models.User, db: Session) -> models.UserProfile:
    if user.profile is None:
        user.profile = models.UserProfile()
        db.flush()
    return user.profile


def _profile_dict(profile: models.UserProfile | None) -> dict[str, Any]:
    if profile is None:
        return {
            "communication_style": "simple",
            "speech_speed": "normal",
            "response_wait_seconds": 5.0,
            "preferred_interaction_mode": "mixed",
            "preferred_reinforcement": None,
            "interests": None,
            "avoid_topics": None,
            "accessibility_notes": None,
            "max_instructions_per_turn": 1,
        }

    return {
        "communication_style": profile.communication_style,
        "speech_speed": profile.speech_speed,
        "response_wait_seconds": profile.response_wait_seconds,
        "preferred_interaction_mode": profile.preferred_interaction_mode,
        "preferred_reinforcement": profile.preferred_reinforcement,
        "interests": profile.interests,
        "avoid_topics": profile.avoid_topics,
        "accessibility_notes": profile.accessibility_notes,
        "max_instructions_per_turn": profile.max_instructions_per_turn,
    }


def _user_dict(user: models.User) -> dict[str, Any]:
    return {
        "external_id": user.external_id,
        "name": user.name,
        "preferred_name": user.preferred_name or user.name,
        "language": user.language,
        "notes": user.notes,
        "active": user.active,
        "profile": _profile_dict(user.profile),
    }


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
        "finished_at": (
            session.finished_at.isoformat()
            if session.finished_at
            else None
        ),
        **timing,
        "counts": counts,
        "evaluated_responses": evaluated,
        "professional_decision": decision,
        "summary": session.summary,
    }


def _normalize_external_id(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", ascii_value.upper()).strip("-")
    return cleaned[:50]


def _unique_external_id(
    *,
    db: Session,
    requested: str | None,
    name: str,
    excluded_user_id: int | None = None,
) -> str:
    if requested and requested.strip():
        base = _normalize_external_id(requested)
        if not base:
            raise HTTPException(
                status_code=422,
                detail="El identificador no contiene caracteres válidos.",
            )
    else:
        base = _normalize_external_id(name) or "USUARIO"

    candidate = base
    suffix = 2

    while True:
        existing = db.scalar(
            select(models.User).where(models.User.external_id == candidate)
        )
        if existing is None or existing.id == excluded_user_id:
            return candidate

        if requested and requested.strip():
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe una persona con identificador {candidate}.",
            )

        suffix_text = f"-{suffix}"
        candidate = base[: 50 - len(suffix_text)] + suffix_text
        suffix += 1


def _get_user_or_404(external_id: str, db: Session) -> models.User:
    user = db.scalar(
        select(models.User).where(models.User.external_id == external_id)
    )
    if user is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada.")
    return user


def _stale_state() -> dict[str, Any]:
    config = session_preparation_service.load_config()
    active_file = config["active_session_file"]
    app_running = session_preparation_service.service_reachable(
        config["conversation_app_host"],
        config["conversation_app_port"],
    )

    return {
        "active_session_file_exists": active_file.is_file(),
        "conversation_app_running": app_running,
    }


def _clean_stale_files_when_safe(db: Session) -> dict[str, Any]:
    active = _active_session(db)
    state = _stale_state()

    if active is not None or state["conversation_app_running"]:
        return {
            "cleaned": False,
            **state,
        }

    config = session_preparation_service.load_config()
    removed = config["active_session_file"].is_file()
    config["active_session_file"].unlink(missing_ok=True)

    try:
        session_preparation_service.reset_active_profile()
        profile_reset = True
    except Exception:
        profile_reset = False

    return {
        "cleaned": removed or profile_reset,
        "removed_active_file": removed,
        "profile_reset": profile_reset,
        **_stale_state(),
    }


@router.get("/panel/api/bootstrap")
def panel_bootstrap(db: Session = Depends(get_db)) -> dict[str, Any]:
    _clean_stale_files_when_safe(db)

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

    services = session_preparation_service.service_status()
    stale = _stale_state()

    return {
        "version": "0.12.8.3",
        "users": [_user_dict(user) for user in users],
        "activities": session_preparation_service.list_activities(),
        "services": services,
        "active_session": active_summary,
        "blocking_state": {
            **stale,
            "database_active_session": active.id if active else None,
            "can_prepare": (
                active is None
                and not services["conversation_app"]["running"]
            ),
        },
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


@router.get("/panel/api/users/{external_id}")
def get_panel_user(
    external_id: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return _user_dict(_get_user_or_404(external_id, db))


@router.post("/panel/api/users", status_code=201)
def create_panel_user(
    payload: PanelUserCreateRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    name = payload.name.strip()
    preferred_name = (
        payload.preferred_name.strip()
        if payload.preferred_name and payload.preferred_name.strip()
        else name
    )
    external_id = _unique_external_id(
        db=db,
        requested=payload.external_id,
        name=name,
    )

    user = models.User(
        external_id=external_id,
        name=name,
        preferred_name=preferred_name,
        language=payload.language.strip().lower() or "es",
        notes=payload.notes.strip() if payload.notes else None,
        active=True,
    )
    user.profile = models.UserProfile(
        communication_style="simple",
        speech_speed="normal",
        response_wait_seconds=5.0,
        preferred_interaction_mode="mixed",
        preferred_reinforcement="refuerzo verbal positivo",
        max_instructions_per_turn=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "created": True,
        "user": _user_dict(user),
    }


@router.put("/panel/api/users/{external_id}")
def update_panel_user(
    external_id: str,
    payload: PanelUserUpdateRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    user = _get_user_or_404(external_id, db)
    values = payload.model_dump(exclude_unset=True)

    if "external_id" in values:
        requested = values.pop("external_id")
        if requested is not None and requested.strip():
            user.external_id = _unique_external_id(
                db=db,
                requested=requested,
                name=user.name,
                excluded_user_id=user.id,
            )

    if "name" in values:
        name = values["name"]
        if name is None or not name.strip():
            raise HTTPException(
                status_code=422,
                detail="El nombre no puede quedar vacío.",
            )
        user.name = name.strip()

    if "preferred_name" in values:
        preferred = values["preferred_name"]
        user.preferred_name = (
            preferred.strip()
            if preferred and preferred.strip()
            else user.name
        )

    if "language" in values:
        language = values["language"]
        if language is None or not language.strip():
            raise HTTPException(
                status_code=422,
                detail="El idioma no puede quedar vacío.",
            )
        user.language = language.strip().lower()

    if "notes" in values:
        notes = values["notes"]
        user.notes = notes.strip() if notes and notes.strip() else None

    db.commit()
    db.refresh(user)

    return {
        "updated": True,
        "user": _user_dict(user),
    }


@router.put("/panel/api/users/{external_id}/profile")
def update_panel_profile(
    external_id: str,
    payload: PanelProfileUpdateRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    user = _get_user_or_404(external_id, db)
    profile = _ensure_profile(user, db)
    values = payload.model_dump(exclude_unset=True)

    nullable_text_fields = {
        "preferred_reinforcement",
        "interests",
        "avoid_topics",
        "accessibility_notes",
    }

    for field, value in values.items():
        if field in nullable_text_fields:
            value = value.strip() if value and value.strip() else None
        if value is not None or field in nullable_text_fields:
            setattr(profile, field, value)

    db.commit()
    db.refresh(user)

    return {
        "updated": True,
        "user": _user_dict(user),
    }


@router.delete("/panel/api/users/{external_id}")
def delete_panel_user(
    external_id: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    user = _get_user_or_404(external_id, db)

    active = _active_session(db)
    if active is not None and active.user_id == user.id:
        raise HTTPException(
            status_code=409,
            detail="No se puede borrar la persona de una sesión activa.",
        )

    has_sessions = bool(user.sessions)

    if has_sessions:
        user.active = False
        db.commit()
        return {
            "deleted": False,
            "deactivated": True,
            "message": (
                "La persona se ha ocultado, pero se conservan sus sesiones "
                "e informes."
            ),
        }

    db.delete(user)
    db.commit()
    return {
        "deleted": True,
        "deactivated": False,
        "message": "La persona y su ficha se han eliminado.",
    }


@router.post("/panel/api/example-user", status_code=201)
def create_example_user(
    payload: ExampleUserRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    existing = db.scalar(
        select(models.User).where(
            models.User.external_id == payload.external_id
        )
    )

    if existing is not None:
        if not existing.active:
            existing.active = True
            db.commit()
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
        notes="Usuario de ejemplo creado desde el panel.",
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
    _clean_stale_files_when_safe(db)

    user = db.scalar(
        select(models.User).where(
            models.User.external_id == payload.user_external_id,
            models.User.active.is_(True),
        )
    )
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado o inactivo.",
        )

    try:
        return session_preparation_service.prepare_session(
            db=db,
            user=user,
            activity_key=payload.activity,
            level=payload.level,
            started_by=payload.started_by,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail="Actividad no encontrada.",
        ) from exc
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
def launch_conversation_app(
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    session = _active_session(db)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail="No hay sesión preparada.",
        )

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
        raise HTTPException(
            status_code=404,
            detail="No hay ninguna sesión activa.",
        )

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


@router.post(
    "/panel/api/sessions/{session_id}/conversation-events",
    status_code=201,
)
def import_final_conversation_event(
    session_id: int,
    payload: PanelTranscriptEventRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    session = db.get(models.SessionRecord, session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada.",
        )

    metadata = dict(payload.metadata)
    importer = metadata.get("importer")
    import_key = metadata.get("import_key")

    if importer != "ahootsa_session_report_12_6_1":
        raise HTTPException(
            status_code=422,
            detail="Importador de transcripción no autorizado.",
        )

    if not isinstance(import_key, str) or not import_key.strip():
        raise HTTPException(
            status_code=422,
            detail="Falta la clave idempotente de importación.",
        )

    existing_events = list(
        db.scalars(
            select(models.SessionEvent).where(
                models.SessionEvent.session_id == session_id
            )
        ).all()
    )

    for existing in existing_events:
        existing_metadata = _event_metadata(existing)

        if (
            existing_metadata.get("importer") == importer
            and existing_metadata.get("import_key") == import_key
        ):
            return {
                "id": existing.id,
                "created": False,
                "session_status": session.status,
            }

    event = models.SessionEvent(
        session_id=session.id,
        event_type=payload.event_type,
        source=payload.source,
        activity=payload.activity,
        value_text=payload.value_text,
        success=payload.success,
        metadata_json=json.dumps(
            metadata,
            ensure_ascii=False,
        ),
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return {
        "id": event.id,
        "created": True,
        "session_status": session.status,
    }


@router.get("/panel/api/session/summary")
def get_panel_session_summary(
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    session = _active_session(db)

    if session is None:
        session = db.scalar(
            select(models.SessionRecord)
            .order_by(models.SessionRecord.id.desc())
        )

    if session is None:
        raise HTTPException(status_code=404, detail="No existen sesiones.")

    return _panel_summary(session)



@router.post("/panel/api/sessions/{session_id}/finalize-record")
def finalize_session_record_only(
    session_id: int,
    payload: PanelFinishRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    session = db.get(models.SessionRecord, session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada.",
        )

    if session.status != "active":
        return _panel_summary(session)

    activity = _current_activity(session)
    activity_key = activity["key"] if activity else None

    db.add(
        models.SessionEvent(
            session_id=session.id,
            event_type="activity_completed",
            source="panel",
            activity=activity_key,
            value_text=(
                "Actividad finalizada desde el cierre operativo."
            ),
            metadata_json=json.dumps(
                {
                    "level": (
                        activity.get("level")
                        if activity
                        else None
                    ),
                    "record_only": True,
                },
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
            value_text=(
                payload.note.strip()
                if payload.note
                else None
            ),
            metadata_json=json.dumps(
                {
                    "decision": payload.decision,
                    "record_only": True,
                },
                ensure_ascii=False,
            ),
        )
    )

    session.status = "finished"
    session.finished_at = datetime.utcnow()
    db.flush()

    summary = _panel_summary(session)
    session.summary = (
        payload.note.strip()
        if payload.note
        else (
            f"Actividad {activity_key or 'sin actividad'}; "
            f"adecuadas={summary['counts']['adequate']}; "
            f"parciales={summary['counts']['partial']}; "
            f"incorrectas={summary['counts']['incorrect']}; "
            f"sin respuesta={summary['counts']['no_response']}; "
            f"pistas={summary['counts']['hint']}; "
            f"decisión={payload.decision}."
        )
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

    session_preparation_service.finalize_session_files(
        session.id,
        finished_at=session.finished_at,
        decision=payload.decision,
        summary=result,
    )

    return result

def _complete_session(
    *,
    session: models.SessionRecord,
    payload: PanelFinishRequest,
    db: Session,
    recovery: bool,
) -> dict[str, Any]:
    session_id = session.id
    marker = panel_session_completion_service.create_panel_marker(session_id)

    try:
        stop_result = (
            panel_session_completion_service.stop_conversation_app()
        )

        if not stop_result["stopped"]:
            raise HTTPException(
                status_code=409,
                detail=(
                    "No se pudo cerrar la Conversation App. "
                    "Usa Liberar bloqueo y revisa el puerto 7860."
                ),
            )

        paths = session_preparation_service.session_paths(session_id)
        log_state = (
            panel_session_completion_service.wait_for_log_stable(
                paths["log"]
            )
        )

        activity = _current_activity(session)
        activity_key = activity["key"] if activity else None

        db.add(
            models.SessionEvent(
                session_id=session.id,
                event_type="activity_completed",
                source="panel",
                activity=activity_key,
                value_text=(
                    "Actividad recuperada y finalizada desde el panel."
                    if recovery
                    else "Actividad finalizada desde el panel profesional."
                ),
                metadata_json=json.dumps(
                    {
                        "level": (
                            activity.get("level")
                            if activity
                            else None
                        ),
                        "recovery": recovery,
                    },
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
                value_text=(
                    payload.note.strip()
                    if payload.note
                    else None
                ),
                metadata_json=json.dumps(
                    {
                        "decision": payload.decision,
                        "recovery": recovery,
                    },
                    ensure_ascii=False,
                ),
            )
        )

        session.status = "finished"
        session.finished_at = datetime.utcnow()
        db.flush()

        summary = _panel_summary(session)
        session.summary = (
            payload.note.strip()
            if payload.note
            else (
                f"Actividad {activity_key or 'sin actividad'}; "
                f"adecuadas={summary['counts']['adequate']}; "
                f"parciales={summary['counts']['partial']}; "
                f"incorrectas={summary['counts']['incorrect']}; "
                f"sin respuesta={summary['counts']['no_response']}; "
                f"pistas={summary['counts']['hint']}; "
                f"decisión={payload.decision}."
            )
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
        except Exception as exc:
            result["file_warning"] = str(exc)

        report_result = (
            panel_session_completion_service.generate_report(session_id)
        )
        result["stop"] = stop_result
        result["log"] = log_state
        result["report"] = report_result
        result["recovery"] = recovery
        return result

    finally:
        marker.unlink(missing_ok=True)


@router.post("/panel/api/session/finish")
def finish_panel_session(
    payload: PanelFinishRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    session = _active_session(db)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="No hay ninguna sesión activa.",
        )

    return _complete_session(
        session=session,
        payload=payload,
        db=db,
        recovery=False,
    )


@router.post("/panel/api/session/recover")
def recover_panel_session(
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    session = _active_session(db)

    if session is not None:
        return _complete_session(
            session=session,
            payload=PanelFinishRequest(
                note=(
                    "Sesión cerrada mediante la recuperación del panel."
                ),
                decision="no_decision",
            ),
            db=db,
            recovery=True,
        )

    stop_result = panel_session_completion_service.stop_conversation_app()
    config = session_preparation_service.load_config()
    config["active_session_file"].unlink(missing_ok=True)

    try:
        session_preparation_service.reset_active_profile()
        profile_reset = True
    except Exception as exc:
        profile_reset = False
        reset_warning = str(exc)
    else:
        reset_warning = None

    return {
        "recovered": True,
        "active_session": False,
        "stop": stop_result,
        "profile_reset": profile_reset,
        "reset_warning": reset_warning,
    }


@router.get("/panel/api/sessions/{session_id}/report/{report_type}")
def download_session_report(
    session_id: int,
    report_type: str,
) -> FileResponse:
    definition = REPORT_FILES.get(report_type)

    if definition is None:
        raise HTTPException(
            status_code=404,
            detail="Formato de informe no reconocido.",
        )

    filename, media_type = definition
    path = (
        session_preparation_service.session_paths(session_id)["session"]
        / filename
    )

    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail="El informe todavía no existe.",
        )

    return FileResponse(
        path,
        media_type=media_type,
        filename=filename,
    )
