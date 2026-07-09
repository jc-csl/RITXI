# AHOOTSA_5_0_7_DIRECT_MEMORY_RESPONSE: evita bloqueo post-tool.
from __future__ import annotations
# AHOOTSA_5_0_10_TOOL_LOG
try:
    from ahootsa_logging import log_event
except Exception:
    def log_event(*a, **k): pass

import importlib.util
import os
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


def _game():
    mod = _load_sibling_module("memory_pairs_game_server", "memory_pairs_game_server.py")
    if not hasattr(mod, "start_server"):
        raise AttributeError("memory_pairs_game_server.py cargado, pero no contiene start_server().")
    return mod


class StartMemoryPairsGame(Tool):
    name = "start_memory_pairs_game"
    description = "Lanza un juego Memory visual de buscar parejas y pide dos números."
    needs_response = True

    parameters_schema = {
        "type": "object",
        "properties": {
            "game_id": {"type": "string", "default": "animales", "description": "Juego: animales, ciudades, alimentos. También acepta parejas, memory, cartas."},
            "reset": {"type": "boolean", "default": True},
            "open_browser": {"type": "boolean", "default": True},
            "port": {"type": "integer", "default": 7870},
        },
        "required": [],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        _log_start("start_memory_pairs_game", kwargs)
        try:
            game_id = kwargs.get("game_id", "animales")
            try:
                if hasattr(_game(), "_safe_game_id"):
                    game_id = _game()._safe_game_id(game_id)
            except Exception:
                pass
            if os.getenv("AHOOTSA_MEMORY_INTEGRATED", "1").lower() not in {"0", "false", "no", "off"}:
                # 7.0.21: el juego se abre integrado en la app Ahootsa (puerto 7860).
                # Evita problemas de apertura externa/puerto 7870 en Desktop Control.
                game_mod = _game()
                if bool(kwargs.get("reset", True)):
                    game_mod.reset_game(game_id)
                base = os.getenv("AHOOTSA_APP_BASE_URL", "http://127.0.0.1:7860").rstrip("/")
                url = f"{base}/memory/page?game_id={game_id}&reset=0"
                result = {"ok": True, "url": url, "port": 7860, "integrated": True, "games": game_mod.available_games(), "state": game_mod.status().get("state")}
            else:
                result = _game().start_server(
                    port=int(kwargs.get("port", 7870)),
                    open_browser=bool(kwargs.get("open_browser", True)),
                    reset=bool(kwargs.get("reset", True)),
                    game_id=game_id,
                )
            message = (
                f"He preparado el juego de {game_id} en el panel Ahootsa. "
                "Elige dos números del 1 al 8. Por ejemplo: tres y cinco."
            )
            compact = {
                "ok": bool(result.get("ok", True)),
                "url": result.get("url"),
                "port": result.get("port", 7870),
                "game_id": game_id,
                "message_for_user": message,
                "robot_say": message,
                "assistant_response": message,
                "speak": message,
                "robot_next_instruction": "Di robot_say. Después espera a que el usuario diga dos números del 1 al 8.",
                "memory_interaction_mode": "feedback_emotion_sound_restored_v0_4_57_2",
            }
            _log_result("start_memory_pairs_game", compact)
            return compact
        except BaseException as exc:
            _log_exc("start_memory_pairs_game", exc, kwargs)
            return {
                "ok": False,
                "error": f"{type(exc).__name__}: {exc}",
                "message_for_user": "No he podido abrir el juego. Revisa el diagnóstico de Ahootsa.",
                "robot_say": "No he podido abrir el juego. Revisa el diagnóstico de Ahootsa.",
                "assistant_response": "No he podido abrir el juego. Revisa el diagnóstico de Ahootsa.",
            }
