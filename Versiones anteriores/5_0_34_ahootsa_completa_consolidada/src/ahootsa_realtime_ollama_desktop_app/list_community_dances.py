"""List Ahootsa community dances from pollen-robotics/reachy-mini-dances-library."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies

DATASET_ID = "pollen-robotics/reachy-mini-dances-library"
DEFAULT_LOCAL_DIR = Path(r"D:\RITXI\reachy-mini-dances-library")


def _config_path() -> Path:
    return Path(__file__).resolve().with_name("community_dances.json")


def _load_config() -> dict[str, Any]:
    path = _config_path()
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"dataset": DATASET_ID, "moves": []}


def _is_valid_dataset_dir(path: Path) -> bool:
    try:
        return path.exists() and path.is_dir() and any(path.glob("*.json"))
    except Exception:
        return False


def find_dances_dataset_dir() -> Path | None:
    explicit = os.getenv("AHOOTSA_DANCES_LIBRARY_DIR", "").strip()
    if explicit and _is_valid_dataset_dir(Path(explicit)):
        return Path(explicit)

    if _is_valid_dataset_dir(DEFAULT_LOCAL_DIR):
        return DEFAULT_LOCAL_DIR

    # Hugging Face cache patterns
    candidates: list[Path] = []
    home = Path.home()
    candidates.append(home / ".cache" / "huggingface" / "hub" / "datasets--pollen-robotics--reachy-mini-dances-library" / "snapshots")
    local = os.getenv("LOCALAPPDATA")
    if local:
        candidates.append(Path(local) / "huggingface" / "hub" / "datasets--pollen-robotics--reachy-mini-dances-library" / "snapshots")
        candidates.append(Path(local) / "Reachy Mini Control")

    for root in candidates:
        try:
            if root.exists():
                hits = sorted(root.rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
                for hit in hits:
                    if hit.name in {"simple_nod.json", "yeah_nod.json", "chicken_peck.json"} and _is_valid_dataset_dir(hit.parent):
                        return hit.parent
        except Exception:
            pass

    return None


def configured_moves() -> list[dict[str, Any]]:
    return list(_load_config().get("moves", []))


def available_json_moves() -> list[str]:
    ds = find_dances_dataset_dir()
    if not ds:
        return []
    return sorted(p.stem for p in ds.glob("*.json"))


class ListCommunityDances(Tool):
    name = "list_community_dances"
    description = "Lista los dances/movimientos comunitarios disponibles para Ahootsa."
    needs_response = True
    parameters_schema = {"type": "object", "properties": {}, "required": []}

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        cfg = configured_moves()
        available = set(available_json_moves())
        items = []
        for move in cfg:
            mid = move.get("id")
            items.append({
                "id": mid,
                "name_es": move.get("name_es", mid),
                "available": bool(mid in available) if available else None,
                "aliases": move.get("aliases", []),
            })
        return {
            "ok": True,
            "dataset": DATASET_ID,
            "dataset_dir": str(find_dances_dataset_dir()) if find_dances_dataset_dir() else None,
            "count_configured": len(items),
            "count_available_json": len(available),
            "moves": items,
            "message_for_user": "Puedo hacer dances como simple_nod, yeah_nod, chicken_peck, dizzy_spin o groovy_sway_and_roll.",
        }
