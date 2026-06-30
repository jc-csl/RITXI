from __future__ import annotations

import importlib.util
import sys
import time
import asyncio
import copy
from pathlib import Path
from typing import Any

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies


def _load_sibling_module(module_name: str, filename: str):
    path = Path(__file__).resolve().with_name(filename)
    if not path.exists():
        raise ModuleNotFoundError(f"No existe {filename} en {Path(__file__).resolve().parent}")

    try:
        stamp = str(int(path.stat().st_mtime_ns))
    except Exception:
        stamp = str(int(time.time() * 1000))
    stable_name = f"ahootsa_{module_name}_{stamp}"

    if stable_name in sys.modules:
        return sys.modules[stable_name]

    spec = importlib.util.spec_from_file_location(stable_name, path)
    if not (spec and spec.loader):
        raise ModuleNotFoundError(f"No se puede cargar {filename}")

    mod = importlib.util.module_from_spec(spec)
    sys.modules[stable_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _game():
    mod = _load_sibling_module("memory_pairs_game_server", "memory_pairs_game_server.py")
    if not hasattr(mod, "start_server"):
        raise AttributeError(
            "memory_pairs_game_server.py cargado, pero no contiene start_server(). "
            "Cierra Reachy Mini Desktop y ejecuta REPARAR_MEMORY_START_SERVER.ps1."
        )
    return mod


async def _emotion(deps: ToolDependencies, emotion: str) -> dict[str, Any] | None:
    """Run exactly one emotion/audio action for the current Memory move."""
    try:
        # Prefer the explicit audio wrapper if installed.
        try:
            pe_audio = _load_sibling_module("play_emotion_with_audio_for_game", "play_emotion_with_audio.py")
            tool = pe_audio.PlayEmotionWithAudio()
            return await tool(deps, emotion=emotion)
        except Exception:
            pe = _load_sibling_module("play_emotion_for_game", "play_emotion.py")
            tool = pe.PlayEmotion()
            return await tool(deps, emotion=emotion, sound=True)
    except Exception as exc:
        return {"ok": False, "error": repr(exc)}


_LAST_REACTED_MOVE_ID: int | None = None
_LAST_REQUEST_SIGNATURE: tuple[int, int] | None = None
_LAST_REQUEST_TS: float = 0.0
_LAST_REQUEST_RESULT: dict[str, Any] | None = None
_DUPLICATE_WINDOW_SECONDS = 8.0


class ChooseMemoryCards(Tool):
    name = "choose_memory_cards"
    description = (
        "Levanta dos cartas del memory activo. "
        "Úsalo inmediatamente cuando el usuario diga dos números. "
        "IMPORTANTE: esta herramienta ya hace una única reacción del robot; "
        "después no llames a play_emotion, play_emotion_with_audio ni dance."
    )
    needs_response = True

    parameters_schema = {
        "type": "object",
        "properties": {
            "first_card": {"type": "integer", "minimum": 1, "maximum": 8},
            "second_card": {"type": "integer", "minimum": 1, "maximum": 8},
            "post_flip_delay_seconds": {
                "type": "number",
                "description": "Pausa después de girar cartas antes de reaccionar.",
                "default": 1.2,
            },
        },
        "required": ["first_card", "second_card"],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        global _LAST_REACTED_MOVE_ID, _LAST_REQUEST_SIGNATURE, _LAST_REQUEST_TS, _LAST_REQUEST_RESULT

        first = int(kwargs.get("first_card"))
        second = int(kwargs.get("second_card"))
        post_flip_delay = float(kwargs.get("post_flip_delay_seconds", 1.2))
        signature = tuple(sorted((first, second)))
        now = time.time()

        # Guard against the realtime model/orchestrator calling the same tool twice
        # for one spoken instruction. This was causing double movement + double sound.
        if (
            _LAST_REQUEST_SIGNATURE == signature
            and _LAST_REQUEST_RESULT is not None
            and now - _LAST_REQUEST_TS < _DUPLICATE_WINDOW_SECONDS
        ):
            state_result = _game().status()
            duplicate = copy.deepcopy(_LAST_REQUEST_RESULT)
            duplicate["ok"] = True
            duplicate["result"] = "duplicate_ignored"
            duplicate["duplicate_ignored"] = True
            duplicate["message_for_user"] = "Ya he levantado esas cartas. No repito el movimiento."
            duplicate["robot_say"] = ""
            duplicate["robot_next_instruction"] = (
                "No llames a ninguna herramienta más. No repitas emoción, sonido ni movimiento."
            )
            if isinstance(state_result, dict) and "state" in state_result:
                duplicate["state"] = state_result["state"]
            return duplicate

        _LAST_REQUEST_SIGNATURE = signature
        _LAST_REQUEST_TS = now

        # Flip the cards immediately. The web view polls /state and will show them.
        result = _game().choose_cards(first, second)
        state = result.get("state") or {}
        move_id = state.get("last_move_id")
        already_reacted = move_id is not None and move_id == _LAST_REACTED_MOVE_ID

        if result.get("result") == "repeat_miss":
            result["robot_say"] = ""
            result["robot_next_instruction"] = (
                "No llames a ninguna herramienta más. Las cartas ya están visibles."
            )
            _LAST_REQUEST_RESULT = copy.deepcopy(result)
            return result

        # Wait a little so the cards appear before the movement/sound starts.
        if post_flip_delay > 0:
            await asyncio.sleep(post_flip_delay)

        # A single reaction per server move_id.
        if already_reacted:
            result["robot_next_instruction"] = (
                "No llames a ninguna herramienta más. La reacción de este movimiento ya se hizo."
            )
            _LAST_REQUEST_RESULT = copy.deepcopy(result)
            return result

        _LAST_REACTED_MOVE_ID = move_id

        prefix = f"Vamos a ver la {first} y la {second}. "

        if result.get("result") == "final" or state.get("finished"):
            emotion_result = await _emotion(deps, "celebration")
            result["emotion_result"] = emotion_result
            result["message_for_user"] = (
                prefix
                + "¡Muy bien! Has terminado el juego. "
                + "¿Quieres jugar otra vez o prefieres hacer otra actividad?"
            )
            result["robot_say"] = result["message_for_user"]
            result["robot_next_instruction"] = (
                "Solo di la respuesta. No llames a play_emotion, play_emotion_with_audio ni dance."
            )

        elif result.get("matched"):
            emotion_result = await _emotion(deps, "success")
            result["emotion_result"] = emotion_result
            base = result.get("message_for_user") or "¡Muy bien! Es pareja."
            result["message_for_user"] = prefix + base + " Dime otros dos números."
            result["robot_say"] = result["message_for_user"]
            result["robot_next_instruction"] = (
                "Solo di la respuesta. No llames a play_emotion, play_emotion_with_audio ni dance."
            )

        elif result.get("result") == "miss":
            emotion_result = await _emotion(deps, "calming")
            result["emotion_result"] = emotion_result
            base = result.get("message_for_user") or "Casi. No son pareja."
            result["message_for_user"] = prefix + base + " Las dejamos visibles cuatro segundos."
            result["robot_say"] = result["message_for_user"]
            result["robot_next_instruction"] = (
                "Solo di la respuesta. No llames a play_emotion, play_emotion_with_audio ni dance."
            )

        elif result.get("ok"):
            # Invalid/neutral cases: no expressive motion to avoid extra noise.
            result["message_for_user"] = prefix + (result.get("message_for_user") or "Mira las cartas.")
            result["robot_say"] = result["message_for_user"]
            result["robot_next_instruction"] = (
                "Solo di la respuesta. No llames a play_emotion, play_emotion_with_audio ni dance."
            )

        _LAST_REQUEST_RESULT = copy.deepcopy(result)
        return result
