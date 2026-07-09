# AHOOTSA_5_0_7_DIRECT_RESPONSE: evita bloqueo post-tool con backend realtime/HF.
# AHOOTSA_COMM_TOOL_LOGGING_v0_4_57_8
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies


def _load_catalog() -> dict[str, Any]:
    path = Path(__file__).resolve().with_name("communication_activities_catalog.json")
    if not path.exists():
        return {"levels": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_level(value: object) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    if text in {"facil", "fácil", "sencillo", "bajo", "iniciacion", "iniciación"}:
        return "facil"
    if text in {"normal", "medio", "intermedio"}:
        return "normal"
    if text in {"avanzada", "avanzado", "dificil", "difícil", "alto", "experto"}:
        return "avanzada"
    return text


def _format_activities(level_id: str, level: dict[str, Any], limit: int) -> str:
    label = level.get("label", level_id)
    opening = level.get("opening", f"Estas son actividades de nivel {label}.")
    activities = list(level.get("activities", []))[:max(5, int(limit or 5))]

    lines = [opening, "", f"Actividades {label.lower()}:"]
    for i, act in enumerate(activities, start=1):
        title = act.get("title", f"Actividad {i}")
        goal = act.get("goal", "")
        lines.append(f"{i}. {title}. {goal}")
    lines.append("")
    lines.append("Elige una actividad diciendo su número o su nombre. Vamos paso a paso.")
    return "\n".join(lines)


class ListCommunicationActivities(Tool):
    name = "list_communication_activities"
    description = "Lista al menos cinco actividades de comunicación para un nivel: facil, normal o avanzada."
    needs_response = False

    parameters_schema = {
        "type": "object",
        "properties": {
            "level": {
                "type": "string",
                "description": "Nivel de actividades: facil, normal o avanzada.",
                "enum": ["facil", "normal", "avanzada"],
                "default": "facil",
            },
            "limit": {"type": "integer", "default": 6},
        },
        "required": ["level"],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        catalog = _load_catalog()
        level_id = _normalize_level(kwargs.get("level", "facil"))
        levels = catalog.get("levels", {})

        if level_id not in levels:
            message = "Puedo ofrecer actividades fáciles, normales o avanzadas. ¿Cuál prefieres?"
            return {
                "ok": False,
                "error": "unknown_level",
                "available_levels": ["facil", "normal", "avanzada"],
                "message": message,
                "text": message,
                "answer": message,
                "content": message,
                "final_response": message,
                "spoken_response": message,
                "tts_text": message,
                "robot_say": message,
                "assistant_response": message,
                "speak": message,
            "direct_response": message,
            "tool_summary": message,
            }

        level = levels[level_id]
        limit = int(kwargs.get("limit", 6) or 6)
        message = _format_activities(level_id, level, limit)
        return {
            "ok": True,
            "level": level_id,
            "level_label": level.get("label", level_id),
            "activities": level.get("activities", [])[:max(5, limit)],
            "message": message,
            "text": message,
            "answer": message,
            "content": message,
            "final_response": message,
            "spoken_response": message,
            "tts_text": message,
            "robot_say": message,
            "assistant_response": message,
            "speak": message,
            "direct_response": message,
            "tool_summary": message,
            "robot_next_instruction": "Di text de forma clara. Después espera a que el usuario elija una actividad."
        }
