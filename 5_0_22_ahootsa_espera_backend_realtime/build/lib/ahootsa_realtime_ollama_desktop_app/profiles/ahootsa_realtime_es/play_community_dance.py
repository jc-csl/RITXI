"""Play Ahootsa community dances from pollen-robotics/reachy-mini-dances-library.

The dataset is motion-only JSON. There is no audio sidecar in this library.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import random
import sys
from pathlib import Path
from typing import Any

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies

DATASET_ID = "pollen-robotics/reachy-mini-dances-library"
DEFAULT_LOCAL_DIR = Path(r"D:\RITXI\reachy-mini-dances-library")

def _load_play_timing_config() -> dict[str, Any]:
    try:
        path = Path(__file__).resolve().with_name("play_timing_config.json")
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _ahootsa_action_delay_seconds(kwargs: dict[str, Any] | None = None) -> float:
    kwargs = kwargs or {}
    raw = kwargs.get("delay_before_play_seconds")
    if raw is None:
        raw = os.getenv("AHOOTSA_ACTION_PLAY_DELAY_SECONDS")
    if raw is None or str(raw).strip() == "":
        raw = _load_play_timing_config().get("action_play_delay_seconds", 0.0)
    try:
        value = float(raw)
    except Exception:
        value = 0.0
    return max(0.0, min(10.0, value))


def _ahootsa_post_play_wait_seconds(kwargs: dict[str, Any] | None = None) -> float:
    kwargs = kwargs or {}
    raw = kwargs.get("post_play_wait_seconds")
    if raw is None:
        raw = os.getenv("AHOOTSA_POST_PLAY_WAIT_SECONDS")
    if raw is None or str(raw).strip() == "":
        raw = _load_play_timing_config().get("post_play_wait_seconds", 3.0)
    try:
        value = float(raw)
    except Exception:
        value = 3.0
    return max(0.0, min(20.0, value))





def _load_list_module():
    path = Path(__file__).resolve().with_name("list_community_dances.py")
    name = "ahootsa_list_community_dances_runtime"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if not (spec and spec.loader):
        raise ModuleNotFoundError("No se puede cargar list_community_dances.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _normalize(text: object) -> str:
    return str(text or "").strip().lower().replace(" ", "_").replace("-", "_")


def _resolve_move(requested: object) -> str:
    mod = _load_list_module()
    cfg = mod.configured_moves()
    available = set(mod.available_json_moves())
    text = _normalize(requested)

    if not text or text == "random":
        pool = [m["id"] for m in cfg if not available or m["id"] in available]
        return random.choice(pool or [m["id"] for m in cfg])

    # exact id
    for move in cfg:
        mid = _normalize(move.get("id"))
        if text == mid:
            return move["id"]

    # aliases / Spanish names
    for move in cfg:
        if text == _normalize(move.get("name_es")):
            return move["id"]
        for alias in move.get("aliases", []):
            if text == _normalize(alias):
                return move["id"]

    # forgiving contains
    for move in cfg:
        hay = [move.get("id", ""), move.get("name_es", "")] + list(move.get("aliases", []))
        if any(text in _normalize(x) or _normalize(x) in text for x in hay if x):
            return move["id"]

    # common spoken mappings
    if text in {"asiente", "asentir", "si", "sí", "dime_que_si"}:
        return "yeah_nod"
    if text in {"baile", "baila", "dance"}:
        return "groovy_sway_and_roll"
    if text in {"saluda", "hola"}:
        return "simple_nod"

    return text


def _patch_recorded_moves_snapshot_download(local_dir: Path) -> None:
    try:
        import reachy_mini.motion.recorded_move as recorded_move_module
        if getattr(recorded_move_module, "_ahootsa_dances_snapshot_patch", False):
            return
        original_snapshot_download = recorded_move_module.snapshot_download
        local_str = str(local_dir)
        local_resolved = str(local_dir.resolve())

        def ahootsa_snapshot_download(repo_id: str, *args: Any, **kwargs: Any) -> str:
            value = str(repo_id)
            if value in {DATASET_ID, local_str, local_resolved}:
                return local_resolved
            return original_snapshot_download(repo_id, *args, **kwargs)

        recorded_move_module.snapshot_download = ahootsa_snapshot_download
        recorded_move_module._ahootsa_dances_snapshot_patch = True
    except Exception:
        pass


class PlayCommunityDance(Tool):
    name = "play_community_dance"
    description = (
        "Reproduce un dance/movimiento comunitario de Reachy Mini. "
        "Ejemplos: simple_nod, yeah_nod, chicken_peck, dizzy_spin, groovy_sway_and_roll. "
        "La librería de dances es solo movimiento, sin audio."
    )
    needs_response = False

    parameters_schema = {
        "type": "object",
        "properties": {
            "dance": {
                "type": "string",
                "description": "Nombre o alias del dance. Usa list_community_dances para ver opciones.",
                "default": "random",
            }
        },
        "required": [],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        mod = _load_list_module()
        dataset_dir = mod.find_dances_dataset_dir()
        if not dataset_dir:
            return {
                "ok": False,
                "error": "No encuentro reachy-mini-dances-library. Ejecuta INSTALAR_DANCES_LIBRARY_AHOOTSA.ps1.",
                "dataset": DATASET_ID,
            }

        move_name = _resolve_move(kwargs.get("dance", "random"))
        json_path = Path(dataset_dir) / f"{move_name}.json"
        if not json_path.exists():
            return {
                "ok": False,
                "error": f"No existe {move_name}.json en la librería de dances.",
                "dance": move_name,
                "dataset_dir": str(dataset_dir),
            }

        delay_seconds = _ahootsa_action_delay_seconds(kwargs)
        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)

        try:
            from reachy_mini.motion.recorded_move import RecordedMoves
            from reachy_mini_conversation_app.dance_emotion_moves import EmotionQueueMove
            _patch_recorded_moves_snapshot_download(Path(dataset_dir))
            library = RecordedMoves(DATASET_ID)
            deps.movement_manager.queue_move(EmotionQueueMove(move_name, library))
            post_wait_seconds = _ahootsa_post_play_wait_seconds(kwargs)
            if post_wait_seconds > 0:
                await asyncio.sleep(post_wait_seconds)
            return {
                "ok": True,
                "dance": move_name,
                "dataset": DATASET_ID,
                "dataset_dir": str(dataset_dir),
                "audio": "none: dances-library is motion-only",
                "message_for_user": "",
            }
        except Exception as exc:
            return {
                "ok": False,
                "dance": move_name,
                "dataset_dir": str(dataset_dir),
                "error": f"{type(exc).__name__}: {exc}",
            }
