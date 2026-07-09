"""List all Ahootsa activities: Memory games, emotions, panel moves, community dances."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies


def _load_sibling(module_name: str, filename: str):
    path = Path(__file__).resolve().with_name(filename)
    name = f"ahootsa_{module_name}_all_activities"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if not (spec and spec.loader):
        raise ModuleNotFoundError(f"No se puede cargar {filename}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _read_json(name: str, default: Any) -> Any:
    path = Path(__file__).resolve().with_name(name)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


class ListAllActivities(Tool):
    name = "list_all_activities"
    description = "Lista todas las actividades de Ahootsa: juegos Memory, emociones, bailes del panel y dances comunitarios."
    needs_response = True

    parameters_schema = {
        "type": "object",
        "properties": {
            "detail": {
                "type": "string",
                "description": "Nivel de detalle: short o full.",
                "default": "short"
            }
        },
        "required": []
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        detail = str(kwargs.get("detail", "short") or "short").lower()

        # Memory games
        memory_games = [
            {"id": "animales", "name_es": "Memory de animales", "tool": "start_memory_pairs_game", "example": "quiero el juego de animales"},
            {"id": "ciudades", "name_es": "Memory de ciudades", "tool": "start_memory_pairs_game", "example": "quiero el juego de ciudades"},
            {"id": "alimentos", "name_es": "Memory de alimentos", "tool": "start_memory_pairs_game", "example": "quiero el juego de alimentos"},
        ]

        emotions_catalog = _read_json("emotions_catalog_es.json", {"emotions": []})
        dances_catalog = _read_json("dances_catalog_es.json", {"dances": []})

        emotions = []
        for e in emotions_catalog.get("emotions", []):
            emotions.append({
                "id": e.get("id"),
                "technical_id": e.get("technical_id"),
                "name_es": e.get("name_es"),
                "category": e.get("category"),
                "tool": e.get("tool", "play_emotion_with_audio"),
                "aliases": e.get("aliases", [])[:6],
            })

        dances = []
        for d in dances_catalog.get("dances", []):
            dances.append({
                "id": d.get("id"),
                "name_es": d.get("name_es"),
                "category": d.get("category"),
                "tool": "play_community_dance",
                "aliases": d.get("aliases", [])[:6],
            })

        panel_examples = [
            {"id": "dance1", "name_es": "baile uno del panel", "tool": "play_panel_dance_activity"},
            {"id": "dance2", "name_es": "baile dos del panel", "tool": "play_panel_dance_activity"},
            {"id": "dance3", "name_es": "baile tres del panel", "tool": "play_panel_dance_activity"},
            {"id": "electric1", "name_es": "movimiento eléctrico", "tool": "play_panel_dance_activity"},
            {"id": "welcoming2", "name_es": "saludo con movimiento", "tool": "play_panel_dance_activity"},
        ]

        if detail != "full":
            emotions_out = emotions[:12]
            dances_out = dances[:12]
        else:
            emotions_out = emotions
            dances_out = dances

        message = (
            "Puedo hacer juegos de parejas de animales, ciudades y alimentos; "
            "emociones como saludo, celebración, calma, pensar y sorpresa; "
            "y dances como asentir, baile de gallina, giro mareado o baile groovy."
        )

        return {
            "ok": True,
            "message_for_user": message,
            "memory_games": memory_games,
            "emotions_count": len(emotions),
            "emotions": emotions_out,
            "panel_activities_examples": panel_examples,
            "community_dances_count": len(dances),
            "community_dances": dances_out,
            "how_to_ask_examples": [
                "¿Qué actividades sabes hacer?",
                "Dime tus emociones.",
                "Lista tus dances comunitarios.",
                "Quiero el juego de animales.",
                "Haz el baile de gallina.",
                "Haz una emoción de calma.",
            ],
        }

# Actividades de comunicación: fácil, normal y avanzada. Usa list_communication_activity_levels y list_communication_activities.
