"""Ahootsa Realtime Ollama wrapper for Reachy Mini Desktop.

This is the v0.4.9 base approach:
start from the original realtime conversation app, keep audio, profiles,
robot tools and emotions, and add Ollama as an extra callable tool.

Important design choice
-----------------------
Ollama is not a realtime audio backend. Therefore this app does NOT replace
Hugging Face/OpenAI/Gemini realtime audio with Ollama. Instead, it runs the
original app unchanged and adds an `ask_ollama` tool plus the original robot tools to the Ahootsa profile.
The realtime model can call that local tool when it needs local text reasoning.
"""

from __future__ import annotations

import os
import shutil
import asyncio
import threading
from pathlib import Path
from datetime import datetime

from reachy_mini import ReachyMini, ReachyMiniApp


APP_VERSION = "0.4.9"
APP_ID = "ahootsa_realtime_ollama_app"
PROFILE_NAME = "ahootsa_realtime_es"
USER_PROFILE_SELECTION = f"user_personalities/{PROFILE_NAME}"
DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "ahootsa-local:latest"


def _default_log_dir() -> Path:
    base = os.getenv("LOCALAPPDATA")
    if base:
        return Path(base) / "Reachy Mini Control" / "ahootsa_logs"
    return Path.cwd() / "ahootsa_logs"


def _log(step: str, **data: object) -> None:
    """Write a lightweight diagnostic log without risking app startup."""
    try:
        log_dir = Path(os.getenv("AHOOTSA_LOG_DIR", str(_default_log_dir())))
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "ahootsa_realtime_ollama_v0_4_9.log"
        extra = ""
        if data:
            extra = " | " + " | ".join(f"{k}={v}" for k, v in data.items())
        with log_file.open("a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat(timespec='seconds')} | {step}{extra}\n")
    except Exception:
        pass


def _copy_profile_to_user_personalities(instance_path: Path) -> None:
    """Install the bundled Ahootsa Realtime profile into the writable app instance."""
    src = Path(__file__).resolve().parent / "profiles" / PROFILE_NAME
    if not src.is_dir():
        raise RuntimeError(f"Ahootsa profile source not found: {src}")

    dst = Path(instance_path) / "user_personalities" / PROFILE_NAME
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True)
    _log("profile_copied", src=src, dst=dst)


def configure_ahootsa_realtime_ollama_environment(instance_path: Path) -> None:
    """Configure the original conversation app to run as Ahootsa Realtime Ollama."""
    _copy_profile_to_user_personalities(instance_path)

    # Avoid the duplicate-profile problem. Built-in profiles stay in reachy_talk_data.
    os.environ.pop("REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY", None)

    # Start with Ahootsa. Users can still switch profiles in the UI.
    os.environ.setdefault("REACHY_MINI_CUSTOM_PROFILE", USER_PROFILE_SELECTION)

    # Keep original realtime audio behavior working. This is intentionally still
    # Hugging Face realtime by default because Ollama is text-only.
    os.environ.setdefault("REALTIME_TRANSCRIPTION_LANGUAGE", "es")
    os.environ.setdefault("BACKEND_PROVIDER", "huggingface")
    os.environ.setdefault("HF_REALTIME_CONNECTION_MODE", "deployed")

    # Local Ollama text tool configuration.
    os.environ.setdefault("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)
    os.environ.setdefault("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)

    # Ahootsa v0.4.9 base original resources:
    # do NOT force the experimental local JSON/OGG library.
    # Movement, dances and emotions must ALWAYS come from the original conversation app tools:
    # dance, stop_dance, play_emotion, stop_emotion, move_head, sweep_look, etc.
    # Clearing these process variables prevents older v0.4.4-v0.4.6 settings from hijacking
    # the official tool behavior. It does not delete files from disk.
    os.environ.pop("AHOOTSA_EMOTIONS_LIBRARY_DIR", None)
    os.environ.pop("REACHY_MINI_EMOTIONS_LIBRARY_DIR", None)

    _log(
        "environment_configured",
        profile=os.environ.get("REACHY_MINI_CUSTOM_PROFILE"),
        backend=os.environ.get("BACKEND_PROVIDER"),
        hf_mode=os.environ.get("HF_REALTIME_CONNECTION_MODE"),
        ollama_base=os.environ.get("OLLAMA_BASE_URL"),
        ollama_model=os.environ.get("OLLAMA_MODEL"),
        robot_tools="original_conversation_app_tools_intact",
    )


class AhootsaRealtimeOllamaApp(ReachyMiniApp):  # type: ignore[misc]
    """Desktop entry point: original conversation app + local Ollama tool."""

    custom_app_url = "http://0.0.0.0:7860/"
    dont_start_webserver = False

    def run(self, reachy_mini: ReachyMini, stop_event: threading.Event) -> None:
        """Run the official conversation app with Ahootsa + Ollama tool configuration."""
        instance_path = self._get_instance_path().parent
        configure_ahootsa_realtime_ollama_environment(instance_path)
        asyncio.set_event_loop(asyncio.new_event_loop())

        # Import after environment setup so config.py reads the desired values.
        from reachy_mini_conversation_app.main import run
        from reachy_mini_conversation_app.utils import parse_args

        try:
            from reachy_mini_conversation_app.config import refresh_runtime_config_from_env

            refresh_runtime_config_from_env()
        except Exception as exc:
            _log("refresh_runtime_config_from_env_failed", error=repr(exc))

        args, _ = parse_args()
        _log("starting_official_conversation_app", instance_path=instance_path)
        run(
            args,
            robot=reachy_mini,
            app_stop_event=stop_event,
            settings_app=self.settings_app,
            instance_path=instance_path,
        )


if __name__ == "__main__":
    app = AhootsaRealtimeOllamaApp()
    try:
        app.wrapped_run()
    except KeyboardInterrupt:
        app.stop()
