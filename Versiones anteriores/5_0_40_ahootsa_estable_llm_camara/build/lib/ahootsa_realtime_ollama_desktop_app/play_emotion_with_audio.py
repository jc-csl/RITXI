"""Ahootsa emotion tool with explicit audio.

0.4.57.2 passes delay_before_play_seconds to play_emotion so Ahootsa can speak first.
"""

from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path
from typing import Any

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies

def _load_debug_logger():
    try:
        import ahootsa_debug_logger  # type: ignore
        return ahootsa_debug_logger
    except Exception:
        try:
            import importlib.util
            import sys
            from pathlib import Path
            path = Path(__file__).resolve().with_name("ahootsa_debug_logger.py")
            name = "ahootsa_debug_logger_runtime"
            if name in sys.modules:
                return sys.modules[name]
            spec = importlib.util.spec_from_file_location(name, path)
            if not (spec and spec.loader):
                return None
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
            return mod
        except Exception:
            return None


def _log_tool_start(tool_name: str, kwargs: dict | None = None) -> None:
    mod = _load_debug_logger()
    if mod:
        mod.log_tool_start(tool_name, kwargs or {})


def _log_tool_result(tool_name: str, result) -> None:
    mod = _load_debug_logger()
    if mod:
        mod.log_tool_result(tool_name, result)


def _log_tool_exception(tool_name: str, exc: BaseException, data: dict | None = None) -> None:
    mod = _load_debug_logger()
    if mod:
        mod.log_exception("tool_exception", exc, data or {}, tool=tool_name)




def _load_local_play_emotion():
    path = Path(__file__).resolve().with_name("play_emotion.py")
    stamp = str(int(path.stat().st_mtime_ns))
    name = f"ahootsa_local_play_emotion_audio_{stamp}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if not (spec and spec.loader):
        raise ModuleNotFoundError("No se puede cargar play_emotion.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class PlayEmotionWithAudio(Tool):
    name = "play_emotion_with_audio"
    description = (
        "Play a Reachy emotion with movement and associated OGG audio. "
        "Use this in Ahootsa when the user asks for an emotion and the sound must be heard."
    )
    needs_response = False

    parameters_schema = {
        "type": "object",
        "properties": {
            "emotion": {
                "type": "string",
                "description": "Emotion name or intent, for example greeting, success, happy, thinking, calming, dance.",
                "default": "happy",
            },
            "delay_before_play_seconds": {
                "type": "number",
                "description": "Optional seconds to wait before playing movement/audio. Default 0.",
                "default": 0.0
            },
            "post_play_wait_seconds": {
                "type": "number",
                "description": "Seconds to wait after play before response. Default 3.0.",
                "default": 3.0
            }
        },
        "required": [],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        _log_tool_start("play_emotion_with_audio", kwargs)
        try:
            mod = _load_local_play_emotion()
            tool = mod.PlayEmotion()
            result = await tool(
                deps,
                emotion=kwargs.get("emotion", "happy"),
                sound=True,
                delay_before_play_seconds=kwargs.get("delay_before_play_seconds"),
                post_play_wait_seconds=kwargs.get("post_play_wait_seconds"),
            )
            if isinstance(result, dict):
                result["message_for_user"] = result.get("message_for_user", "")
            _log_tool_result("play_emotion_with_audio", result)
            return result
        except BaseException as exc:
            _log_tool_exception("play_emotion_with_audio", exc, kwargs)
            return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "message_for_user": ""}
