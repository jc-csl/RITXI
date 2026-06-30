
from __future__ import annotations

import importlib.util
import sys
import time
import asyncio
from pathlib import Path
from typing import Any

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies


def _load_sibling_module(module_name: str, filename: str):
    path = Path(__file__).resolve().with_name(filename)
    if not path.exists():
        raise ModuleNotFoundError(f"No existe {filename} en {Path(__file__).resolve().parent}")

    # Important: include file mtime in module name to avoid stale cached modules
    # after installing a new Ahootsa version while Desktop/runner is still alive.
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


async def _emotion(deps: ToolDependencies, emotion: str) -> None:
    try:
        pe = _load_sibling_module("play_emotion_for_game", "play_emotion.py")
        tool = pe.PlayEmotion()
        await tool(deps, emotion=emotion, sound=True)
    except Exception:
        return

_LAST_REACTED_MOVE_ID: int | None = None


class ChooseMemoryCards(Tool):
    name = "choose_memory_cards"
    description = (
        "Levanta dos cartas del memory activo. "
        "Úsalo inmediatamente cuando el usuario diga dos números. "
        "No esperes a hablar antes de llamar a esta herramienta."
    )
    needs_response = True

    parameters_schema = {
        "type": "object",
        "properties": {
            "first_card": {"type": "integer", "minimum": 1, "maximum": 8},
            "second_card": {"type": "integer", "minimum": 1, "maximum": 8},
            "post_flip_delay_seconds": {
                "type": "number",
                "description": "Pausa breve después de girar cartas antes de reaccionar.",
                "default": 0.7,
            },
        },
        "required": ["first_card", "second_card"],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        global _LAST_REACTED_MOVE_ID

        first = int(kwargs.get("first_card"))
        second = int(kwargs.get("second_card"))
        post_flip_delay = float(kwargs.get("post_flip_delay_seconds", 0.7))

        # IMPORTANT: flip cards immediately.
        result = _game().choose_cards(first, second)
        state = result.get("state") or {}
        move_id = state.get("last_move_id")
        already_reacted = move_id is not None and move_id == _LAST_REACTED_MOVE_ID

        if result.get("result") == "repeat_miss":
            result["robot_next_instruction"] = "No repitas la reacción. Las cartas ya están visibles."
            result["message_for_user"] = "Esas cartas ya están visibles. Mira con calma."
            result["robot_say"] = ""
            return result

        # Let the web view show the cards before the emotion/reaction starts.
        if post_flip_delay > 0:
            await asyncio.sleep(post_flip_delay)

        if already_reacted:
            result["robot_next_instruction"] = "No repitas la reacción del robot para este mismo movimiento."
            return result

        _LAST_REACTED_MOVE_ID = move_id

        prefix = f"Vamos a ver la {first} y la {second}. "

        if result.get("result") == "final" or state.get("finished"):
            await _emotion(deps, "celebration")
            result["message_for_user"] = (
                prefix
                + "¡Muy bien! Has terminado el juego. "
                + "¿Quieres jugar otra vez o prefieres hacer otra actividad?"
            )
            result["robot_say"] = result["message_for_user"]
            result["robot_next_instruction"] = (
                "Felicita, pregunta si quiere jugar otra vez o hacer otra actividad. "
                "No resetees todavía si el usuario no lo pide."
            )

        elif result.get("matched"):
            await _emotion(deps, "success")
            base = result.get("message_for_user") or "¡Muy bien! Es pareja."
            result["message_for_user"] = prefix + base + " Dime otros dos números."
            result["robot_say"] = result["message_for_user"]
            result["robot_next_instruction"] = "Felicita una sola vez y pide otros dos números."

        elif result.get("result") == "miss":
            await _emotion(deps, "calming")
            base = result.get("message_for_user") or "Casi. No son pareja."
            result["message_for_user"] = prefix + base + " Las dejamos visibles cuatro segundos."
            result["robot_say"] = result["message_for_user"]
            result["robot_next_instruction"] = (
                "Anima una sola vez. No repitas la reacción. Luego pide otros dos números."
            )

        elif result.get("ok"):
            await _emotion(deps, "thinking")
            result["message_for_user"] = prefix + (result.get("message_for_user") or "Mira las cartas.")
            result["robot_say"] = result["message_for_user"]
            result["robot_next_instruction"] = "Explica con una frase corta y pide otros dos números."

        return result
