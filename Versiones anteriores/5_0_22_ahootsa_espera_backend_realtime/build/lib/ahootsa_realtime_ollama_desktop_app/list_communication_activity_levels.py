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


class ListCommunicationActivityLevels(Tool):
    name = "list_communication_activity_levels"
    description = "Ofrece los tres niveles de actividades de comunicación: fácil, normal o avanzada."
    needs_response = False

    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        catalog = _load_catalog()
        levels = catalog.get("levels", {})
        message = (
            "¿Qué tipo de actividades quieres hacer: fáciles, normales o avanzadas? "
            "Podemos ir poco a poco."
        )
        return {
            "ok": True,
            "levels": [
                {"id": "facil", "label": levels.get("facil", {}).get("label", "Fácil")},
                {"id": "normal", "label": levels.get("normal", {}).get("label", "Normal")},
                {"id": "avanzada", "label": levels.get("avanzada", {}).get("label", "Avanzada")},
            ],
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
