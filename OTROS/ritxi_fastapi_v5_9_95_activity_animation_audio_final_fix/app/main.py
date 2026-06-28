"""
v5.9.61 · Punto de entrada FastAPI

Este módulo concentra la API local usada por el navegador:
- sirve la interfaz HTML/JS/CSS;
- expone `/api/chat`, `/api/audio`, `/api/robot`, `/api/config` y `/api/status`;
- inicializa servicios compartidos en `Runtime`;
- registra eventos para diagnóstico;
- permite editar configuración y cerrar procesos desde el panel.

Regla de mantenimiento:
La interfaz (`app/static/app.js`) no debe hablar directamente con Ollama, Whisper o Reachy.
Siempre debe hacerlo a través de estos endpoints.
"""


from __future__ import annotations

from contextlib import asynccontextmanager
import os
import json
import subprocess
import sys
import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException, File, UploadFile, Query, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.audio.echo_guard import EchoGuard
from app.audio.stt import PersistentSTTService
from app.audio.local_whisper import transcribe_audio_file, warmup_whisper_model
from app.audio.tts_queue import TTSQueue
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging, event_log_path, log_event, sanitize_settings, session_log_path, session_start_iso
from app.core.daemon_manager import ReachyDaemonManager
from app.llm.factory import build_llm_provider
from app.models.schemas import (
    ArchitectureStatus,
    ClientLogRequest,
    ClientLogResponse,
    ClientSpeakingRequest,
    CharacterListResponse,
    CharacterResponse,
    CharacterSelectRequest,
    CharacterUpdateRequest,
    ChatRequest,
    ChatResponse,
    FeatureFlags,
    HealthResponse,
    IdleConfigRequest,
    IdleConfigResponse,
    LLMStatus,
    LogStatus,
    ManualActionRequest,
    ManualActionResponse,
    RobotPoseRequest,
    RobotPoseResponse,
    RobotStatus,
    RuntimeSettingsResponse,
    SessionResetResponse,
    SpeechMotionConfigRequest,
    SpeechMotionConfigResponse,
    TranscribeResponse,
    TranscribeTextRequest,
)
from app.orchestration.action_scheduler import ActionIntent, ActionScheduler
from app.orchestration.conversation import ConversationMemory
from app.orchestration.turn_manager import TurnManager
from app.robot.base import PoseCommand
from app.robot.reachy_sdk import ReachySdkRobotClient
from app.robot.simulated import SimulatedRobotClient
from app.services.character import CharacterManager

configure_logging()


class Runtime:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.echo_guard = EchoGuard(enabled=settings.echo_guard_enabled, cooldown_s=settings.echo_cooldown_s)
        self.llm = build_llm_provider(settings)
        self.robot = ReachySdkRobotClient(settings.robot_host) if settings.mode == "reachy_daemon" else SimulatedRobotClient()
        self.tts = TTSQueue(settings, self.echo_guard)
        self.stt = PersistentSTTService(settings)
        self.scheduler = ActionScheduler(settings=settings, robot=self.robot, tts=self.tts, idle_enabled=settings.idle_enabled_default)
        self.character_manager = CharacterManager(settings)
        self.memory = ConversationMemory(settings, self.llm, self.character_manager)
        self.turn_manager = TurnManager(settings, self.llm, self.memory, self.scheduler, self.echo_guard, self.character_manager)
        self.daemon_manager = ReachyDaemonManager(host=settings.robot_host, port=8000)

    async def start(self) -> None:
        log_event("runtime_start", settings=sanitize_settings(self.settings))
        await self.robot.connect()
        await self.stt.start()
        await self.tts.start()
        await self.scheduler.start()

    async def stop(self) -> None:
        log_event("runtime_stop")
        await self.scheduler.stop()
        await self.tts.stop()
        await self.stt.stop()
        await self.robot.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa y cierra los servicios compartidos de la aplicación."""
    settings = get_settings()
    runtime = Runtime(settings)
    await runtime.start()
    app.state.runtime = runtime
    try:
        yield
    finally:
        await runtime.stop()


app = FastAPI(title="Ritxi FastAPI v5", version="0.5.0", lifespan=lifespan)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def runtime() -> Runtime:
    return app.state.runtime


async def build_architecture_status() -> ArchitectureStatus:
    rt = runtime()
    llm_available = await rt.llm.is_available()
    robot_connected = await rt.robot.is_connected()
    stt_available = await rt.stt.is_available()
    warnings: list[str] = []

    if rt.settings.llm_provider != "mock" and not llm_available:
        warnings.append("El proveedor LLM configurado no responde; puedes usar RITXI_LLM_PROVIDER=mock para pruebas.")
    if rt.settings.mode == "reachy_daemon" and not robot_connected:
        warnings.append("Modo reachy_daemon activo, pero no hay conexión con el daemon/robot.")
    if rt.settings.mode == "reachy_daemon":
        warnings.append("Para simulación oficial recuerda ejecutar en otra terminal: reachy-mini-daemon --sim")
    if rt.settings.stt_provider == "http" and not stt_available:
        warnings.append("STT HTTP no disponible; usa navegador/browser o arranca el servidor STT persistente.")
    if rt.settings.stt_provider == "local_whisper" and not stt_available:
        warnings.append("STT local_whisper seleccionado. Instala requirements-stt-whisper.txt si el endpoint de transcripción indica que falta faster-whisper.")
    if rt.settings.tts_provider == "pyttsx3" and not rt.tts.available:
        warnings.append("TTS pyttsx3 no disponible; usa RITXI_TTS_PROVIDER=mock o none.")

    base_url: str | None = None
    if rt.settings.llm_provider == "ollama":
        base_url = rt.settings.ollama_url
    elif rt.settings.llm_provider == "openai_compatible":
        base_url = rt.settings.openai_base_url

    return ArchitectureStatus(
        app=rt.settings.app_name,
        version=rt.settings.app_version,
        turn_state=rt.turn_manager.state,
        robot=RobotStatus(mode=rt.settings.mode, kind=rt.robot.kind, connected=robot_connected, host=rt.settings.robot_host, last_error=getattr(rt.robot, "last_error", None)),
        llm=LLMStatus(
            provider=rt.llm.provider_name,
            model=rt.llm.model_name,
            available=llm_available,
            streaming_enabled=rt.settings.llm_streaming_enabled,
            base_url=base_url,
        ),
        stt=rt.stt.status().model_copy(update={"available": stt_available}),
        tts=rt.tts.status(),
        scheduler=rt.scheduler.status(),
        echo_guard=rt.echo_guard.status(),
        current_character=rt.character_manager.current(),
        last_latencies=rt.turn_manager.last_latencies,
        last_response=rt.turn_manager.last_response,
        logs=LogStatus(session_start=session_start_iso(), session_log_file=session_log_path(), event_log_file=event_log_path()),
        warnings=warnings,
    )


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    status = await build_architecture_status()
    return HealthResponse(**status.model_dump())


@app.get("/api/architecture/status", response_model=ArchitectureStatus)
async def architecture_status() -> ArchitectureStatus:
    return await build_architecture_status()




@app.get("/api/daemon/status")
async def daemon_status(limit: int = Query(default=120, ge=1, le=500)) -> dict[str, object]:
    """Estado y salida de terminal del daemon Reachy Mini.

    La ventana MuJoCo es una ventana nativa externa y no puede incrustarse de
    forma fiable dentro del navegador, pero esta API permite mostrar en el panel
    la salida de terminal del daemon y comprobar si responde en el puerto 8000.
    """
    status = runtime().daemon_manager.status(limit=limit)
    return status.__dict__


@app.post("/api/daemon/start")
async def daemon_start() -> dict[str, object]:
    status = runtime().daemon_manager.start()
    return status.__dict__


@app.post("/api/daemon/stop")
async def daemon_stop() -> dict[str, object]:
    status = runtime().daemon_manager.stop()
    return status.__dict__


@app.get("/api/runtime/settings", response_model=RuntimeSettingsResponse)
async def runtime_settings() -> RuntimeSettingsResponse:
    rt = runtime()
    return RuntimeSettingsResponse(
        flags_defaults=FeatureFlags(
            input_microphone=rt.settings.use_input_microphone_default,
            output_text=True,
            output_audio=rt.settings.use_output_audio_default,
            stt=True,
            llm=True,
            tts=rt.settings.use_output_audio_default,
            robot_motion=rt.settings.use_robot_motion_default,
            camera_vision=False,
            process_emotions=rt.settings.use_emotion_tags_default,
            streaming=rt.settings.llm_streaming_enabled,
            synchronize_turn=rt.settings.synchronize_turns_default,
            debug=rt.settings.debug_default,
            speech_motion=rt.settings.speech_motion_enabled_default,
            active_wait=rt.settings.idle_enabled_default,
            move_talk_generate_text=True,
            auto_voice_response=True,
            auto_send_after_stt=True,
            echo_guard=rt.settings.echo_guard_enabled,
            mode_tutor_di=True,
            detailed_logs=rt.settings.debug_default,
            save_session=True,
            simulation_mode=rt.settings.mode == "internal_simulation",
        ),
        mode=rt.settings.mode,
        llm_provider=rt.settings.llm_provider,
        llm_streaming_enabled=rt.settings.llm_streaming_enabled,
        stt_provider=rt.settings.stt_provider,
        tts_provider=rt.settings.tts_provider,
        echo_guard_enabled=rt.settings.echo_guard_enabled,
        idle_enabled=rt.scheduler.idle_enabled,
        speech_motion_enabled=rt.scheduler.speech_motion_enabled,
        speech_motion_intensity=rt.scheduler.speech_motion_intensity,
        current_character=rt.character_manager.current(),
    )



@app.get("/api/models/presets")
async def model_presets() -> dict[str, object]:
    base = Path(__file__).resolve().parents[1]
    path = base / "app" / "config" / "model_presets.json"
    if not path.exists():
        return {
            "default_model": runtime().settings.ollama_model,
            "presets": [],
            "current_model": getattr(runtime().llm, "model_name", runtime().settings.ollama_model),
        }
    data = json.loads(path.read_text(encoding="utf-8"))
    data["current_model"] = getattr(runtime().llm, "model_name", runtime().settings.ollama_model)
    return data


def _apply_model_override(rt: Runtime, payload: ChatRequest) -> None:
    model = (payload.llm_model or "").strip()
    preset = (payload.model_preset or "").strip()
    if not model and preset:
        try:
            base = Path(__file__).resolve().parents[1]
            data = json.loads((base / "app" / "config" / "model_presets.json").read_text(encoding="utf-8"))
            for item in data.get("presets", []):
                if item.get("id") == preset:
                    model = str(item.get("model") or "").strip()
                    break
        except Exception as exc:  # noqa: BLE001
            log_event("model_preset_load_error", preset=preset, error=str(exc))
    if not model:
        return
    allowed = {"qwen3:0.6b", "gemma3:1b", "llama3.2:1b", "llama3.2:3b"}
    if model not in allowed:
        log_event("model_override_rejected", requested=model, allowed=sorted(allowed))
        return
    if hasattr(rt.llm, "model_name"):
        old = getattr(rt.llm, "model_name", None)
        setattr(rt.llm, "model_name", model)
        log_event("model_override_applied", old_model=old, new_model=model, preset=preset or None)
    if payload.temperature is not None and hasattr(rt.llm, "temperature_override"):
        old_temp = getattr(rt.llm, "temperature_override", None)
        setattr(rt.llm, "temperature_override", float(payload.temperature))
        log_event("temperature_override_applied", old_temperature=old_temp, new_temperature=float(payload.temperature))

@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Texto vacío.")
    rt = runtime()
    _apply_model_override(rt, payload)
    return await rt.turn_manager.handle_text(payload.session_id, text, payload.flags)




@app.post("/api/audio/warmup_whisper")
async def warmup_whisper() -> dict[str, object]:
    """Precarga Whisper para que el primer uso del micro no tarde varios segundos."""
    settings = get_settings()
    result = await warmup_whisper_model(settings)
    return {"status": "ok", **result}

@app.post("/api/audio/transcribe_text", response_model=TranscribeResponse)
async def transcribe_text(payload: TranscribeTextRequest) -> TranscribeResponse:
    return await runtime().stt.transcribe_text(payload.text)




@app.post("/api/audio/transcribe_file", response_model=TranscribeResponse)
async def transcribe_file(
    file: UploadFile = File(...),
    language: str = Query(default="es", min_length=2, max_length=12),
    vocabulary_hint: str | None = Query(default=None, max_length=32),
) -> TranscribeResponse:
    """Transcribe audio recorded by the browser using local Whisper/faster-whisper.

    This endpoint is used when Web Speech API is unreliable. The browser sends
    a small WAV file captured from the PC microphone. The model is loaded lazily
    and kept warm by the Python process after the first request.
    """
    rt = runtime()
    return await transcribe_audio_file(
        file=file,
        settings=rt.settings,
        language=language or rt.settings.stt_whisper_language,
        vocabulary_hint=vocabulary_hint,
    )

@app.get("/api/characters", response_model=CharacterListResponse)
async def characters() -> CharacterListResponse:
    rt = runtime()
    return CharacterListResponse(current_character_id=rt.character_manager.current_id, characters=rt.character_manager.list_profiles())


@app.get("/api/character", response_model=CharacterResponse)
async def current_character() -> CharacterResponse:
    return CharacterResponse(current=runtime().character_manager.current())


@app.post("/api/character/select", response_model=CharacterResponse)
async def select_character(payload: CharacterSelectRequest) -> CharacterResponse:
    rt = runtime()
    try:
        profile = rt.character_manager.select(payload.character_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Carácter no encontrado") from exc
    return CharacterResponse(current=profile)


@app.put("/api/character", response_model=CharacterResponse)
async def update_character(payload: CharacterUpdateRequest) -> CharacterResponse:
    profile = runtime().character_manager.upsert(payload.profile, persist=payload.persist)
    return CharacterResponse(current=profile)


@app.post("/api/config/speech_motion", response_model=SpeechMotionConfigResponse)
async def set_speech_motion(payload: SpeechMotionConfigRequest) -> SpeechMotionConfigResponse:
    rt = runtime()
    rt.scheduler.set_speech_motion(payload.enabled, payload.intensity)
    return SpeechMotionConfigResponse(enabled=rt.scheduler.speech_motion_enabled, intensity=rt.scheduler.speech_motion_intensity)




@app.get("/api/audio/recorded/{emotion_id}")
async def recorded_audio_file(emotion_id: str):
    """Sirve el audio oficial de Hugging Face para que lo reproduzca el navegador.

    El dataset actual de Pollen Robotics usa principalmente `.ogg`; versiones
    anteriores podían usar `.wav`. Se sirve el tipo MIME según la extensión.
    """
    rt = runtime()
    robot = rt.robot
    if not hasattr(robot, "recorded_library"):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="La librería RecordedMoves no está disponible en este modo de robot.")
    try:
        executed_id, path, error = await __import__("asyncio").to_thread(
            robot.recorded_library.get_recorded_audio_path, emotion_id  # type: ignore[attr-defined]
        )
    except Exception as exc:  # noqa: BLE001
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error buscando audio oficial: {exc}")
    if not path:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=error or f"No se encontró audio oficial para {emotion_id}")

    suffix = Path(path).suffix.lower()
    media_type = "audio/ogg" if suffix == ".ogg" else "audio/wav"
    filename = f"{executed_id or emotion_id}{suffix or '.ogg'}"
    headers = {
        "X-Ritxi-Emotion-Id": emotion_id,
        "X-Ritxi-Executed-Id": executed_id or emotion_id,
        "X-Ritxi-Audio-Path": str(path),
    }
    log_event("recorded_audio_file_served", requested=emotion_id, executed_id=executed_id, path=str(path), media_type=media_type)
    return FileResponse(path, media_type=media_type, filename=filename, headers=headers)


@app.get("/api/robot/recorded_moves")
async def recorded_moves_catalog() -> dict[str, object]:
    """Diagnóstico de la librería oficial de emociones/movimientos grabados.

    Carga la librería de forma diferida. Si no hay red o el dataset cambia,
    devuelve el error y Ritxi seguirá usando movimientos internos de fallback.
    """
    rt = runtime()
    robot = rt.robot
    catalog: list[str] = []
    error: str | None = None
    if hasattr(robot, "recorded_library"):
        try:
            catalog = await __import__("asyncio").to_thread(robot.recorded_library.available_moves)  # type: ignore[attr-defined]
            error = getattr(robot.recorded_library, "last_error", None)  # type: ignore[attr-defined]
        except Exception as exc:  # noqa: BLE001
            error = str(exc)
    else:
        error = "El modo de robot actual no usa reachy_mini RecordedMoves."
    return {
        "library": rt.settings.recorded_moves_library,
        "enabled": rt.settings.use_recorded_moves_default,
        "play_audio": rt.settings.play_recorded_audio_default,
        "count": len(catalog),
        "moves": catalog,
        "error": error,
    }

@app.post("/api/robot/action", response_model=ManualActionResponse)
async def manual_action(payload: ManualActionRequest) -> ManualActionResponse:
    rt = runtime()
    # Limpiar diagnóstico anterior de audio/movimiento grabado para que la UI pueda
    # decidir si tiene que usar voz del navegador como fallback.
    if hasattr(rt.robot, "last_recorded_result"):
        try:
            rt.robot.last_recorded_result = None  # type: ignore[attr-defined]
        except Exception:
            pass
    action = await rt.scheduler.enqueue(
        ActionIntent(
            emotion=payload.emotion,
            text=payload.text,
            motion_enabled=payload.motion_enabled,
            audio_enabled=payload.audio_enabled,
            return_to_neutral=payload.return_to_neutral,
            layer=payload.layer,
            reason="manual",
            speech_motion=payload.speech_motion,
        ),
        wait=payload.wait,
    )
    details = None
    if payload.wait and hasattr(rt.robot, "last_recorded_result"):
        details = getattr(rt.robot, "last_recorded_result", None)
    return ManualActionResponse(action_id=action.action_id, queued=True, completed=payload.wait, queue_size=rt.scheduler.status().queue_size, error=action.error, details=details)


@app.post("/api/robot/pose", response_model=RobotPoseResponse)
async def robot_pose(payload: RobotPoseRequest) -> RobotPoseResponse:
    rt = runtime()
    action = await rt.scheduler.enqueue(
        ActionIntent(
            emotion="neutral",
            motion_enabled=True,
            audio_enabled=False,
            return_to_neutral=False,
            pose=PoseCommand(
                yaw=payload.yaw,
                pitch=payload.pitch,
                roll=payload.roll,
                left_antenna=payload.left_antenna,
                right_antenna=payload.right_antenna,
                duration_s=payload.duration_s,
            ),
            layer="manual",
            reason="pose",
        ),
        wait=payload.wait,
    )
    return RobotPoseResponse(action_id=action.action_id, queued=True, completed=payload.wait, queue_size=rt.scheduler.status().queue_size, error=action.error)


@app.post("/api/config/idle", response_model=IdleConfigResponse)
async def set_idle(payload: IdleConfigRequest) -> IdleConfigResponse:
    rt = runtime()
    rt.scheduler.set_idle(payload.enabled)
    if not payload.enabled:
        await rt.scheduler.enqueue(ActionIntent(emotion="neutral", motion_enabled=True, audio_enabled=False, return_to_neutral=False, layer="manual", reason="idle-off"))
    return IdleConfigResponse(enabled=payload.enabled)


@app.post("/api/sessions/{session_id}/reset", response_model=SessionResetResponse)
async def reset_session(session_id: str) -> SessionResetResponse:
    runtime().memory.reset(session_id)
    return SessionResetResponse(session_id=session_id, reset=True)


@app.post("/api/microphone/force_unmute")
async def microphone_force_unmute() -> dict[str, object]:
    rt = runtime()
    await rt.echo_guard.force_unmute("manual-ui")
    log_event("microphone_force_unmute_requested")
    return {"microphone_enabled": rt.echo_guard.status().microphone_enabled, "reason": rt.echo_guard.status().reason}




@app.post("/api/microphone/client_speaking")
async def microphone_client_speaking(payload: ClientSpeakingRequest) -> dict[str, object]:
    rt = runtime()
    if payload.speaking:
        await rt.echo_guard.mark_speaking(True)
    else:
        await rt.echo_guard.cooldown_and_unmute(payload.reason or "browser-tts-end")
    log_event("client_speaking_update", speaking=payload.speaking, reason=payload.reason)
    return {"speaking": rt.echo_guard.status().speaking, "microphone_enabled": rt.echo_guard.status().microphone_enabled, "reason": rt.echo_guard.status().reason}

@app.post("/api/log/client", response_model=ClientLogResponse)
async def client_log(payload: ClientLogRequest) -> ClientLogResponse:
    log_event("client_log", level=payload.level, message=payload.message, data=payload.data)
    return ClientLogResponse(session_log_file=session_log_path(), event_log_file=event_log_path())


@app.post("/api/robot/reconnect")
async def robot_reconnect() -> dict[str, object]:
    rt = runtime()
    ok = await rt.robot.connect()
    log_event("robot_reconnect_requested", ok=ok, last_error=getattr(rt.robot, "last_error", None))
    return {"connected": ok, "last_error": getattr(rt.robot, "last_error", None)}


@app.post("/api/shutdown")
async def shutdown_safe() -> dict[str, str]:
    rt = runtime()
    rt.scheduler.set_idle(False)
    await rt.scheduler.enqueue(ActionIntent(emotion="neutral", motion_enabled=True, audio_enabled=False, return_to_neutral=False, layer="manual", reason="safe-shutdown"), wait=True)
    return {"status": "Servicios internos puestos en reposo. Cierra Uvicorn con Ctrl+C para parar el servidor."}





def _project_root() -> Path:
    """Devuelve la raíz real del proyecto usando la ruta de app/main.py."""
    return Path(__file__).resolve().parents[1]


def _normalize_config_ref(path: str) -> tuple[str, str]:
    """Acepta una clave lógica o una ruta relativa segura y devuelve (key, rel_path).

    Ejemplos válidos:
    - stt_vocab_activity_mapping
    - app/config/stt_vocabularies/activity_mapping.json
    - app/config/interaction_policy.json
    """
    raw = (path or "").strip().replace("\\", "/")
    if not raw:
        raise HTTPException(status_code=400, detail="Ruta de configuración vacía")

    if raw in CONFIG_FILE_MAP:
        return raw, CONFIG_FILE_MAP[raw]

    # Permitir también rutas relativas que estén dentro del mapa permitido.
    for key, rel in CONFIG_FILE_MAP.items():
        if raw == rel.replace("\\", "/"):
            return key, rel

    raise HTTPException(
        status_code=404,
        detail=f"Archivo de configuración no permitido: {raw}. Usa una clave de /api/config/files o una ruta relativa permitida.",
    )


def _ensure_editable_config_exists(target: Path, rel_path: str) -> None:
    """Crea plantillas mínimas para configs editables si faltan.

    Esto evita errores al abrir configuraciones desde la pestaña Config. cuando
    un archivo nuevo todavía no existe en una instalación limpia.
    """
    if target.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    templates: dict[str, str] = {
        "app/config/stt_vocabularies/activity_mapping.json": "{\n  \"default\": \"open_text\",\n  \"activities\": {}\n}\n",
        "app/config/stt_vocabularies/common.json": "{\n  \"words\": []\n}\n",
        "app/config/stt_vocabularies/animals.json": "{\n  \"animals\": [\"perro\", \"gato\"]\n}\n",
        "app/config/stt_vocabularies/language.json": "{\n  \"words\": []\n}\n",
        "app/config/stt_vocabularies/social_communication.json": "{\n  \"phrases\": []\n}\n",
        "app/config/stt_vocabularies/emotions.json": "{\n  \"emotions\": [\"contento\", \"triste\", \"tranquilo\"]\n}\n",
        "app/config/stt_vocabularies/music_sounds.json": "{\n  \"sounds\": []\n}\n",
        "app/config/interaction_policy.json": "{\n  \"local_activity_ids\": [],\n  \"ollama_activity_ids\": [],\n  \"defaults\": {}\n}\n",
        "app/config/conversation_policy.json": "{\n  \"repetition_guard\": {\"enabled\": true},\n  \"topic_fallbacks\": {},\n  \"default_fallbacks\": {}\n}\n",
        "app/config/ritxi_constants.py": "DEFAULT_MODEL = \"qwen3:0.6b\"\nDEFAULT_TEMPERATURE = 0.25\n",
    }
    content = templates.get(rel_path.replace("\\", "/"), "")
    target.write_text(content, encoding="utf-8")
    log_event("config_file_template_created", rel_path=rel_path, target=str(target))


CONFIG_FILE_MAP = {
    ".env.example": ".env.example",
    "README.md": "README.md",
    "plan.md": "plan.md",
    "agents.local.md": "agents.local.md",

    # Archivos clave editables desde la pestaña Configuración
    "system_prompt": "app/prompts/system_prompt.txt",
    "settings_py": "app/core/config.py",
    "model_presets": "app/config/model_presets.json",
    "interaction_policy": "app/config/interaction_policy.json",
    "conversation_policy": "app/config/conversation_policy.json",
    "robot_motion_policy": "app/config/robot_motion_policy.json",
    "ritxi_constants": "app/config/ritxi_constants.py",
    "character_profile": "profiles/characters/ritxi_tutor_comunicacion_di.json",

    # Vocabularios STT guiados por actividad
    "stt_vocab_activity_mapping": "app/config/stt_vocabularies/activity_mapping.json",
    "stt_vocab_common": "app/config/stt_vocabularies/common.json",
    "stt_vocab_animals": "app/config/stt_vocabularies/animals.json",
    "stt_vocab_language": "app/config/stt_vocabularies/language.json",
    "stt_vocab_social": "app/config/stt_vocabularies/social_communication.json",
    "stt_vocab_emotions": "app/config/stt_vocabularies/emotions.json",
    "stt_vocab_music": "app/config/stt_vocabularies/music_sounds.json",
}


@app.get("/api/config/selftest")
async def config_selftest() -> dict[str, object]:
    """Comprueba que todas las rutas configurables sean relativas, seguras y abribles."""
    base = _project_root().resolve()
    results: list[dict[str, object]] = []
    ok = True
    for key, rel in CONFIG_FILE_MAP.items():
        target = (base / rel).resolve()
        safe = str(target).startswith(str(base))
        exists = target.exists()
        if not safe:
            ok = False
        results.append({"key": key, "real_path": rel, "safe": safe, "exists": exists})
    log_event("config_selftest", ok=ok, files=len(results))
    return {"ok": ok, "project_root": str(base), "files": results}


@app.get("/api/config/files")
async def list_config_files() -> dict[str, list[dict[str, str]]]:
    labels = {
        ".env.example": "Variables .env de ejemplo",
        "README.md": "README",
        "plan.md": "Plan técnico",
        "agents.local.md": "Instrucciones locales",
        "system_prompt": "Prompt de sistema",
        "settings_py": "Constantes / configuración Python",
        "model_presets": "Modelos rápidos Ollama",
        "conversation_policy": "Política conversación / repetición / fallbacks",
        "robot_motion_policy": "Política robot / animaciones inicio-final",
        "interaction_policy": "Política de interacción / fichas IA-local",
        "ritxi_constants": "Constantes externas Ritxi",
        "character_profile": "Perfil de carácter Ritxi",
        "stt_vocab_activity_mapping": "Mapa actividad → vocabulario",
        "stt_vocab_common": "Vocabulario común",
        "stt_vocab_animals": "Vocabulario animales",
        "stt_vocab_language": "Vocabulario lenguaje",
        "stt_vocab_social": "Vocabulario comunicación social",
        "stt_vocab_emotions": "Vocabulario emociones",
        "stt_vocab_music": "Vocabulario música/sonidos",
    }
    base = _project_root()
    files: list[dict[str, str]] = []
    for key, rel in CONFIG_FILE_MAP.items():
        target = base / rel
        # Todos los archivos permitidos se muestran. Si alguno falta, se crea al abrir.
        files.append({"path": rel, "key": key, "label": labels.get(key, key), "real_path": rel, "exists": str(target.exists()).lower()})
    return {"files": files}

@app.get("/api/config/file")
async def read_config_file(path: str = Query(...)) -> dict[str, str]:
    key, rel_path = _normalize_config_ref(path)
    base = _project_root()
    target = (base / rel_path).resolve()
    if not str(target).startswith(str(base.resolve())):
        raise HTTPException(status_code=403, detail="Ruta fuera del proyecto no permitida")
    try:
        _ensure_editable_config_exists(target, rel_path)
        content = target.read_text(encoding="utf-8", errors="replace")
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        log_event("config_file_read_error", key=key, rel_path=rel_path, error=str(exc))
        raise HTTPException(status_code=500, detail=f"No se pudo leer {rel_path}: {exc}") from exc
    if len(content) > 60000:
        content = content[:60000] + "\n\n...[recortado]..."
    log_event("config_file_read", key=key, rel_path=rel_path, bytes=len(content))
    return {"path": key, "real_path": rel_path, "content": content}


@app.post("/api/config/file")
async def save_config_file(
    path: str = Query(...),
    payload: dict = Body(...),
) -> dict[str, str | int]:
    """Guarda un archivo permitido de configuración desde el panel.

    Seguridad:
    - Solo se permiten claves incluidas en CONFIG_FILE_MAP.
    - No se aceptan rutas arbitrarias.
    - Se limita el tamaño para evitar escrituras accidentales enormes.
    """
    key, rel_path = _normalize_config_ref(path)

    content = str(payload.get("content", ""))
    if len(content) > 120_000:
        raise HTTPException(status_code=413, detail="Archivo demasiado grande para editar desde el panel")

    base = _project_root()
    target = (base / rel_path).resolve()

    if not str(target).startswith(str(base.resolve())):
        raise HTTPException(status_code=403, detail="Ruta fuera del proyecto no permitida")

    target.parent.mkdir(parents=True, exist_ok=True)

    # Validación mínima para JSON.
    if rel_path.endswith(".json"):
        try:
            import json
            json.loads(content)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=f"JSON no válido en {rel_path}: {exc}") from exc

    try:
        target.write_text(content, encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"No se pudo guardar el archivo: {exc}") from exc

    # Si se modifica el perfil de carácter, recargarlo en memoria.
    if key == "character_profile":
        try:
            rt = runtime()
            rt.character_manager.load_all()
            rt.character_manager.select(rt.settings.default_character_id)
        except Exception as exc:  # noqa: BLE001
            log_event("config_character_reload_error", error=str(exc))

    log_event("config_file_saved", key=key, rel_path=rel_path, bytes=len(content))
    return {"status": "guardado", "path": key, "real_path": rel_path, "bytes": len(content)}

@app.post("/api/exit_all")
async def exit_all(background_tasks: BackgroundTasks) -> dict[str, str]:
    """Cierra Ritxi y, en Windows, intenta cerrar también el daemon Reachy.

    Se usa desde el botón SALIR del panel. La respuesta vuelve al navegador y
    después se mata el proceso de FastAPI para no cortar la respuesta HTTP.
    """
    rt = runtime()
    rt.scheduler.set_idle(False)
    try:
        await rt.scheduler.enqueue(ActionIntent(emotion="neutral", motion_enabled=True, audio_enabled=False, return_to_neutral=False, layer="manual", reason="exit-all"), wait=False)
    except Exception as exc:  # noqa: BLE001
        log_event("exit_all_neutral_error", error=str(exc))

    def _close_later() -> None:
        if sys.platform.startswith("win"):
            cmd = (
                "timeout /t 1 /nobreak >nul "
                "& taskkill /IM reachy-mini-daemon.exe /F >nul 2>nul "
                f"& taskkill /PID {os.getpid()} /F >nul 2>nul"
            )
            subprocess.Popen(["cmd.exe", "/c", cmd], creationflags=subprocess.CREATE_NO_WINDOW)  # noqa: S603,S607
        else:
            async def _stop() -> None:
                await asyncio.sleep(1)
                os._exit(0)
            try:
                asyncio.create_task(_stop())
            except RuntimeError:
                os._exit(0)

    background_tasks.add_task(_close_later)
    log_event("exit_all_requested")
    return {"status": "Cerrando Ritxi y daemon Reachy. Puedes cerrar esta pestaña."}
@app.get("/api/interaction_policy")
async def interaction_policy() -> dict[str, object]:
    """Devuelve política externa de interacción desde app/config/interaction_policy.json."""
    base = Path(__file__).resolve().parents[1]
    path = base / "app" / "config" / "interaction_policy.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        log_event("interaction_policy_load_error", error=str(exc))
        return {
            "version": "fallback",
            "defaults": {"model": "qwen3:0.6b", "temperature": 0.25, "chat_timeout_ms": 60000},
            "local_activity_ids": [],
            "ollama_activity_ids": [],
        }



