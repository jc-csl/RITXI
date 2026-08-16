from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    external_id: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=120)
    preferred_name: str | None = Field(default=None, max_length=120)
    language: str = Field(default="es", min_length=2, max_length=10)
    notes: str | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: str
    name: str
    preferred_name: str | None
    language: str
    notes: str | None
    active: bool
    created_at: datetime


class ProfileUpsert(BaseModel):
    communication_style: Literal["simple", "standard"] = "simple"
    speech_speed: Literal["slow", "normal", "fast"] = "normal"
    response_wait_seconds: float = Field(default=5.0, ge=1.0, le=30.0)
    preferred_interaction_mode: Literal["voice", "touch", "mixed"] = "mixed"
    preferred_reinforcement: str | None = Field(default=None, max_length=200)
    interests: str | None = None
    avoid_topics: str | None = None
    accessibility_notes: str | None = None
    max_instructions_per_turn: int = Field(default=1, ge=1, le=5)


class ProfileRead(ProfileUpsert):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    updated_at: datetime


class SessionStart(BaseModel):
    user_external_id: str = Field(min_length=1, max_length=50)
    started_by: str = Field(default="professional", min_length=1, max_length=120)


class SessionFinish(BaseModel):
    summary: str | None = None


class SessionRead(BaseModel):
    id: int
    user_external_id: str
    user_name: str
    language: str
    started_by: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    summary: str | None


class SessionContext(BaseModel):
    id: int
    started_at: datetime
    started_by: str
    status: str


class UserContext(BaseModel):
    id: int
    external_id: str
    name: str
    preferred_name: str
    language: str
    notes: str | None
    active: bool


class ProfileContext(BaseModel):
    communication_style: str
    speech_speed: str
    response_wait_seconds: float
    preferred_interaction_mode: str
    preferred_reinforcement: str | None
    interests: str | None
    avoid_topics: str | None
    accessibility_notes: str | None
    max_instructions_per_turn: int


class ConversationContext(BaseModel):
    current_activity: str | None = None
    current_goal: str | None = None
    current_step: str | None = None


class MemoryContext(BaseModel):
    id: int
    category: str
    content: str
    importance: int


class ActiveContext(BaseModel):
    session: SessionContext
    user: UserContext
    profile: ProfileContext
    memory: list[MemoryContext]
    conversation: ConversationContext


class EventCreate(BaseModel):
    event_type: Literal[
        "session_started",
        "activity_started",
        "robot_message",
        "user_response",
        "hint_given",
        "silence_detected",
        "error_detected",
        "activity_completed",
        "session_finished",
        "technical_metric",
    ]
    source: Literal["conversation_app", "panel", "robot", "system"] = "conversation_app"
    activity: str | None = Field(default=None, max_length=120)
    value_text: str | None = None
    value_number: float | None = None
    success: bool | None = None
    metadata: dict | None = None


class EventRead(BaseModel):
    id: int
    session_id: int
    event_type: str
    source: str
    activity: str | None
    value_text: str | None
    value_number: float | None
    success: bool | None
    metadata: dict | None
    occurred_at: datetime


class ActivitySummary(BaseModel):
    activity: str
    starts: int
    completions: int
    responses: int
    correct_responses: int
    incorrect_responses: int
    hints: int
    silences: int
    errors: int
    average_response_time_seconds: float | None
    completed_successfully: bool | None


class SessionSummary(BaseModel):
    session_id: int
    user_external_id: str
    user_name: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    duration_seconds: float
    duration_minutes: float
    total_events: int
    activities_started: int
    activities_completed: int
    user_responses: int
    correct_responses: int
    incorrect_responses: int
    unanswered_responses: int
    success_rate_percent: float | None
    hints_given: int
    silences_detected: int
    errors_detected: int
    average_response_time_seconds: float | None
    activities: list[ActivitySummary]
    automatic_observations: list[str]
    automatic_summary_text: str


class MemoryCreate(BaseModel):
    category: Literal[
        "preference",
        "person",
        "interest",
        "routine",
        "achievement",
        "support",
        "avoid",
        "other",
    ] = "other"
    content: str = Field(min_length=1, max_length=1000)
    source: Literal["manual", "session", "system"] = "manual"
    importance: int = Field(default=3, ge=1, le=5)


class MemoryUpdate(BaseModel):
    category: Literal[
        "preference",
        "person",
        "interest",
        "routine",
        "achievement",
        "support",
        "avoid",
        "other",
    ] | None = None
    content: str | None = Field(default=None, min_length=1, max_length=1000)
    source: Literal["manual", "session", "system"] | None = None
    importance: int | None = Field(default=None, ge=1, le=5)
    active: bool | None = None


class MemoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    category: str
    content: str
    source: str
    importance: int
    active: bool
    created_at: datetime
    updated_at: datetime
