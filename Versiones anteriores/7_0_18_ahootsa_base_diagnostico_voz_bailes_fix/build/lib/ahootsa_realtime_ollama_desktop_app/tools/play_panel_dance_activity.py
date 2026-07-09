"""Play panel-like dances/activities with Spanish names and robust resolution."""
from __future__ import annotations
import importlib.util, os, sys, unicodedata, re
from pathlib import Path
from typing import Any
from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies

def _repair_mojibake(text: str) -> str:
    if not isinstance(text, str):
        text = str(text or "")
    for enc in ("latin-1", "cp1252"):
        try:
            repaired = text.encode(enc, errors="strict").decode("utf-8", errors="strict")
            if repaired and repaired != text:
                return repaired
        except Exception:
            pass
    return text


def _normalize(value: object) -> str:
    text = _repair_mojibake(str(value or "").strip())
    without_accents = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", without_accents.lower()).strip("_")

def _profile_name() -> str:
    return (os.getenv("AHOOTSA_PROFILE") or os.getenv("REACHY_MINI_PROFILE") or "ahootsa7_realtime_es").strip() or "ahootsa7_realtime_es"

def _load_local_play_emotion():
    root = Path(__file__).resolve().parents[1]
    profile = _profile_name()
    candidates = [root / "profiles" / profile / "play_emotion.py", root / "profiles" / "ahootsa7_realtime_es" / "play_emotion.py", root / "profiles" / "ahootsa7_actividades" / "play_emotion.py"]
    for path in candidates:
        if path.exists():
            stamp = str(int(path.stat().st_mtime_ns))
            name = f"ahootsa_profile_play_emotion_{profile}_{stamp}"
            if name in sys.modules:
                return sys.modules[name]
            spec = importlib.util.spec_from_file_location(name, path)
            if not (spec and spec.loader):
                continue
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
            return mod
    raise ModuleNotFoundError("No se puede cargar play_emotion.py desde los perfiles Ahootsa")

def _log_tool_start(tool_name: str, kwargs: dict | None = None) -> None:
    try:
        import ahootsa_debug_logger  # type: ignore
        ahootsa_debug_logger.log_tool_start(tool_name, kwargs or {})
    except Exception: pass

def _log_tool_result(tool_name: str, result) -> None:
    try:
        import ahootsa_debug_logger  # type: ignore
        ahootsa_debug_logger.log_tool_result(tool_name, result)
    except Exception: pass

def _log_tool_exception(tool_name: str, exc: BaseException, data: dict | None = None) -> None:
    try:
        import ahootsa_debug_logger  # type: ignore
        ahootsa_debug_logger.log_exception("tool_exception", exc, data or {}, tool=tool_name)
    except Exception: pass

def _display_name(move: str, mod=None) -> str:
    try:
        if mod and hasattr(mod, "display_name_for_move"):
            return str(mod.display_name_for_move(move))
    except Exception: pass
    defaults = {"dance1":"baile alegre uno", "dance2":"baile animado dos", "dance3":"baile con energía tres", "success1":"celebración", "welcoming2":"saludo", "calming1":"calma", "electric1":"eléctrico"}
    return defaults.get(move, move)

class PlayPanelDanceActivity(Tool):
    name = "play_panel_dance_activity"
    description = "Reproduce un baile, emoción o movimiento del panel usando nombres en español. Úsala SIEMPRE para: baile uno, baile dos, baile tres, saludo, celebración, calma, eléctrico. No uses la herramienta oficial dance para estos recursos."
    needs_response = True
    parameters_schema = {"type": "object", "properties": {"activity": {"type": "string", "default": "baile uno", "description": "Nombre en español o técnico. Ejemplos: baile uno, baile dos, baile tres, saludo, celebración, calma, dance1. También entiende: sludo, sluod, play, olay, play dos, olay dos, baile número dos, baile número tres."}, "sound": {"type": "boolean", "default": True}, "delay_before_play_seconds": {"type": "number", "default": 0.0}, "post_play_wait_seconds": {"type": "number", "default": 3.0}}, "required": []}
    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        _log_tool_start("play_panel_dance_activity", kwargs)
        requested = str(kwargs.get("activity", "baile uno") or "baile uno").strip()
        try:
            mod = _load_local_play_emotion()
            resolved = mod.resolve_emotion_name(requested) if hasattr(mod, "resolve_emotion_name") else None
            if not resolved:
                examples = mod.available_examples_es() if hasattr(mod, "available_examples_es") else ["baile uno", "baile dos", "baile tres", "celebración", "saludo"]
                result = {"ok": False, "error": "actividad_no_reconocida", "requested_activity": requested, "available_examples": examples, "message_for_user": "No he reconocido ese baile o emoción. Prueba con baile uno, baile dos, baile tres, saludo, celebración, calma o eléctrico."}
                _log_tool_result("play_panel_dance_activity", result)
                return result
            tool = mod.PlayEmotion()
            result = await tool(deps, emotion=resolved, sound=bool(kwargs.get("sound", True)), delay_before_play_seconds=kwargs.get("delay_before_play_seconds"), post_play_wait_seconds=kwargs.get("post_play_wait_seconds"))
            if isinstance(result, dict):
                if result.get("ok") or result.get("motion_ok") or result.get("audio_ok") or (isinstance(result.get("motion"), dict) and result["motion"].get("ok")) or result.get("status") in {"played", "audio_played_motion_not_confirmed"}:
                    result["ok"] = True
                    result["status"] = result.get("status") or "played"
                result["requested_activity"] = requested
                result["resolved_activity"] = resolved
                result["resolved_activity_es"] = _display_name(resolved, mod)
                result["message_for_user"] = f"He hecho {_display_name(resolved, mod)}."
                result.setdefault("mujoco_note", "Si MuJoCo muestra avisos IK pero el movimiento se ve, no es fallo del baile.")
            _log_tool_result("play_panel_dance_activity", result)
            return result
        except BaseException as exc:
            _log_tool_exception("play_panel_dance_activity", exc, {"requested": requested})
            return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "requested_activity": requested, "message_for_user": "No he podido lanzar ese baile o emoción."}
