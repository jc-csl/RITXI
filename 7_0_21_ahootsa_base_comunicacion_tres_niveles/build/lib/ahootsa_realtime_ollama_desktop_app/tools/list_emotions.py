"""List Ahootsa emotions from emotions_catalog_es.json and local emotions library."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies

DATASET_ID = "pollen-robotics/reachy-mini-emotions-library"
DEFAULT_LOCAL_DIR = Path(r"D:\RITXI\reachy-mini-emotions-library")


def _catalog_path() -> Path:
    return Path(__file__).resolve().with_name("emotions_catalog_es.json")


def load_catalog() -> dict[str, Any]:
    path = _catalog_path()
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"dataset": DATASET_ID, "emotions": []}


def _is_valid_dir(path: Path) -> bool:
    try:
        return path.exists() and path.is_dir() and any(path.glob("*.json"))
    except Exception:
        return False


def find_emotions_dataset_dir() -> Path | None:
    explicit = os.getenv("AHOOTSA_EMOTIONS_LIBRARY_DIR", "").strip() or os.getenv("REACHY_MINI_EMOTIONS_LIBRARY_DIR", "").strip()
    if explicit and _is_valid_dir(Path(explicit)):
        return Path(explicit)

    if _is_valid_dir(DEFAULT_LOCAL_DIR):
        return DEFAULT_LOCAL_DIR

    home = Path.home()
    candidates = [
        home / ".cache" / "huggingface" / "hub" / "datasets--pollen-robotics--reachy-mini-emotions-library" / "snapshots"
    ]
    local = os.getenv("LOCALAPPDATA")
    if local:
        candidates.append(Path(local) / "huggingface" / "hub" / "datasets--pollen-robotics--reachy-mini-emotions-library" / "snapshots")
        candidates.append(Path(local) / "Reachy Mini Control")

    for root in candidates:
        try:
            if root.exists():
                hits = sorted(root.rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
                for hit in hits:
                    if hit.name in {"welcoming2.json", "success1.json", "calming1.json"} and _is_valid_dir(hit.parent):
                        return hit.parent
        except Exception:
            pass
    return None


def available_emotion_json() -> list[str]:
    ds = find_emotions_dataset_dir()
    if not ds:
        return []
    return sorted(p.stem for p in ds.glob("*.json"))


def available_emotion_audio() -> list[str]:
    ds = find_emotions_dataset_dir()
    if not ds:
        return []
    stems = set()
    for ext in ("*.ogg", "*.opus", "*.wav", "*.mp3"):
        stems.update(p.stem for p in ds.glob(ext))
    return sorted(stems)


def catalog_items() -> list[dict[str, Any]]:
    return list(load_catalog().get("emotions", []))


class ListEmotions(Tool):
    name = "list_emotions"
    description = "Lista emociones y reacciones disponibles de Ahootsa, con nombres en español y disponibilidad local."
    needs_response = True

    parameters_schema = {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Categoría opcional: saludos, positivas, calma_apoyo, cognitivas, sorpresa, negativas_suaves, bailes_emociones.",
                "default": ""
            },
            "only_available": {
                "type": "boolean",
                "description": "Mostrar solo las que tienen JSON local detectado.",
                "default": False
            }
        },
        "required": []
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        category = str(kwargs.get("category", "") or "").strip()
        only_available = bool(kwargs.get("only_available", False))

        json_available = set(available_emotion_json())
        audio_available = set(available_emotion_audio())

        items = []
        for item in catalog_items():
            if category and item.get("category") != category:
                continue
            technical_id = item.get("technical_id") or item.get("id")
            available = technical_id in json_available if json_available else None
            has_audio = technical_id in audio_available if audio_available else None
            if only_available and available is False:
                continue
            items.append({
                "id": item.get("id"),
                "technical_id": technical_id,
                "name_es": item.get("name_es"),
                "category": item.get("category"),
                "aliases": item.get("aliases", []),
                "tool": item.get("tool", "play_emotion"),
                "available": available,
                "audio_available": has_audio,
                "example_user_requests": item.get("example_user_requests", []),
            })

        message_names = ", ".join(x["name_es"] for x in items[:12] if x.get("name_es"))
        if len(items) > 12:
            message_names += f" y {len(items)-12} más"

        return {
            "ok": True,
            "dataset": DATASET_ID,
            "dataset_dir": str(find_emotions_dataset_dir()) if find_emotions_dataset_dir() else None,
            "count_catalog": len(catalog_items()),
            "count_returned": len(items),
            "count_json_available": len(json_available),
            "count_audio_available": len(audio_available),
            "category_filter": category or None,
            "emotions": items,
            "message_for_user": (
                "Puedo hacer emociones y bailes como " + message_names + ". Puedes pedirlos por nombre en español."
                if message_names else
                "Tengo un catálogo de emociones, pero no he encontrado la librería local de archivos."
            ),
        }
