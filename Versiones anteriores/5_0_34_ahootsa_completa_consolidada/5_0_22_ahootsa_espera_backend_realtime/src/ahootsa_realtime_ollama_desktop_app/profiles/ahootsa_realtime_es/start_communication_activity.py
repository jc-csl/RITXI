# AHOOTSA_5_0_7_DIRECT_RESPONSE: evita bloqueo post-tool con backend realtime/HF.
# AHOOTSA_COMM_TOOL_LOGGING_v0_4_57_8
from __future__ import annotations
# AHOOTSA_5_0_10_TOOL_LOG
try:
    from ahootsa_logging import log_event
except Exception:
    def log_event(*a, **k): pass

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


def _activity_by_id_or_number(level: dict[str, Any], activity: object) -> tuple[int, dict[str, Any] | None]:
    activities = list(level.get("activities", []))
    raw = str(activity or "").strip().lower()
    try:
        idx = int(raw)
        if 1 <= idx <= len(activities):
            return idx, activities[idx - 1]
    except Exception:
        pass

    norm = raw.replace(" ", "_").replace("-", "_")
    for i, act in enumerate(activities, start=1):
        if norm == str(act.get("id", "")).lower():
            return i, act
        if raw in str(act.get("title", "")).lower():
            return i, act
    return 0, None


class StartCommunicationActivity(Tool):
    name = "start_communication_activity"
    description = "Inicia una actividad de comunicación de un nivel dado, guiando con una pregunta sencilla."
    needs_response = False

    parameters_schema = {
        "type": "object",
        "properties": {
            "level": {"type": "string", "enum": ["facil", "normal", "avanzada"], "default": "facil"},
            "activity": {"type": "string", "description": "Número, id o nombre de la actividad.", "default": "1"},
        },
        "required": ["level", "activity"],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        catalog = _load_catalog()
        level_id = _normalize_level(kwargs.get("level", "facil"))
        level = (catalog.get("levels") or {}).get(level_id)

        if not level:
            message = "Puedo hacer actividades fáciles, normales o avanzadas. ¿Cuál prefieres?"
            return {
                "ok": False,
                "error": "unknown_level",
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
            }

        number, act = _activity_by_id_or_number(level, kwargs.get("activity", "1"))
        if not act:
            message = "No encuentro esa actividad. Dime un número de la lista, por ejemplo uno, dos o tres."
            return {
                "ok": False,
                "error": "unknown_activity",
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
            }

        title = act.get("title", f"Actividad {number}")
        goal = act.get("goal", "")
        prompt = act.get("prompt", "")
        support = act.get("support", "")

        message = (
            f"Vamos con la actividad {number}: {title}. "
            f"{goal} "
            f"Te pregunto: {prompt} "
            f"Si lo necesitas, te doy una pista: {support}"
        )
        return {
            "ok": True,
            "level": level_id,
            "activity_number": number,
            "activity": act,
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
            "robot_next_instruction": "Di text con pausas. Después espera la respuesta del usuario y guia con una pregunta sencilla."
        }
