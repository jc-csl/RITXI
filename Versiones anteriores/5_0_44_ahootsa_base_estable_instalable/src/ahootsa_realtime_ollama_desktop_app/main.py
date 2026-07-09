"""Ahootsa 5.0.44: app instalable sobre Reachy Mini Conversation App."""
from __future__ import annotations

import asyncio
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from reachy_mini import ReachyMini, ReachyMiniApp

APP_VERSION = "5.0.44"
APP_ID = "ahootsa_realtime_ollama_app"
DEFAULT_PROFILE = "ahootsa_realtime_es"
DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "llama3.2:3b"
DEFAULT_AHOOTSA_VOICE = "Sohee"


def package_root() -> Path:
    return Path(__file__).resolve().parent


def _runtime_log_path() -> Path:
    log_root = Path(os.getenv("AHOOTSA_LOG_DIR", r"D:\RITXI\logs"))
    log_root.mkdir(parents=True, exist_ok=True)
    sid = os.getenv("AHOOTSA_SESSION_ID") or datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(os.getenv("AHOOTSA_LOG_FILE_RUNTIME", str(log_root / f"ahootsa5_{sid}_runtime.log")))


def _log(event: str, **data: Any) -> None:
    try:
        import json
        payload = {"ts": datetime.now().isoformat(timespec="seconds"), "version": APP_VERSION, "event": event, "data": data}
        with _runtime_log_path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


def configure_ahootsa_environment(instance_path: Path | str | None = None) -> None:
    root = package_root()
    profile = os.getenv("AHOOTSA_PROFILE", DEFAULT_PROFILE).strip() or DEFAULT_PROFILE
    os.environ["REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY"] = str(root / "profiles")
    os.environ["REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY"] = str(root / "tools")
    os.environ["REACHY_MINI_CUSTOM_PROFILE"] = profile
    os.environ["REACHY_MINI_PROFILE"] = profile
    os.environ["REACHY_MINI_PERSONALITY"] = profile
    os.environ["AHOOTSA_NAME"] = "Ahootsa"
    os.environ["ASSISTANT_NAME"] = "Ahootsa"
    os.environ["ROBOT_NAME"] = "Ahootsa"
    os.environ["PROJECT_NAME"] = "Ahootsa"
    os.environ["AHOOTSA_LANGUAGE"] = "es"
    os.environ["REACHY_MINI_LANGUAGE"] = "es"
    os.environ["REALTIME_TRANSCRIPTION_LANGUAGE"] = os.getenv("REALTIME_TRANSCRIPTION_LANGUAGE", "es")
    os.environ.pop("BACKEND_PROVIDER", None)
    os.environ.pop("MODEL_NAME", None)
    os.environ.setdefault("HF_REALTIME_CONNECTION_MODE", os.getenv("AHOOTSA_HF_MODE", "deployed"))
    os.environ.setdefault("AHOOTSA_VOICE", DEFAULT_AHOOTSA_VOICE)
    os.environ.setdefault("OPENAI_REALTIME_VOICE", DEFAULT_AHOOTSA_VOICE)
    os.environ.setdefault("REACHY_MINI_VOICE", DEFAULT_AHOOTSA_VOICE)
    os.environ.setdefault("VOICE", DEFAULT_AHOOTSA_VOICE)
    os.environ.setdefault("REALTIME_VOICE", DEFAULT_AHOOTSA_VOICE)
    os.environ.setdefault("TTS_VOICE", DEFAULT_AHOOTSA_VOICE)
    os.environ.setdefault("AUDIO_VOICE", DEFAULT_AHOOTSA_VOICE)
    os.environ.setdefault("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)
    os.environ.setdefault("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
    os.environ.setdefault("AHOOTSA_OLLAMA_TIMEOUT_SECONDS", "20")
    os.environ.setdefault("AHOOTSA_DISABLE_EMOTION_AUDIO", "1")
    os.environ.setdefault("AHOOTSA_MEMORY_REACTION_ENABLED", "1")
    os.environ.setdefault("AHOOTSA_MEMORY_WINSOUND_ENABLED", "0")
    os.environ.setdefault("AHOOTSA_IDLE_REMINDER_ENABLED", "0")
    os.environ.setdefault("AHOOTSA_ACTION_PLAY_DELAY_SECONDS", "0")
    os.environ.setdefault("AHOOTSA_POST_PLAY_WAIT_SECONDS", "0.6")
    if instance_path:
        os.environ.setdefault("AHOOTSA_INSTANCE_PATH", str(instance_path))
    _log("environment_configured", profile=profile, external_profiles=os.environ.get("REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY"), external_tools=os.environ.get("REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY"), hf_mode=os.environ.get("HF_REALTIME_CONNECTION_MODE"), hf_ws_url=os.environ.get("HF_REALTIME_WS_URL", ""), ollama_base=os.environ.get("OLLAMA_BASE_URL"), ollama_model=os.environ.get("OLLAMA_MODEL"))


def _force_runtime_config() -> None:
    try:
        from reachy_mini_conversation_app.config import refresh_runtime_config_from_env
        refresh_runtime_config_from_env()
        _log("official_runtime_config_refreshed")
    except Exception as exc:
        _log("official_runtime_config_refresh_failed", error=repr(exc))


class AhootsaRealtimeOllamaApp(ReachyMiniApp):  # type: ignore[misc]
    custom_app_url = "http://localhost:7860/ahootsa"
    dont_start_webserver = False

    def run(self, reachy_mini: ReachyMini, stop_event: threading.Event) -> None:
        instance_path = self._get_instance_path().parent
        configure_ahootsa_environment(instance_path)
        asyncio.set_event_loop(asyncio.new_event_loop())
        try:
            from ahootsa_realtime_ollama_desktop_app.ahootsa_routes import mount_ahootsa_routes
            mount_ahootsa_routes(self.settings_app)
            _log("ahootsa_routes_mounted")
        except Exception as exc:
            _log("ahootsa_routes_mount_failed", error=repr(exc))
        from reachy_mini_conversation_app.main import run
        from reachy_mini_conversation_app.utils import parse_args
        _force_runtime_config()
        args, _ = parse_args()
        _log("starting_official_conversation_engine", instance_path=str(instance_path), args=repr(args))
        run(args, robot=reachy_mini, app_stop_event=stop_event, settings_app=self.settings_app, instance_path=instance_path)


if __name__ == "__main__":
    app = AhootsaRealtimeOllamaApp()
    try:
        app.wrapped_run()
    except KeyboardInterrupt:
        app.stop()
