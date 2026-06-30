"""Ahootsa emotion tool with explicit audio.

This wrapper avoids ambiguity with the official play_emotion tool name.
It calls the profile-local PlayEmotion implementation, which plays movement + OGG audio.
"""

from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path
from typing import Any

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies


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
            }
        },
        "required": [],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        mod = _load_local_play_emotion()
        tool = mod.PlayEmotion()
        return await tool(deps, emotion=kwargs.get("emotion", "happy"), sound=True)
