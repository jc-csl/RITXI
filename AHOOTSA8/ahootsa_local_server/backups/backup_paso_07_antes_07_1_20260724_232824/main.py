from contextlib import asynccontextmanager
from datetime import datetime
import json
from collections import defaultdict
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models
from .config import DATABASE_PATH
from .database import check_database_connection, get_db, initialize_database
from .schemas import (
    ActiveContext,
    ActivitySummary,
    ConversationContext,
    EventCreate,
    EventRead,
    ProfileContext,
    ProfileRead,
    ProfileUpsert,
    SessionContext,
    SessionFinish,
    SessionRead,
    SessionStart,
    SessionSummary,
    UserContext,
    UserCreate,
    UserRead,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Ahootsa Local Server",
    description="Servidor local independiente para usuarios, perfiles, sesiones, eventos y resúmenes.",
    version="0.7.0",
    lifespan=lifespan,
)


def get_user_or_404(external_id: str, db: Session) -> models.User:
    user = db.scalar(select(models.User).where(models.User.external_id == external_id))
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return user


def ensure_profile(user: models.User, db: Session) -> models.UserProfile:
    if user.profile is None:
        user.profile = models.UserProfile()
        db.commit()
        db.refresh(user)
    return user.profile


def session_to_read(session: models.SessionRecord) -> SessionRead:
    return SessionRead(
        id=session.id,
        user_external_id=session.user.external_id,
        user_name=session.user.name,
        language=session.user.language,
        started_by=session.started_by,
        status=session.status,
        started_at=session.started_at,
        finished_at=session.finished_at,
        summary=session.summary,
    )


def event_to_read(event: models.SessionEvent) -> EventRead:
    metadata = json.loads(event.metadata_json) if event.metadata_json else None
    return EventRead(
        id=event.id,
        session_id=event.session_id,
        event_type=event.event_type,
        source=event.source,
        activity=event.activity,
        value_text=event.value_text,
        value_number=event.value_number,
        success=event.success,
        metadata=metadata,
        occurred_at=event.occurred_at,
    )


def parse_metadata(event: models.SessionEvent) -> dict[str, Any]:
    if not event.metadata_json:
        return {}
    try:
        value = json.loads(event.metadata_json)
        return value if isinstance(value, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def get_response_time(event: models.SessionEvent) -> float | None:
    metadata = parse_metadata(event)
    value = metadata.get("response_time_seconds")
    if isinstance(value, (int, float)) and value >= 0:
        return float(value)
    return None


def build_session_summary(
    session: models.SessionRecord,
    events: list[models.SessionEvent],
) -> SessionSummary:
    effective_end = session.finished_at or datetime.utcnow()
    duration_seconds = max((effective_end - session.started_at).total_seconds(), 0.0)

    total_responses = 0
    correct = 0
    incorrect = 0
    unanswered = 0
    hints = 0
    silences = 0
    errors = 0
    activities_started = 0
    activities_completed = 0
    response_times: list[float] = []

    activity_data: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "starts": 0,
            "completions": 0,
            "responses": 0,
            "correct": 0,
            "incorrect": 0,
            "hints": 0,
            "silences": 0,
            "errors": 0,
            "response_times": [],
            "completion_success_values": [],
        }
    )

    for event in events:
        activity_name = event.activity or "sin_actividad"
        data = activity_data[activity_name]

        if event.event_type == "activity_started":
            activities_started += 1
            data["starts"] += 1

        elif event.event_type == "activity_completed":
            activities_completed += 1
            data["completions"] += 1
            if event.success is not None:
                data["completion_success_values"].append(event.success)

        elif event.event_type == "user_response":
            total_responses += 1
            data["responses"] += 1

            if event.success is True:
                correct += 1
                data["correct"] += 1
            elif event.success is False:
                incorrect += 1
                data["incorrect"] += 1
            else:
                unanswered += 1

            response_time = get_response_time(event)
            if response_time is not None:
                response_times.append(response_time)
                data["response_times"].append(response_time)

        elif event.event_type == "hint_given":
            hints += 1
            data["hints"] += 1

        elif event.event_type == "silence_detected":
            silences += 1
            data["silences"] += 1

        elif event.event_type == "error_detected":
            errors += 1
            data["errors"] += 1

    evaluated_responses = correct + incorrect
    success_rate = (
        round((correct / evaluated_responses) * 100, 1)
        if evaluated_responses > 0
        else None
    )
    average_response_time = (
        round(sum(response_times) / len(response_times), 2)
        if response_times
        else None
    )

    activity_summaries: list[ActivitySummary] = []
    for activity_name, data in sorted(activity_data.items()):
        completion_values = data["completion_success_values"]
        completed_successfully = (
            all(completion_values) if completion_values else None
        )
        activity_average = (
            round(sum(data["response_times"]) / len(data["response_times"]), 2)
            if data["response_times"]
            else None
        )

        activity_summaries.append(
            ActivitySummary(
                activity=activity_name,
                starts=data["starts"],
                completions=data["completions"],
                responses=data["responses"],
                correct_responses=data["correct"],
                incorrect_responses=data["incorrect"],
                hints=data["hints"],
                silences=data["silences"],
                errors=data["errors"],
                average_response_time_seconds=activity_average,
                completed_successfully=completed_successfully,
            )
        )

    observations: list[str] = []

    if total_responses == 0:
        observations.append("No se registraron respuestas del usuario.")
    elif success_rate is not None and success_rate >= 80:
        observations.append("La mayoría de las respuestas evaluadas fueron correctas.")
    elif success_rate is not None and success_rate < 50:
        observations.append("Conviene revisar la dificultad o repetir la actividad.")

    if hints > 0:
        observations.append(f"Se ofrecieron {hints} pista(s) durante la sesión.")

    if silences > 0:
        observations.append(f"Se detectaron {silences} silencio(s) prolongado(s).")

    if errors > 0:
        observations.append(f"Se registraron {errors} error(es) durante la interacción.")

    if activities_started > activities_completed:
        observations.append("Hay actividades iniciadas que no constan como finalizadas.")

    if average_response_time is not None:
        if average_response_time > 10:
            observations.append("El tiempo medio de respuesta fue elevado.")
        elif average_response_time <= 5:
            observations.append("El tiempo medio de respuesta fue ágil.")

    if not observations:
        observations.append("La sesión se desarrolló sin incidencias destacables.")

    lines = [
        f"Usuario: {session.user.preferred_name or session.user.name}",
        f"Duración: {round(duration_seconds / 60, 1)} minutos",
        f"Actividades iniciadas: {activities_started}",
        f"Actividades completadas: {activities_completed}",
        f"Respuestas registradas: {total_responses}",
        f"Respuestas correctas: {correct}",
        f"Respuestas incorrectas: {incorrect}",
    ]

    if success_rate is not None:
        lines.append(f"Porcentaje de acierto: {success_rate}%")

    if average_response_time is not None:
        lines.append(f"Tiempo medio de respuesta: {average_response_time} segundos")

    lines.append("Observaciones:")
    lines.extend(f"- {observation}" for observation in observations)

    return SessionSummary(
        session_id=session.id,
        user_external_id=session.user.external_id,
        user_name=session.user.preferred_name or session.user.name,
        status=session.status,
        started_at=session.started_at,
        finished_at=session.finished_at,
        duration_seconds=round(duration_seconds, 2),
        duration_minutes=round(duration_seconds / 60, 2),
        total_events=len(events),
        activities_started=activities_started,
        activities_completed=activities_completed,
        user_responses=total_responses,
        correct_responses=correct,
        incorrect_responses=incorrect,
        unanswered_responses=unanswered,
        success_rate_percent=success_rate,
        hints_given=hints,
        silences_detected=silences,
        errors_detected=errors,
        average_response_time_seconds=average_response_time,
        activities=activity_summaries,
        automatic_observations=observations,
        automatic_summary_text="\n".join(lines),
    )


def get_session_events(session_id: int, db: Session) -> list[models.SessionEvent]:
    return list(
        db.scalars(
            select(models.SessionEvent)
            .where(models.SessionEvent.session_id == session_id)
            .order_by(models.SessionEvent.occurred_at)
        ).all()
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "ahootsa-local-server",
        "version": "0.7.0",
    }


@app.get("/health/database")
def database_health_check() -> dict[str, str | bool]:
    connected = check_database_connection()
    return {
        "status": "ok" if connected else "error",
        "database": "sqlite",
        "connected": connected,
        "path": str(DATABASE_PATH),
    }


@app.post("/users", response_model=UserRead, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> models.User:
    user = models.User(
        external_id=payload.external_id.strip(),
        name=payload.name.strip(),
        preferred_name=payload.preferred_name.strip() if payload.preferred_name else None,
        language=payload.language.strip().lower(),
        notes=payload.notes,
    )
    user.profile = models.UserProfile()
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ya existe un usuario con ese external_id.",
        ) from exc
    db.refresh(user)
    return user


@app.get("/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)) -> list[models.User]:
    return list(db.scalars(select(models.User).order_by(models.User.name)).all())


@app.put("/users/{external_id}/profile", response_model=ProfileRead)
def upsert_profile(
    external_id: str,
    payload: ProfileUpsert,
    db: Session = Depends(get_db),
):
    user = get_user_or_404(external_id, db)
    profile = ensure_profile(user, db)

    for field, value in payload.model_dump().items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


@app.post("/sessions/start", response_model=SessionRead, status_code=201)
def start_session(payload: SessionStart, db: Session = Depends(get_db)) -> SessionRead:
    active = db.scalar(
        select(models.SessionRecord).where(models.SessionRecord.status == "active")
    )
    if active is not None:
        raise HTTPException(status_code=409, detail="Ya existe una sesión activa.")

    user = db.scalar(
        select(models.User).where(
            models.User.external_id == payload.user_external_id,
            models.User.active.is_(True),
        )
    )
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado o desactivado.",
        )

    ensure_profile(user, db)

    session = models.SessionRecord(
        user_id=user.id,
        started_by=payload.started_by.strip(),
        status="active",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    db.add(
        models.SessionEvent(
            session_id=session.id,
            event_type="session_started",
            source="panel",
            value_text=f"Sesión iniciada por {payload.started_by.strip()}",
        )
    )
    db.commit()

    return session_to_read(session)


@app.get("/sessions/active", response_model=SessionRead)
def get_active_session(db: Session = Depends(get_db)) -> SessionRead:
    session = db.scalar(
        select(models.SessionRecord).where(models.SessionRecord.status == "active")
    )
    if session is None:
        raise HTTPException(status_code=404, detail="No hay ninguna sesión activa.")
    return session_to_read(session)


@app.get("/sessions/active/context", response_model=ActiveContext)
def get_active_context(db: Session = Depends(get_db)) -> ActiveContext:
    session = db.scalar(
        select(models.SessionRecord).where(models.SessionRecord.status == "active")
    )
    if session is None:
        raise HTTPException(status_code=404, detail="No hay ninguna sesión activa.")

    user = session.user
    profile = ensure_profile(user, db)

    latest_activity_event = db.scalar(
        select(models.SessionEvent)
        .where(
            models.SessionEvent.session_id == session.id,
            models.SessionEvent.event_type == "activity_started",
        )
        .order_by(models.SessionEvent.occurred_at.desc())
    )

    return ActiveContext(
        session=SessionContext(
            id=session.id,
            started_at=session.started_at,
            started_by=session.started_by,
            status=session.status,
        ),
        user=UserContext(
            id=user.id,
            external_id=user.external_id,
            name=user.name,
            preferred_name=user.preferred_name or user.name,
            language=user.language,
            notes=user.notes,
            active=user.active,
        ),
        profile=ProfileContext(
            communication_style=profile.communication_style,
            speech_speed=profile.speech_speed,
            response_wait_seconds=profile.response_wait_seconds,
            preferred_interaction_mode=profile.preferred_interaction_mode,
            preferred_reinforcement=profile.preferred_reinforcement,
            interests=profile.interests,
            avoid_topics=profile.avoid_topics,
            accessibility_notes=profile.accessibility_notes,
            max_instructions_per_turn=profile.max_instructions_per_turn,
        ),
        conversation=ConversationContext(
            current_activity=latest_activity_event.activity
            if latest_activity_event
            else None,
            current_goal=None,
            current_step=None,
        ),
    )


@app.post("/sessions/{session_id}/events", response_model=EventRead, status_code=201)
def create_event(
    session_id: int,
    payload: EventCreate,
    db: Session = Depends(get_db),
) -> EventRead:
    session = db.get(models.SessionRecord, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")

    if session.status != "active":
        raise HTTPException(
            status_code=409,
            detail="No se pueden añadir eventos a una sesión finalizada.",
        )

    event = models.SessionEvent(
        session_id=session_id,
        event_type=payload.event_type,
        source=payload.source,
        activity=payload.activity,
        value_text=payload.value_text,
        value_number=payload.value_number,
        success=payload.success,
        metadata_json=(
            json.dumps(payload.metadata, ensure_ascii=False)
            if payload.metadata
            else None
        ),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event_to_read(event)


@app.post("/sessions/active/events", response_model=EventRead, status_code=201)
def create_event_for_active_session(
    payload: EventCreate,
    db: Session = Depends(get_db),
) -> EventRead:
    session = db.scalar(
        select(models.SessionRecord).where(models.SessionRecord.status == "active")
    )
    if session is None:
        raise HTTPException(status_code=404, detail="No hay ninguna sesión activa.")
    return create_event(session.id, payload, db)


@app.get("/sessions/{session_id}/events", response_model=list[EventRead])
def list_session_events(
    session_id: int,
    db: Session = Depends(get_db),
) -> list[EventRead]:
    session = db.get(models.SessionRecord, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")

    return [event_to_read(event) for event in get_session_events(session_id, db)]


@app.get("/sessions/{session_id}/summary", response_model=SessionSummary)
def get_session_summary(
    session_id: int,
    db: Session = Depends(get_db),
) -> SessionSummary:
    session = db.get(models.SessionRecord, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")

    events = get_session_events(session_id, db)
    return build_session_summary(session, events)


@app.get("/sessions/active/summary", response_model=SessionSummary)
def get_active_session_summary(db: Session = Depends(get_db)) -> SessionSummary:
    session = db.scalar(
        select(models.SessionRecord).where(models.SessionRecord.status == "active")
    )
    if session is None:
        raise HTTPException(status_code=404, detail="No hay ninguna sesión activa.")

    events = get_session_events(session.id, db)
    return build_session_summary(session, events)


@app.post("/sessions/{session_id}/finish", response_model=SessionRead)
def finish_session(
    session_id: int,
    payload: SessionFinish,
    db: Session = Depends(get_db),
) -> SessionRead:
    session = db.get(models.SessionRecord, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")

    if session.status != "active":
        raise HTTPException(status_code=409, detail="La sesión ya está finalizada.")

    session.status = "finished"
    session.finished_at = datetime.utcnow()

    db.add(
        models.SessionEvent(
            session_id=session.id,
            event_type="session_finished",
            source="panel",
            value_text=payload.summary,
        )
    )
    db.flush()

    events = get_session_events(session.id, db)
    automatic_summary = build_session_summary(session, events)

    session.summary = (
        payload.summary.strip()
        if payload.summary and payload.summary.strip()
        else automatic_summary.automatic_summary_text
    )

    db.commit()
    db.refresh(session)
    return session_to_read(session)
