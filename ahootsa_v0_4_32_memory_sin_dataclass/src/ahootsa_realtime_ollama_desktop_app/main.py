"""Ahootsa Realtime Ollama wrapper for Reachy Mini Desktop.

v0.4.14:
- keeps the official conversation app intact;
- forces the Ahootsa profile at startup with REACHY_MINI_CUSTOM_PROFILE=ahootsa_realtime_es;
- copies the Ahootsa profile to user-personalities AND to the official app profile folder as an added profile;
- keeps original robot tools and adds only ask_ollama.
"""

from __future__ import annotations

import os
import shutil
import asyncio
import threading
from pathlib import Path
from datetime import datetime

from reachy_mini import ReachyMini, ReachyMiniApp


APP_VERSION = "0.4.32"
APP_ID = "ahootsa_realtime_ollama_app"
PROFILE_NAME = "ahootsa_realtime_es"
DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "ahootsa-local:latest"


def _default_log_dir() -> Path:
    base = os.getenv("LOCALAPPDATA")
    if base:
        return Path(base) / "Reachy Mini Control" / "ahootsa_logs"
    return Path.cwd() / "ahootsa_logs"


def _log(step: str, **data: object) -> None:
    try:
        log_dir = Path(os.getenv("AHOOTSA_LOG_DIR", str(_default_log_dir())))
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"ahootsa_realtime_ollama_v{APP_VERSION.replace('.', '_')}.log"
        extra = ""
        if data:
            extra = " | " + " | ".join(f"{k}={v}" for k, v in data.items())
        with log_file.open("a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat(timespec='seconds')} | {step}{extra}\n")
    except Exception:
        pass


def _profile_source() -> Path:
    src = Path(__file__).resolve().parent / "profiles" / PROFILE_NAME
    if not src.is_dir():
        raise RuntimeError(f"Ahootsa profile source not found: {src}")
    return src


def _copy_profile(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True)

    tools = dst / "tools.txt"
    ask = dst / "ask_ollama.py"
    if tools.exists():
        raw = tools.read_text(encoding="utf-8")
        if "ask_ollama" not in raw:
            tools.write_text(raw.rstrip() + "\nask_ollama\n", encoding="utf-8")
    if not ask.exists():
        raise RuntimeError(f"ask_ollama.py was not copied to {dst}")

    _log("profile_copied", src=src, dst=dst)


def _copy_profile_to_known_locations(instance_path: Path) -> None:
    """Copy Ahootsa profile to several recognized profile locations.

    The official app loads tools from the selected profile at startup.
    Some Desktop builds use instance/user_personalities, while the documented
    custom profile mechanism expects a named profile under the official package
    profiles directory. We add the Ahootsa folder without modifying official
    built-in profiles.
    """
    src = _profile_source()

    # Writable instance locations.
    candidates: list[Path] = [
        Path(instance_path) / "user_personalities" / PROFILE_NAME,
        Path(instance_path) / "profiles" / PROFILE_NAME,
        Path(os.getenv("LOCALAPPDATA", "")) / "Reachy Mini Control" / "user_personalities" / PROFILE_NAME,
    ]

    # Official package profile location. This adds a new folder only.
    try:
        import reachy_mini_conversation_app

        pkg_profiles = Path(reachy_mini_conversation_app.__file__).resolve().parent / "profiles" / PROFILE_NAME
        candidates.append(pkg_profiles)
    except Exception as exc:
        _log("official_profile_path_failed", error=repr(exc))

    seen: set[str] = set()
    for dst in candidates:
        if not str(dst) or str(dst) in seen:
            continue
        seen.add(str(dst))
        try:
            _copy_profile(src, dst)
        except Exception as exc:
            _log("profile_copy_failed", dst=dst, error=repr(exc))


def configure_ahootsa_realtime_ollama_environment(instance_path: Path) -> None:
    _copy_profile_to_known_locations(instance_path)

    # Do not load old external/duplicate profiles from previous experiments.
    os.environ.pop("REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY", None)

    # IMPORTANT:
    # The official README documents REACHY_MINI_CUSTOM_PROFILE=<name>.
    # Do not set user_personalities/<name> here, because some versions then fall back to default.
    os.environ["REACHY_MINI_CUSTOM_PROFILE"] = PROFILE_NAME

    # Keep original realtime audio behavior. Ollama is text-only and is only exposed as a tool.
    os.environ.setdefault("REALTIME_TRANSCRIPTION_LANGUAGE", "es")
    os.environ.setdefault("BACKEND_PROVIDER", "huggingface")
    os.environ.setdefault("HF_REALTIME_CONNECTION_MODE", "deployed")

    # Local Ollama text tool configuration.
    os.environ.setdefault("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)
    os.environ.setdefault("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)

    # Remove old experimental local emotion variables.
    os.environ.pop("AHOOTSA_EMOTIONS_LIBRARY_DIR", None)
    os.environ.pop("REACHY_MINI_EMOTIONS_LIBRARY_DIR", None)
    os.environ.pop("AHOOTSA_LOCAL_EMOTIONS_LIBRARY", None)

    _log(
        "environment_configured",
        profile=os.environ.get("REACHY_MINI_CUSTOM_PROFILE"),
        backend=os.environ.get("BACKEND_PROVIDER"),
        hf_mode=os.environ.get("HF_REALTIME_CONNECTION_MODE"),
        ollama_base=os.environ.get("OLLAMA_BASE_URL"),
        ollama_model=os.environ.get("OLLAMA_MODEL"),
        robot_tools="official_original_tools_plus_ask_ollama",
    )


class AhootsaRealtimeOllamaApp(ReachyMiniApp):  # type: ignore[misc]
    custom_app_url = "http://localhost:7860/"
    dont_start_webserver = False

    def run(self, reachy_mini: ReachyMini, stop_event: threading.Event) -> None:
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
