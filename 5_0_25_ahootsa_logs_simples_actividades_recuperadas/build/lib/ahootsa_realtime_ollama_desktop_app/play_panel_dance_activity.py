"""Play panel-like dances/activities with audio."""
from __future__ import annotations
import importlib.util, sys
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
    needs_response = True
    parameters_schema = {
        "type": "object",
        "properties": {
            "activity": {"type": "string", "default": "dance1"},
            "sound": {"type": "boolean", "default": True},
            "delay_before_play_seconds": {"type": "number", "default": 0.0},
            "post_play_wait_seconds": {"type": "number", "default": 3.0},
        },
        "required": [],
    }
    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        _log_tool_start("play_panel_dance_activity", kwargs)
        requested = str(kwargs.get("activity", "dance1") or "dance1").strip()
        key = requested.lower().replace(" ", "_")
        move = ALIASES.get(key, requested)
        try:
            mod = _load_local_play_emotion()
            tool = mod.PlayEmotion()
            result = await tool(
                deps,
                emotion=move,
                sound=bool(kwargs.get("sound", True)),
                delay_before_play_seconds=kwargs.get("delay_before_play_seconds"),
                post_play_wait_seconds=kwargs.get("post_play_wait_seconds"),
            )
            if isinstance(result, dict):
                result["requested_activity"] = requested
                result["resolved_activity"] = move
                result["message_for_user"] = f"He hecho {move}."
            _log_tool_result("play_panel_dance_activity", result)
            return result
        except BaseException as exc:
            _log_tool_exception("play_panel_dance_activity", exc, {"requested": requested, "resolved": move})
            return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "requested_activity": requested, "resolved_activity": move, "message_for_user": ""}
