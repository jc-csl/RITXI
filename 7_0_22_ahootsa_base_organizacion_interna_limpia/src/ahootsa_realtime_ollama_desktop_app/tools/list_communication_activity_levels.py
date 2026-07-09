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


class ListCommunicationActivityLevels(Tool):
    name = "list_communication_activity_levels"
    description = (
        "Responde de forma directa con los 3 niveles de actividades de comunicación: "
        "fácil, intermedia y avanzada. Las actividades principales son saludar, "
        "pedir comida, mantener turnos y conversar. No usa Ollama."
    )
    needs_response = False

    parameters_schema = {"type": "object", "properties": {}, "required": []}

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        start = now_ms()
        log_event("communication_tool_start", {"tool": self.name, "kwargs": kwargs}, tool=self.name)
        catalog = _load_catalog()
        levels = catalog.get("levels", {})
        message = (
            "Tenemos tres niveles: fácil, intermedio y avanzado. "
            "En cada nivel puedes practicar saludar, pedir comida, mantener turnos y conversar. "
            "¿Qué nivel quieres: fácil, intermedio o avanzado?"
        )
        payload = {
            "ok": True,
            "tool": self.name,
            "activity_families": catalog.get("activity_families", []),
            "levels": [
                {"id": "facil", "label": levels.get("facil", {}).get("label", "Fácil"), "description": levels.get("facil", {}).get("description", "")},
                {"id": "normal", "label": levels.get("normal", {}).get("label", "Intermedia"), "description": levels.get("normal", {}).get("description", "")},
                {"id": "avanzada", "label": levels.get("avanzada", {}).get("label", "Avanzada"), "description": levels.get("avanzada", {}).get("description", "")},
            ],
            "text": message,
            "robot_say": message,
            "robot_next_instruction": "Di text exactamente. No llames a Ollama. Después espera el nivel elegido.",
        }
        return finish(start, self.name, "niveles", payload, message)
