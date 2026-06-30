from __future__ import annotations

import importlib.util
import sys
import time
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
            "Cierra Reachy Mini Desktop y ejecuta REPARAR_MEMORY_ESTABLE_SIN_BLOQUEO.ps1."
        )
    return mod


_LAST_REQUEST_SIGNATURE: tuple[int, int] | None = None
_LAST_REQUEST_TS: float = 0.0
_LAST_REQUEST_RESULT: dict[str, Any] | None = None
_DUPLICATE_WINDOW_SECONDS = 8.0


class ChooseMemoryCards(Tool):
    name = "choose_memory_cards"
    description = (
        "Levanta dos cartas del memory activo. "
        "Versión estable sin bloqueo: esta herramienta NO ejecuta movimiento ni audio interno. "
        "Solo gira cartas y devuelve la frase para hablar. "
        "Después no llames a play_emotion, play_emotion_with_audio ni dance."
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

        first = int(kwargs.get("first_card"))
        second = int(kwargs.get("second_card"))
        signature = tuple(sorted((first, second)))
        now = time.time()

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
            duplicate["message_for_user"] = "Ya he levantado esas cartas. No repito la jugada."
            duplicate["robot_say"] = ""
            duplicate["robot_next_instruction"] = (
                "No llames a ninguna herramienta más. No repitas emoción, sonido ni movimiento."
            )
            if isinstance(state_result, dict) and "state" in state_result:
                duplicate["state"] = state_result["state"]
            return duplicate

        _LAST_REQUEST_SIGNATURE = signature
        _LAST_REQUEST_TS = now

        # Flip cards immediately. No movement/audio here: keeps the microphone pipeline responsive.
        result = _game().choose_cards(first, second)

        if result.get("result") == "repeat_miss":
            result["robot_say"] = ""
            result["message_for_user"] = "Esas cartas ya están visibles. Míralas con calma."
            result["robot_next_instruction"] = "No llames a ninguna herramienta más."
            _LAST_REQUEST_RESULT = copy.deepcopy(result)
            return result

        prefix = f"Vamos a ver la {first} y la {second}. "
        state = result.get("state") or {}

        if result.get("result") == "final" or state.get("finished"):
            result["message_for_user"] = (
                prefix
                + "¡Muy bien! Has terminado el juego. "
                + "¿Quieres jugar otra vez o prefieres hacer otra actividad?"
            )
        elif result.get("matched"):
            base = result.get("message_for_user") or "¡Muy bien! Es pareja."
            result["message_for_user"] = prefix + base + " Dime otros dos números."
        elif result.get("result") == "miss":
            base = result.get("message_for_user") or "Casi. No son pareja."
            result["message_for_user"] = prefix + base + " Las dejamos visibles cuatro segundos."
        elif result.get("ok"):
            result["message_for_user"] = prefix + (result.get("message_for_user") or "Mira las cartas.")

        result["robot_say"] = result.get("message_for_user", "")
        result["robot_next_instruction"] = (
            "Di solo robot_say. No llames a play_emotion, play_emotion_with_audio ni dance. "
            "No hagas otra herramienta: esta jugada ya está resuelta."
        )
        result["memory_reaction_mode"] = "visual_only_no_blocking_audio"
        _LAST_REQUEST_RESULT = copy.deepcopy(result)
        return result
