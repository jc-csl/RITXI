
from __future__ import annotations

import importlib.util
import sys
import time
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

class MemoryPairsGameStatus(Tool):
    name = "memory_pairs_game_status"
    description = "Consulta el estado actual del juego de parejas y la lista de juegos disponibles."
    needs_response = True

    parameters_schema = {"type": "object", "properties": {}, "required": []}

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        result = _game().status()
        state = result.get("state", {})
        available = ", ".join(g["id"] for g in result.get("games", []))
        result["message_for_user"] = (
            f"Llevas {state.get('matches', 0)} parejas encontradas en {state.get('moves', 0)} movimientos. "
            f"Juegos disponibles: {available}."
        )
        return result
