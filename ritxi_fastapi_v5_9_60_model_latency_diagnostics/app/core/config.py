"""
v5.9.42 · Comentarios de arquitectura

Configuración central de Ritxi.

Responsabilidades:
- definir valores por defecto;
- leer variables de entorno;
- controlar proveedores activos: Ollama, STT, TTS, robot;
- limitar tiempos y tamaños para mantener baja latencia.

Los scripts 1/2/3/4 configuran parte de estas variables al arrancar.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración centralizada de Ritxi v5.

    Todas las variables se pueden sobrescribir con prefijo RITXI_.
    La v4 prioriza conversación continua por micro/audio PC, carácter configurable
    y sincronización estricta del ciclo escuchar → pensar → hablar/mover → escuchar.
    """

    model_config = SettingsConfigDict(
        env_prefix="RITXI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Ritxi FastAPI v5"
    app_version: str = "0.5.6"

    # Robot
    mode: Literal["internal_simulation", "reachy_daemon"] = "internal_simulation"
    robot_host: str = "127.0.0.1"
    robot_port: int = Field(default=50051, ge=1, le=65535)

    # LLM
    llm_provider: Literal["ollama", "openai_compatible", "mock"] = "ollama"
    llm_streaming_enabled: bool = True
    llm_temperature: float = Field(default=0.25, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(default=40, ge=16, le=4096)
    llm_timeout_s: float = Field(default=60.0, ge=1.0, le=180.0)
    mock_fallback_enabled: bool = True

    # Ollama
    ollama_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "gemma3:1b"

    # OpenAI-compatible: Ollama / LM Studio / llama.cpp server / MLX server con API compatible
    openai_base_url: str = "http://127.0.0.1:11434/v1"
    openai_api_key: str = "ollama"
    openai_model: str = "gemma3:1b"

    # Conversación y carácter
    max_history_messages: int = Field(default=2, ge=0, le=50)
    default_session_id: str = "demo"
    default_character_id: str = "ritxi_tutor_comunicacion_di"
    synchronize_turns_default: bool = True
    first_sentence_tts_streaming: bool = True
    turn_min_delay_ms: int = Field(default=150, ge=0, le=5000)
    realtime_relisten_delay_ms: int = Field(default=450, ge=100, le=8000)

    # STT persistente / navegador
    stt_provider: Literal["browser", "mock", "http", "local_whisper"] = "browser"
    stt_server_url: str = "http://127.0.0.1:8765"
    stt_keep_warm: bool = True
    stt_timeout_s: float = Field(default=12.0, ge=1.0, le=120.0)
    stt_whisper_model_size: str = "tiny"
    stt_whisper_compute_type: str = "int8"
    stt_whisper_language: str = "es"

    # TTS por cola
    tts_provider: Literal["none", "mock", "pyttsx3", "browser"] = "mock"
    tts_rate: int = Field(default=165, ge=80, le=260)
    tts_voice: str | None = None

    # Echo guard
    echo_guard_enabled: bool = True
    echo_cooldown_s: float = Field(default=0.9, ge=0.0, le=10.0)

    # Movimiento mientras habla
    speech_motion_enabled_default: bool = True
    speech_motion_intensity_default: float = Field(default=0.72, ge=0.0, le=1.0)
    speech_motion_interval_s: float = Field(default=0.45, ge=0.12, le=2.0)


    # Biblioteca oficial de movimientos/emociones grabadas de Reachy Mini
    use_recorded_moves_default: bool = True
    play_recorded_audio_default: bool = False
    recorded_moves_library: str = "pollen-robotics/reachy-mini-emotions-library"

    # UI defaults
    use_input_microphone_default: bool = True
    use_output_audio_default: bool = True
    use_robot_motion_default: bool = True
    use_emotion_tags_default: bool = True
    idle_enabled_default: bool = False
    debug_default: bool = True

    # CORS
    cors_origins: str = "*"

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def selected_model(self) -> str:
        if self.llm_provider == "ollama":
            return self.ollama_model
        if self.llm_provider == "openai_compatible":
            return self.openai_model
        return "mock-ritxi-v5"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
