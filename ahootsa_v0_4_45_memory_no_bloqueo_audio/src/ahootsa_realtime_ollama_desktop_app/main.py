"""Ahootsa Realtime Ollama wrapper for Reachy Mini Desktop.

v0.4.45:
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
import subprocess
import time
from pathlib import Path
from datetime import datetime

from reachy_mini import ReachyMini, ReachyMiniApp


APP_VERSION = "0.4.45"
APP_ID = "ahootsa_realtime_ollama_app"
PROFILE_NAME = "ahootsa_realtime_es"
DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "ahootsa-local:latest"
DEFAULT_AHOOTSA_VOICE = "Sohee"


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


def _copy_profile_to_default_fallback_locations(instance_path: Path) -> None:
    """Robust fallback for Desktop builds that ignore REACHY_MINI_CUSTOM_PROFILE.

    Some builds start with the official "default" or "starter_profile" profile
    before/without reading the custom profile variables. In that case the robot
    says "Hi there, I'm Reachy Mini" and does not know Ahootsa tools.

    To avoid that, Ahootsa copies its profile files over the installed
    default/starter profile folders, creating a backup marker first.
    """
    if os.getenv("AHOOTSA_FORCE_DEFAULT_PROFILE", "1").strip().lower() in {"0", "false", "no", "off"}:
        _log("default_fallback_disabled")
        return

    src = _profile_source()
    profile_roots: list[Path] = [
        Path(instance_path) / "profiles",
        Path(instance_path) / "user_personalities",
    ]

    try:
        import reachy_mini_conversation_app
        app_root = Path(reachy_mini_conversation_app.__file__).resolve().parent
        profile_roots.append(app_root / "profiles")
        profile_roots.append(app_root / "external_content" / "external_profiles")
    except Exception as exc:
        _log("default_fallback_conversation_app_path_failed", error=repr(exc))

    try:
        import reachy_talk_data
        data_root = Path(reachy_talk_data.__file__).resolve().parent
        profile_roots.append(data_root / "profiles")
        profile_roots.append(data_root / "external_content" / "external_profiles")
    except Exception as exc:
        _log("default_fallback_talk_data_path_failed", error=repr(exc))

    fallback_names = ("default", "starter_profile", "starter", "base")
    seen: set[str] = set()

    for root in profile_roots:
        if not root or not str(root) or not root.exists():
            continue
        for name in fallback_names:
            dst = root / name
            key = str(dst)
            if key in seen:
                continue
            seen.add(key)

            try:
                if dst.exists():
                    backup_marker = dst / ".ahootsa_backup_created"
                    if not backup_marker.exists():
                        backup = dst.with_name(dst.name + ".ahootsa_backup")
                        if not backup.exists():
                            shutil.copytree(dst, backup, dirs_exist_ok=True)
                        backup_marker.write_text(str(backup), encoding="utf-8")
                dst.mkdir(parents=True, exist_ok=True)
                shutil.copytree(src, dst, dirs_exist_ok=True)
                _log("default_fallback_profile_forced", dst=dst)
            except Exception as exc:
                _log("default_fallback_profile_failed", dst=dst, error=repr(exc))


def configure_ahootsa_realtime_ollama_environment(instance_path: Path) -> None:
    """Configure Ahootsa without copying profiles while the app is running.

    v0.4.45:
    Runtime copying caused WinError 32 file locks when the package was installed
    in editable mode and the official app was already reading profile files.
    Profile copying is now an install/repair-time action, not a runtime action.
    """

    # Only allow runtime copying for manual debugging.
    if os.getenv("AHOOTSA_RUNTIME_PROFILE_COPY", "0").strip().lower() in {"1", "true", "yes", "on"}:
        try:
            _copy_profile_to_known_locations(instance_path)
            _copy_profile_to_default_fallback_locations(instance_path)
            _log("runtime_profile_copy_enabled")
        except Exception as exc:
            _log("runtime_profile_copy_failed", error=repr(exc))
    else:
        _log("runtime_profile_copy_disabled", instance_path=instance_path)

    # Do not load old external/duplicate profiles from previous experiments.
    os.environ.pop("REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY", None)

    os.environ["REACHY_MINI_CUSTOM_PROFILE"] = PROFILE_NAME
    os.environ["REACHY_MINI_PROFILE"] = PROFILE_NAME
    os.environ["REACHY_MINI_PERSONALITY"] = PROFILE_NAME
    os.environ["REACHY_MINI_USER_PERSONALITY"] = PROFILE_NAME
    os.environ["AHOOTSA_FORCE_DEFAULT_PROFILE"] = "1"
    os.environ["AHOOTSA_RUNTIME_PROFILE_COPY"] = "0"

    # Voice hints for backends that read environment variables.
    os.environ["AHOOTSA_VOICE"] = DEFAULT_AHOOTSA_VOICE
    os.environ["OPENAI_REALTIME_VOICE"] = DEFAULT_AHOOTSA_VOICE
    os.environ["REACHY_MINI_VOICE"] = DEFAULT_AHOOTSA_VOICE
    os.environ["VOICE"] = DEFAULT_AHOOTSA_VOICE
    os.environ["REALTIME_VOICE"] = DEFAULT_AHOOTSA_VOICE
    os.environ["TTS_VOICE"] = DEFAULT_AHOOTSA_VOICE
    os.environ["AUDIO_VOICE"] = DEFAULT_AHOOTSA_VOICE

    # Keep the realtime audio pipeline responsive.
    os.environ.setdefault("REALTIME_TRANSCRIPTION_LANGUAGE", "es")
    os.environ.setdefault("BACKEND_PROVIDER", "huggingface")
    os.environ.setdefault("HF_REALTIME_CONNECTION_MODE", "deployed")

    # Local Ollama text tool configuration.
    os.environ.setdefault("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)
    os.environ.setdefault("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)

    # Memory reaction: disabled by default because calling movement/audio inside
    # choose_memory_cards can block the conversation audio loop on some systems.
    os.environ.setdefault("AHOOTSA_MEMORY_REACTION_ENABLED", "0")

    # Avoid Windows SAPI idle voice.
    os.environ.setdefault("AHOOTSA_IDLE_REMINDER_ENABLED", "0")

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
        runtime_profile_copy=os.environ.get("AHOOTSA_RUNTIME_PROFILE_COPY"),
        memory_reaction=os.environ.get("AHOOTSA_MEMORY_REACTION_ENABLED"),
        robot_tools="official_original_tools_plus_ahootsa_tools",
    )



def _speak_idle_reminder_once(text: str) -> None:
    try:
        escaped = text.replace("'", "''")
        cmd = (
            "Add-Type -AssemblyName System.Speech; "
            "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            "$s.Rate=0; $s.Volume=85; "
            f"$s.Speak('{escaped}')"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
            timeout=12,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        _log("idle_reminder_spoken", text=text)
    except Exception as exc:
        _log("idle_reminder_failed", error=repr(exc))


def _start_idle_reminder_thread(stop_event: threading.Event) -> None:
    enabled = os.getenv("AHOOTSA_IDLE_REMINDER_ENABLED", "0").strip().lower()
    if enabled in {"0", "false", "no", "off"}:
        _log("idle_reminder_disabled")
        return
    try:
        first_delay = float(os.getenv("AHOOTSA_IDLE_REMINDER_SECONDS", "20"))
    except Exception:
        first_delay = 20.0
    try:
        repeat_delay = float(os.getenv("AHOOTSA_IDLE_REMINDER_REPEAT_SECONDS", "60"))
    except Exception:
        repeat_delay = 60.0
    phrase = os.getenv("AHOOTSA_IDLE_REMINDER_TEXT", "Sigo aquí. Cuando quieras, podemos jugar o hacer otra actividad.")

    def worker() -> None:
        delay = max(5.0, first_delay)
        while delay > 0 and not stop_event.is_set():
            step = min(1.0, delay)
            time.sleep(step)
            delay -= step
        if stop_event.is_set():
            return
        while not stop_event.is_set():
            _speak_idle_reminder_once(phrase)
            delay = max(20.0, repeat_delay)
            while delay > 0 and not stop_event.is_set():
                step = min(1.0, delay)
                time.sleep(step)
                delay -= step

    threading.Thread(target=worker, name="AhootsaIdleReminder", daemon=True).start()
    _log("idle_reminder_started", first_delay=first_delay, repeat_delay=repeat_delay)


class AhootsaRealtimeOllamaApp(ReachyMiniApp):  # type: ignore[misc]
    custom_app_url = "http://localhost:7860/"
    dont_start_webserver = False

    def run(self, reachy_mini: ReachyMini, stop_event: threading.Event) -> None:
        instance_path = self._get_instance_path().parent
        configure_ahootsa_realtime_ollama_environment(instance_path)
        _start_idle_reminder_thread(stop_event)
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
