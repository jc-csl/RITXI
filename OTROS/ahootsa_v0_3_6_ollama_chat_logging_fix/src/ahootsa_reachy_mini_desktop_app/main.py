"""Local wrapper to show Ahootsa as a separate Reachy Mini Desktop app.

This package does not replace the official conversation app. It registers a new
``reachy_mini_apps`` entry point and configures the official conversation app to
start with the Spanish Ahootsa profile.

v0.2.6 profile strategy
-----------------------
Do NOT set REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY with copies of the official
profiles. The conversation app already ships those profiles in
``reachy_talk_data``. Duplicating them externally produces the official runtime
error "Ambiguous profile names found".

Instead, this wrapper copies only the Ahootsa profile into the app instance
``user_personalities`` folder and selects it as
``user_personalities/ahootsa_es``. This keeps all built-in profiles and adds
Ahootsa without collisions.
"""

from __future__ import annotations

import asyncio
import os
import shutil
import threading
from pathlib import Path

from reachy_mini import ReachyMini, ReachyMiniApp


APP_NAME = "ahootsa_reachy_mini_conversation_app"
PROFILE_NAME = "ahootsa_es"
USER_PROFILE_SELECTION = f"user_personalities/{PROFILE_NAME}"


def _copy_ahootsa_profile_to_user_personalities(instance_path: Path) -> None:
    """Install the bundled Ahootsa profile into the writable instance profile root."""
    src = Path(__file__).resolve().parent / "profiles" / PROFILE_NAME
    if not src.is_dir():
        raise RuntimeError(f"Ahootsa profile source not found: {src}")

    dst = Path(instance_path) / "user_personalities" / PROFILE_NAME
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True)


def configure_ahootsa_environment(instance_path: Path) -> None:
    """Configure the official conversation app to load Ahootsa safely."""
    _copy_ahootsa_profile_to_user_personalities(instance_path)

    # Important: leave built-in profiles active. Setting this variable to an
    # external folder containing official profile names causes Config to abort
    # with "Ambiguous profile names found".
    os.environ.pop("REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY", None)

    # Use setdefault so advanced users can override values externally.
    os.environ.setdefault("REACHY_MINI_CUSTOM_PROFILE", USER_PROFILE_SELECTION)
    os.environ.setdefault("REALTIME_TRANSCRIPTION_LANGUAGE", "es")
    os.environ.setdefault("BACKEND_PROVIDER", "huggingface")
    os.environ.setdefault("HF_REALTIME_CONNECTION_MODE", "deployed")


class AhootsaReachyMiniConversationApp(ReachyMiniApp):  # type: ignore[misc]
    """Ahootsa Spanish conversation app entry point for the Reachy Mini daemon."""

    custom_app_url = "http://0.0.0.0:7860/"
    dont_start_webserver = False

    def run(self, reachy_mini: ReachyMini, stop_event: threading.Event) -> None:
        """Run the official conversation app with Ahootsa Spanish configuration."""
        instance_path = self._get_instance_path().parent
        configure_ahootsa_environment(instance_path)
        asyncio.set_event_loop(asyncio.new_event_loop())

        # Import after environment setup so config.py reads the desired profile.
        from reachy_mini_conversation_app.main import run
        from reachy_mini_conversation_app.utils import parse_args

        try:
            from reachy_mini_conversation_app.config import refresh_runtime_config_from_env

            refresh_runtime_config_from_env()
        except Exception:
            # Older versions may not expose refresh_runtime_config_from_env.
            pass

        args, _ = parse_args()
        run(
            args,
            robot=reachy_mini,
            app_stop_event=stop_event,
            settings_app=self.settings_app,
            instance_path=instance_path,
        )


if __name__ == "__main__":
    app = AhootsaReachyMiniConversationApp()
    try:
        app.wrapped_run()
    except KeyboardInterrupt:
        app.stop()
