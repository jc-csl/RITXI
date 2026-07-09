# AHOOTSA_5_0_7_DIRECT_MEMORY_RESPONSE: evita bloqueo post-tool.
from __future__ import annotations
# AHOOTSA_5_0_10_TOOL_LOG
try:
    from ahootsa_logging import log_event
except Exception:
    def log_event(*a, **k): pass

import asyncio
import copy
import importlib.util
import json
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


def _log_event(event: str, data: dict[str, Any] | None = None, tool: str = "choose_memory_cards") -> None:
    mod = _load_debug_logger()
    if mod:
        mod.log_event(event, data or {}, tool=tool)


def _log_start(tool_name: str, kwargs: dict[str, Any]) -> None:
    mod = _load_debug_logger()
    if mod:
        mod.log_tool_start(tool_name, kwargs)


def _log_result(tool_name: str, result: Any) -> None:
    mod = _load_debug_logger()
    if mod:
        mod.log_tool_result(tool_name, result)


def _log_exc(tool_name: str, exc: BaseException, data: dict[str, Any] | None = None) -> None:
    mod = _load_debug_logger()
    if mod:
        mod.log_exception("tool_exception", exc, data or {}, tool=tool_name)


def _load_sibling_module(module_name: str, filename: str):
    path = Path(__file__).resolve().with_name(filename)
    if not path.exists():
        raise ModuleNotFoundError(f"No existe {filename} en {Path(__file__).resolve().parent}")
    try:
        stamp = str(int(path.stat().st_mtime_ns))
    except Exception:
        stamp = str(int(time.time() * 1000))
    stable_name = f"ahootsa_shared_tool_{module_name}"
    if stable_name in sys.modules:
        return sys.modules[stable_name]
    spec = importlib.util.spec_from_file_location(stable_name, path)
    if not (spec and spec.loader):
        raise ModuleNotFoundError(f"No se puede cargar {filename}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[stable_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _profile_name() -> str:
    try:
        import os
        return (os.getenv("AHOOTSA_PROFILE") or os.getenv("REACHY_MINI_PROFILE") or "ahootsa7_realtime_es").strip() or "ahootsa7_realtime_es"
    except Exception:
        return "ahootsa7_realtime_es"


def _load_profile_play_emotion():
    """Load Ahootsa profile-local play_emotion without requiring tools/play_emotion.py.

    Important: the official Reachy app already has a built-in play_emotion tool.
    We must not copy Ahootsa play_emotion into tools/, because that creates a
    name collision. Memory reactions and panel dances should load the profile
    local implementation explicitly from profiles/<profile>/play_emotion.py.
    """
    root = Path(__file__).resolve().parents[1]
    profile = _profile_name()
    candidates = [
        root / "profiles" / profile / "play_emotion.py",
        root / "profiles" / "ahootsa7_realtime_es" / "play_emotion.py",
        root / "profiles" / "ahootsa7_actividades" / "play_emotion.py",
        root / "profiles" / "ahootsa7_completo" / "play_emotion.py",
    ]
    for path in candidates:
        if path.exists():
            try:
                stamp = str(int(path.stat().st_mtime_ns))
            except Exception:
                stamp = str(int(time.time() * 1000))
            stable_name = f"ahootsa_profile_play_emotion_for_memory_{profile}_{stamp}"
            if stable_name in sys.modules:
                return sys.modules[stable_name]
            spec = importlib.util.spec_from_file_location(stable_name, path)
            if not (spec and spec.loader):
                continue
            mod = importlib.util.module_from_spec(spec)
            sys.modules[stable_name] = mod
            spec.loader.exec_module(mod)
            return mod
    raise ModuleNotFoundError("No existe play_emotion.py en perfiles Ahootsa")


def _game():
    mod = _load_sibling_module("memory_pairs_game_server", "memory_pairs_game_server.py")
    if not hasattr(mod, "start_server"):
        raise AttributeError("memory_pairs_game_server.py cargado, pero no contiene start_server().")
    return mod


def _json_config(filename: str, default: dict[str, Any]) -> dict[str, Any]:
    path = Path(__file__).resolve().with_name(filename)
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                merged = dict(default)
                merged.update(data)
                return merged
    except Exception:
        pass
    return default


def _feedback_config() -> dict[str, Any]:
    return _json_config(
        "memory_feedback_config.json",
        {
            "duplicate_guard_seconds": 6.0,
            "play_reaction_emotion": True,
            "reaction_sound": True,
            "emotions": {"match": "success", "miss": "calming", "repeat_miss": "thinking", "final": "dance3", "invalid": "confused"},
            "post_wait_seconds": {"match": 0.2, "miss": 0.2, "repeat_miss": 0.2, "final": 0.2, "invalid": 0.0},
        },
    )


def _direct_config() -> dict[str, Any]:
    return _json_config(
        "memory_direct_response_config.json",
        {
            "background_reaction_delay_seconds": 2.8,
            "winsound_fallback": True,
            "winsound": {
                "miss": [[220, 130], [180, 160]],
                "match": [[660, 100], [880, 120]],
                "final": [[660, 100], [880, 120], [1040, 140]],
                "repeat_miss": [[330, 120]],
                "invalid": [[300, 120]],
            },
        },
    )


def _winsound_feedback(kind: str) -> dict[str, Any]:
    cfg = _direct_config()
    if not bool(cfg.get("winsound_fallback", True)):
        return {"ok": False, "skipped": True, "reason": "winsound_fallback disabled"}
    try:
        import winsound  # Windows only
        pattern = (cfg.get("winsound") or {}).get(kind) or [[300, 120]]
        for freq, dur in pattern:
            winsound.Beep(int(freq), int(dur))
        return {"ok": True, "backend": "winsound", "kind": kind}
    except BaseException as exc:
        _log_exc("choose_memory_cards.winsound", exc, {"kind": kind})
        return {"ok": False, "backend": "winsound", "error": f"{type(exc).__name__}: {exc}"}


async def _play_reaction_now(deps: ToolDependencies, kind: str) -> dict[str, Any]:
    cfg = _feedback_config()
    if not cfg.get("play_reaction_emotion", True):
        return {"ok": False, "skipped": True, "reason": "play_reaction_emotion disabled"}

    emotion = (cfg.get("emotions") or {}).get(kind)
    if not emotion:
        return {"ok": False, "skipped": True, "reason": f"no emotion for {kind}"}

    sound = bool(cfg.get("reaction_sound", True))
    wait_seconds = float((cfg.get("post_wait_seconds") or {}).get(kind, 0.2))

    try:
        # 7.0.17: do not expect tools/play_emotion.py. It would collide with
        # the official Reachy built-in play_emotion. Load the Ahootsa profile
        # implementation explicitly.
        pe = _load_profile_play_emotion()
        tool = pe.PlayEmotion()
        result = await tool(
            deps,
            emotion=emotion,
            sound=sound,
            delay_before_play_seconds=0,
            post_play_wait_seconds=wait_seconds,
        )
        if isinstance(result, dict):
            result["memory_reaction_kind"] = kind
            result["memory_reaction_requested_sound"] = sound
        return result if isinstance(result, dict) else {"ok": True, "raw": str(result)}
    except BaseException as exc:
        _log_exc("choose_memory_cards.reaction", exc, {"kind": kind, "emotion": emotion})
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "emotion": emotion}


async def _delayed_reaction(deps: ToolDependencies, kind: str, delay: float) -> None:
    try:
        _log_event("memory_reaction_scheduled", {"kind": kind, "delay": delay})
        await asyncio.sleep(max(0.0, float(delay)))
        reaction_result = await _play_reaction_now(deps, kind)
        beep_result = _winsound_feedback(kind)
        _log_event("memory_reaction_background_result", {"kind": kind, "reaction_result": reaction_result, "beep_result": beep_result})
    except BaseException as exc:
        _log_exc("choose_memory_cards.delayed_reaction", exc, {"kind": kind})


def _schedule_reaction(deps: ToolDependencies, kind: str) -> dict[str, Any]:
    delay = float(_direct_config().get("background_reaction_delay_seconds", 2.8))
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_delayed_reaction(deps, kind, delay))
        return {"ok": True, "scheduled": True, "delay_seconds": delay, "kind": kind}
    except BaseException as exc:
        _log_exc("choose_memory_cards.schedule_reaction", exc, {"kind": kind})
        # Last resort: at least beep synchronously.
        beep_result = _winsound_feedback(kind)
        return {"ok": False, "scheduled": False, "error": f"{type(exc).__name__}: {exc}", "beep_result": beep_result}



async def _run_reaction_before_speech(deps: ToolDependencies, kind: str) -> dict[str, Any]:
    """Ejecuta primero movimiento/sonido y devuelve luego para que el backend hable después."""
    result: dict[str, Any] = {"ok": True, "kind": kind, "mode": "effect_then_spoken_feedback_7_0_17"}
    try:
        reaction_result = await _play_reaction_now(deps, kind)
        result["reaction_result"] = reaction_result
    except BaseException as exc:
        _log_exc("choose_memory_cards.inline_reaction", exc, {"kind": kind})
        result["reaction_result"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    try:
        result["beep_result"] = _winsound_feedback(kind)
    except BaseException as exc:
        result["beep_result"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    return result


def _with_direct_response_fields(payload: dict[str, Any], message: str) -> dict[str, Any]:
    # Different official-app versions look at different keys. Fill all common variants.
    payload["message"] = message
    payload["text"] = message
    payload["answer"] = message
    payload["content"] = message
    payload["response"] = message
    payload["final_response"] = message
    payload["spoken_response"] = message
    payload["tts_text"] = message
    payload["message_for_user"] = message
    payload["robot_say"] = message
    payload["assistant_response"] = message
    payload["speak"] = message
    payload["say"] = message
    payload["tool_summary"] = message
    return payload


_LAST_REQUEST_SIGNATURE: tuple[int, int] | None = None
_LAST_REQUEST_TS: float = 0.0
_LAST_REQUEST_RESULT: dict[str, Any] | None = None


class ChooseMemoryCards(Tool):
    name = "choose_memory_cards"
    description = (
        "Levanta dos cartas del Memory activo. Devuelve una respuesta directa para decir al usuario "
        "ejecuta primero la reacción emocional/sonido y después devuelve el texto que debe decir Ahootsa."
    )
    needs_response = True

    parameters_schema = {
        "type": "object",
        "properties": {
            "first_card": {"type": "integer", "minimum": 1, "maximum": 8},
            "second_card": {"type": "integer", "minimum": 1, "maximum": 8},
        },
        "required": ["first_card", "second_card"],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        global _LAST_REQUEST_SIGNATURE, _LAST_REQUEST_TS, _LAST_REQUEST_RESULT
        _log_start("choose_memory_cards", kwargs)

        try:
            first = int(kwargs.get("first_card"))
            second = int(kwargs.get("second_card"))
            signature = tuple(sorted((first, second)))
            now = time.time()
            duplicate_window = float(_feedback_config().get("duplicate_guard_seconds", 6.0))

            if (
                _LAST_REQUEST_SIGNATURE == signature
                and _LAST_REQUEST_RESULT is not None
                and now - _LAST_REQUEST_TS < duplicate_window
            ):
                message = "No eran pareja. Inténtalo otra vez con otros dos números."
                duplicate = {
                    "ok": True,
                    "result": "duplicate_ignored",
                    "duplicate_ignored": True,
                    "matched": False,
                    "memory_reaction_mode": "effect_then_spoken_feedback_7_0_17",
                    "robot_next_instruction": "Di text de forma natural. No llames a otra emoción ni a otro dance.",
                }
                _with_direct_response_fields(duplicate, message)
                _log_result("choose_memory_cards", duplicate)
                return duplicate

            _LAST_REQUEST_SIGNATURE = signature
            _LAST_REQUEST_TS = now

            raw = _game().choose_cards(first, second)
            state = raw.get("state") or {}
            raw_result = raw.get("result")

            # 7.0.17: no decir "Vamos a ver..." porque la imagen ya está visible
            # en el iframe. La respuesta oral debe ser breve: acierto/fallo y ánimo.
            reaction_kind = "invalid"

            if raw_result == "repeat_miss":
                reaction_kind = "repeat_miss"
                message = "No eran pareja. Inténtalo otra vez con otros dos números."
            elif raw_result == "final" or state.get("finished"):
                reaction_kind = "final"
                message = "¡Felicidades! Has terminado el juego. Lo has hecho muy bien. ¿Quieres volver a jugar o prefieres salir?"
            elif raw.get("matched") or raw_result in {"match", "matched"}:
                reaction_kind = "match"
                message = "¡Muy bien! Es pareja. Lo has hecho genial. Sigue así y elige otros dos números."
            elif raw_result == "miss":
                reaction_kind = "miss"
                message = raw.get("message_for_user") or "No eran pareja. Inténtalo otra vez con otros dos números."
            elif raw.get("ok"):
                reaction_kind = "invalid"
                message = "Elige dos números del 1 al 8 cuando quieras continuar."
            else:
                reaction_kind = "invalid"
                message = raw.get("message_for_user") or "No he podido levantar esas cartas. Prueba otra vez con dos números del 1 al 8."

            reaction_schedule = await _run_reaction_before_speech(deps, reaction_kind)

            result = {
                "ok": bool(raw.get("ok", True)),
                "result": raw_result,
                "matched": bool(raw.get("matched", False)),
                "reaction_kind": reaction_kind,
                "reaction_schedule": reaction_schedule,
                "state_summary": {
                    "game_id": state.get("game_id"),
                    "last_result": state.get("last_result"),
                    "last_move_id": state.get("last_move_id"),
                    "matches": state.get("matches"),
                    "total_pairs": state.get("total_pairs"),
                    "finished": state.get("finished"),
                },
                "memory_reaction_mode": "effect_then_spoken_feedback_7_0_17",
                "robot_next_instruction": (
                    "Responde al usuario con el campo text exactamente. "
                    "No llames a play_emotion, play_emotion_with_audio, play_panel_dance_activity ni dance después. "
                    "Esta herramienta ya ha ejecutado la reacción antes de que hables."
                ),
            }
            _with_direct_response_fields(result, message)
            if reaction_kind == "final":
                result["suggested_next_actions"] = [
                    "Si el usuario dice 'otra vez' o 'volver a jugar', llama a start_memory_pairs_game con el mismo juego.",
                    "Si el usuario dice salir, despídete brevemente. Si pide otra actividad, usa list_communication_activity_levels."
                ]

            _LAST_REQUEST_RESULT = copy.deepcopy(result)
            _log_result("choose_memory_cards", result)
            return result

        except BaseException as exc:
            _log_exc("choose_memory_cards", exc, kwargs)
            result = {"ok": False, "error": f"{type(exc).__name__}: {exc}", "memory_reaction_mode": "direct_response_delayed_sound_7_0_17"}
            _with_direct_response_fields(result, "Ha fallado la jugada. No pasa nada. Debes decir dos números del 1 al 8.")
            return result
