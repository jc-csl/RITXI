# AHOOTSA_7_0_22_COMMUNICATION_THREE_LEVELS
from __future__ import annotations

import json
from pathlib import Path

from ahootsa_realtime_ollama_desktop_app.resources import data_path
from typing import Any

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies

try:
    from .communication_latency_utils import now_ms, log_event, finish
except Exception:
    from communication_latency_utils import now_ms, log_event, finish  # type: ignore


def _load_catalog() -> dict[str, Any]:
    path = data_path("communication", "communication_activities_catalog.json")
    if not path.exists():
        return {"levels": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_level(value: object) -> str:
    text = str(value or "").strip().lower()
    for a, b in {"á":"a", "é":"e", "í":"i", "ó":"o", "ú":"u", "ü":"u"}.items():
        text = text.replace(a, b)
    if text in {"facil", "faciles", "fácil", "fáciles", "sencillo", "bajo", "iniciacion", "1", "uno"}:
        return "facil"
    if text in {"normal", "normales", "medio", "intermedio", "intermedia", "intermedias", "nivel 2", "2", "dos"}:
        return "normal"
    if text in {"avanzada", "avanzado", "avanzadas", "dificil", "difícil", "alto", "experto", "3", "tres"}:
        return "avanzada"
    return text


def _format_activities(level_id: str, level: dict[str, Any], limit: int) -> str:
    label = level.get("label", level_id)
    opening = level.get("opening", f"Estas son actividades de nivel {label}.")
    activities = list(level.get("activities", []))[:max(4, int(limit or 4))]
    lines = [opening, "", f"Actividades de comunicación · nivel {str(label).lower()}:"]
    for i, act in enumerate(activities, start=1):
        title = act.get("title", f"Actividad {i}")
        goal = act.get("goal", "")
        lines.append(f"{i}. {title}. {goal}")
    lines.append("")
    lines.append("Elige una actividad diciendo su número o su nombre: saludar, pedir comida, mantener turnos o conversar.")
    return "\n".join(lines)


class ListCommunicationActivities(Tool):
    name = "list_communication_activities"
    description = (
        "Lista actividades de comunicación de un nivel: fácil, intermedia o avanzada. "
        "Las actividades principales son saludar, pedir comida, mantener turnos y conversar. "
        "No usa Ollama y debe responder con el texto de la herramienta."
    )
    needs_response = False

    parameters_schema = {
        "type": "object",
        "properties": {
            "level": {"type": "string", "description": "Nivel: facil, intermedia/normal o avanzada.", "enum": ["facil", "intermedia", "normal", "avanzada"], "default": "facil"},
            "limit": {"type": "integer", "default": 4},
        },
        "required": ["level"],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        start = now_ms()
        log_event("communication_tool_start", {"tool": self.name, "kwargs": kwargs}, tool=self.name)
        catalog = _load_catalog()
        level_id = _normalize_level(kwargs.get("level", "facil"))
        levels = catalog.get("levels", {})
        if level_id not in levels:
            message = "Puedo ofrecer actividades de nivel fácil, intermedio o avanzado. ¿Cuál prefieres?"
            payload = {"ok": False, "tool": self.name, "error": "unknown_level", "available_levels": ["facil", "normal", "avanzada"]}
            return finish(start, self.name, "listar_unknown_level", payload, message)
        level = levels[level_id]
        limit = int(kwargs.get("limit", 4) or 4)
        message = _format_activities(level_id, level, limit)
        payload = {
            "ok": True,
            "tool": self.name,
            "level": level_id,
            "level_label": level.get("label", level_id),
            "activity_families": catalog.get("activity_families", []),
            "activities": level.get("activities", [])[:max(4, limit)],
            "text": message,
            "robot_say": message,
            "robot_next_instruction": "Di text exactamente. No llames a Ollama. Después espera a que el usuario elija una actividad.",
        }
        return finish(start, self.name, "listar", payload, message)
