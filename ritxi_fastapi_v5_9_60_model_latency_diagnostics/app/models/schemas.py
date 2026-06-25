from __future__ import annotations

from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

Emotion = str


ActionLayer = Literal["speech", "emotion", "idle", "manual"]


class FeatureFlags(BaseModel):
    # Entrada / salida principales
    input_microphone: bool = True
    output_text: bool = True
    output_audio: bool = True

    # Módulos que pueden aislarse para pruebas
    stt: bool = True
    llm: bool = True
    tts: bool = True
    robot_motion: bool = True
    camera_vision: bool = False

    # Sincronización / comportamiento
    process_emotions: bool = True
    streaming: bool = True
    synchronize_turn: bool = True
    debug: bool = True
    speech_motion: bool = True
    active_wait: bool = False
    move_talk_generate_text: bool = True
    auto_voice_response: bool = True
    auto_send_after_stt: bool = True
    echo_guard: bool = True
    mode_tutor_di: bool = True

    # Diagnóstico / sesión
    detailed_logs: bool = True
    save_session: bool = True
    simulation_mode: bool = True


class ChatRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    session_id: str = Field(default="demo", min_length=1, max_length=80)
    flags: FeatureFlags = Field(default_factory=FeatureFlags)
    llm_model: str | None = Field(default=None, max_length=80)
    model_preset: str | None = Field(default=None, max_length=40)


class LatencyMetrics(BaseModel):
    stt_ms: float = 0.0
    llm_first_token_ms: float | None = None
    llm_total_ms: float = 0.0
    tts_first_enqueue_ms: float | None = None
    output_total_ms: float = 0.0
    turn_total_ms: float = 0.0


class ChatResponse(BaseModel):
    session_id: str
    text: str
    raw_llm_text: str | None = None
    emotion: Emotion = "neutral"
    action_ids: list[str] = Field(default_factory=list)
    action_queued: bool = False
    action_completed: bool = False
    queue_size: int = 0
    provider: str
    model: str
    character_id: str
    streaming_used: bool = False
    microphone_enabled: bool = True
    turn_state: str = "idle"
    latencies: LatencyMetrics = Field(default_factory=LatencyMetrics)
    warnings: list[str] = Field(default_factory=list)


class ManualActionRequest(BaseModel):
    emotion: Emotion = "neutral"
    text: str | None = Field(default=None, max_length=500)
    audio_enabled: bool = False
    motion_enabled: bool = True
    return_to_neutral: bool = True
    layer: ActionLayer = "manual"
    wait: bool = False
    speech_motion: bool = True


class ManualActionResponse(BaseModel):
    action_id: str
    queued: bool
    completed: bool = False
    queue_size: int
    error: str | None = None
    details: dict[str, object] | None = None


class IdleConfigRequest(BaseModel):
    enabled: bool


class IdleConfigResponse(BaseModel):
    enabled: bool


class QueueStatus(BaseModel):
    queue_size: int
    busy: bool
    idle_enabled: bool
    current_action: str | None = None
    last_action: str | None = None
    last_layer: str | None = None
    speech_motion_enabled: bool = True
    speech_motion_intensity: float = 0.7


class EchoGuardStatus(BaseModel):
    enabled: bool
    microphone_enabled: bool
    speaking: bool
    cooldown_s: float
    reason: str | None = None


class LLMStatus(BaseModel):
    provider: str
    model: str
    available: bool
    streaming_enabled: bool
    base_url: str | None = None


class STTStatus(BaseModel):
    provider: str
    available: bool
    warm: bool
    server_url: str | None = None


class TTSStatus(BaseModel):
    provider: str
    available: bool
    queue_size: int
    speaking: bool


class RobotStatus(BaseModel):
    mode: str
    kind: str
    connected: bool
    host: str
    last_error: str | None = None


class CharacterProfile(BaseModel):
    id: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=120)
    role: str = Field(default="", max_length=600)
    mission: str = Field(default="", max_length=1200)
    tone: str = Field(default="", max_length=1200)
    communication_rules: list[str] = Field(default_factory=list)
    activity_style: list[str] = Field(default_factory=list)
    default_emotion: Emotion = "alegre"
    allowed_emotions: list[str] = Field(default_factory=list)
    movement_style: str = Field(default="", max_length=1000)
    safety_rules: list[str] = Field(default_factory=list)
    prompt_extra: str = Field(default="", max_length=3000)


class CharacterListResponse(BaseModel):
    current_character_id: str
    characters: list[CharacterProfile]


class CharacterSelectRequest(BaseModel):
    character_id: str = Field(min_length=1, max_length=80)


class CharacterUpdateRequest(BaseModel):
    profile: CharacterProfile
    persist: bool = True


class CharacterResponse(BaseModel):
    current: CharacterProfile


class RuntimeSettingsResponse(BaseModel):
    flags_defaults: FeatureFlags
    mode: str
    llm_provider: str
    llm_streaming_enabled: bool
    stt_provider: str
    tts_provider: str
    echo_guard_enabled: bool
    idle_enabled: bool
    speech_motion_enabled: bool
    speech_motion_intensity: float
    current_character: CharacterProfile


class LogStatus(BaseModel):
    session_start: str
    session_log_file: str
    event_log_file: str


class ArchitectureStatus(BaseModel):
    app: str
    version: str
    turn_state: str
    robot: RobotStatus
    llm: LLMStatus
    stt: STTStatus
    tts: TTSStatus
    scheduler: QueueStatus
    echo_guard: EchoGuardStatus
    current_character: CharacterProfile
    last_latencies: LatencyMetrics | None = None
    last_response: str | None = None
    logs: LogStatus
    warnings: list[str] = Field(default_factory=list)


class HealthResponse(ArchitectureStatus):
    pass


class SessionResetResponse(BaseModel):
    session_id: str
    reset: bool


class RobotPoseRequest(BaseModel):
    yaw: float = Field(default=0.0, ge=-180.0, le=180.0)
    pitch: float = Field(default=0.0, ge=-40.0, le=40.0)
    roll: float = Field(default=0.0, ge=-40.0, le=40.0)
    left_antenna: float = Field(default=0.0, ge=-90.0, le=90.0)
    right_antenna: float = Field(default=0.0, ge=-90.0, le=90.0)
    duration_s: float = Field(default=0.35, ge=0.05, le=5.0)
    wait: bool = False


class RobotPoseResponse(BaseModel):
    action_id: str = Field(default_factory=lambda: uuid4().hex)
    queued: bool = True
    completed: bool = False
    queue_size: int
    error: str | None = None


class TranscribeTextRequest(BaseModel):
    text: str = Field(default="", max_length=4000)


class TranscribeResponse(BaseModel):
    text: str
    provider: str
    warm: bool
    latency_ms: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class SpeechMotionConfigRequest(BaseModel):
    enabled: bool
    intensity: float = Field(default=0.7, ge=0.0, le=1.0)


class SpeechMotionConfigResponse(BaseModel):
    enabled: bool
    intensity: float


class ClientLogRequest(BaseModel):
    level: Literal["debug", "info", "warning", "error"] = "info"
    message: str = Field(min_length=1, max_length=1000)
    data: dict[str, Any] = Field(default_factory=dict)


class ClientLogResponse(BaseModel):
    logged: bool = True
    session_log_file: str
    event_log_file: str


class ClientSpeakingRequest(BaseModel):
    speaking: bool
    reason: str = Field(default="browser-tts", max_length=120)
