"""Play panel-like dances/activities with audio."""
from __future__ import annotations
import importlib.util, sys
from pathlib import Path
from typing import Any
from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies


def _load_local_play_emotion():
    path = Path(__file__).resolve().with_name("play_emotion.py")
    stamp = str(int(path.stat().st_mtime_ns))
    name = f"ahootsa_panel_play_emotion_{stamp}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if not (spec and spec.loader):
        raise ModuleNotFoundError("No se puede cargar play_emotion.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

ALIASES = {
    "baile": "dance1", "baila": "dance1", "dance": "dance1",
    "dance1": "dance1", "dance2": "dance2", "dance3": "dance3",
    "saludo": "welcoming2", "greeting": "welcoming2",
    "celebra": "success1", "celebracion": "success1", "celebración": "success1",
    "success": "success1", "feliz": "laughing2", "pensar": "thoughtful1",
    "thinking": "thoughtful1", "calma": "calming1",
    "electric": "electric1", "electrico": "electric1", "eléctrico": "electric1",
}

class PlayPanelDanceActivity(Tool):
    name = "play_panel_dance_activity"
    description = "Reproduce un baile o actividad/movimiento del panel de control, con audio asociado si existe."
    needs_response = False
    parameters_schema = {
        "type": "object",
        "properties": {
            "activity": {"type": "string", "default": "dance1"},
            "sound": {"type": "boolean", "default": True},
        },
        "required": [],
    }
    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        requested = str(kwargs.get("activity", "dance1") or "dance1").strip()
        key = requested.lower().replace(" ", "_")
        move = ALIASES.get(key, requested)
        mod = _load_local_play_emotion()
        tool = mod.PlayEmotion()
        result = await tool(deps, emotion=move, sound=bool(kwargs.get("sound", True)))
        result["requested_activity"] = requested
        result["resolved_activity"] = move
        result["message_for_user"] = f"Reproduciendo {move}."
        return result
