# AHOOTSA_7_0_20_COMMUNICATION_DIRECT_LATENCY
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies

try:
    from .communication_latency_utils import now_ms, log_event, finish
except Exception:
    from communication_latency_utils import now_ms, log_event, finish  # type: ignore


def _load_catalog() -> dict[str, Any]:
    path = Path(__file__).resolve().with_name("communication_activities_catalog.json")
    if not path.exists():
        return {"levels": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize(text: object) -> str:
    t = str(text or "").strip().lower()
    for a, b in {"á":"a", "é":"e", "í":"i", "ó":"o", "ú":"u", "ü":"u", "ñ":"n"}.items():
        t = t.replace(a, b)
    return t


def _normalize_level(value: object) -> str:
    text = _normalize(value)
    if text in {"facil", "faciles", "fácil", "fáciles", "sencillo", "bajo", "iniciacion", "1", "uno"}:
        return "facil"
    if text in {"normal", "normales", "medio", "intermedio", "intermedia", "nivel 2", "2", "dos"}:
        return "normal"
    if text in {"avanzada", "avanzado", "avanzadas", "dificil", "difícil", "alto", "experto", "3", "tres"}:
        return "avanzada"
    return text


def _activity_by_id_or_number(level: dict[str, Any], activity: object) -> tuple[int, dict[str, Any] | None]:
    activities = list(level.get("activities", []))
    raw = _normalize(activity)
    m = re.search(r"\d+", raw)
    if m:
        idx = int(m.group(0))
        if 1 <= idx <= len(activities):
            return idx, activities[idx - 1]
    number_words = {"uno":1, "una":1, "dos":2, "tres":3, "cuatro":4, "cinco":5, "seis":6}
    for word, idx in number_words.items():
        if word in raw and 1 <= idx <= len(activities):
            return idx, activities[idx - 1]
    norm = raw.replace(" ", "_").replace("-", "_")
    for i, act in enumerate(activities, start=1):
        if norm == _normalize(act.get("id", "")):
            return i, act
        if raw and raw in _normalize(act.get("title", "")):
            return i, act
    return 0, None


class StartCommunicationActivity(Tool):
    name = "start_communication_activity"
    description = (
        "Inicia rápidamente una actividad de comunicación de un nivel dado. "
        "No usa Ollama; devuelve directamente la explicación y la primera pregunta."
    )
    # 7.0.20: respuesta directa para evitar el minuto de espera post-tool.
    needs_response = False

    parameters_schema = {
        "type": "object",
        "properties": {
            "level": {"type": "string", "enum": ["facil", "intermedia", "normal", "avanzada"], "default": "facil"},
            "activity": {"type": "string", "description": "Número, id o nombre de la actividad.", "default": "1"},
        },
        "required": ["level", "activity"],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        start = now_ms()
        log_event("communication_tool_start", {"tool": self.name, "kwargs": kwargs}, tool=self.name)
        catalog = _load_catalog()
        level_id = _normalize_level(kwargs.get("level", "facil"))
        level = (catalog.get("levels") or {}).get(level_id)
        if not level:
            message = "Puedo hacer actividades fáciles, intermedias o avanzadas. ¿Cuál prefieres?"
            payload = {"ok": False, "tool": self.name, "error": "unknown_level"}
            return finish(start, self.name, "iniciar_unknown_level", payload, message)

        number, act = _activity_by_id_or_number(level, kwargs.get("activity", "1"))
        if not act:
            message = "No encuentro esa actividad. Dime un número de la lista, por ejemplo uno, dos o tres."
            payload = {"ok": False, "tool": self.name, "error": "unknown_activity", "level": level_id}
            return finish(start, self.name, "iniciar_unknown_activity", payload, message)

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
        payload = {
            "ok": True,
            "tool": self.name,
            "level": level_id,
            "activity_number": number,
            "activity": act,
            "robot_next_instruction": "Di text con pausas. No llames a Ollama. Después espera la respuesta del usuario.",
        }
        return finish(start, self.name, "iniciar", payload, message)
