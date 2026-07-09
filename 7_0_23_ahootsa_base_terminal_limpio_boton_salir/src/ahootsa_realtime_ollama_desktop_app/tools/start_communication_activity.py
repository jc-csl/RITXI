# AHOOTSA_7_0_23_COMMUNICATION_THREE_LEVELS
from __future__ import annotations

import json
import re
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


def _normalize(text: object) -> str:
    t = str(text or "").strip().lower()
    for a, b in {"á":"a", "é":"e", "í":"i", "ó":"o", "ú":"u", "ü":"u", "ñ":"n"}.items():
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t)


def _normalize_level(value: object) -> str:
    text = _normalize(value)
    if text in {"facil", "faciles", "fácil", "fáciles", "sencillo", "bajo", "iniciacion", "1", "uno"}:
        return "facil"
    if text in {"normal", "normales", "medio", "intermedio", "intermedia", "intermedias", "nivel 2", "2", "dos"}:
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
    number_words = {"uno":1, "una":1, "primera":1, "primer":1, "dos":2, "segunda":2, "tres":3, "tercera":3, "cuatro":4, "cuarta":4}
    for word, idx in number_words.items():
        if re.search(rf"\b{word}\b", raw) and 1 <= idx <= len(activities):
            return idx, activities[idx - 1]

    family_aliases = {
        "saludar": {"saludar", "saludo", "hola", "buenos dias", "buenas", "como estas", "que tal"},
        "pedir_comida": {"pedir comida", "comida", "restaurante", "cafeteria", "bar", "menu", "pedir agua", "pedir bebida", "bocadillo"},
        "mantener_turnos": {"mantener turnos", "turnos", "turno", "mi turno", "tu turno", "esperar", "no interrumpir", "escuchar"},
        "conversar": {"conversar", "conversacion", "charlar", "hablar", "preguntar", "tema", "dialogar"},
    }
    for i, act in enumerate(activities, start=1):
        haystack = " ".join([
            _normalize(act.get("id", "")),
            _normalize(act.get("title", "")),
            _normalize(act.get("family", "")),
            " ".join(_normalize(x) for x in act.get("aliases", [])),
        ])
        if raw and raw in haystack:
            return i, act
        fam = str(act.get("family", ""))
        if fam in family_aliases and any(alias in raw for alias in family_aliases[fam]):
            return i, act
    return 0, None


class StartCommunicationActivity(Tool):
    name = "start_communication_activity"
    description = (
        "Inicia una actividad de comunicación de un nivel dado. Las actividades principales son "
        "saludar, pedir comida, mantener turnos y conversar, en nivel fácil, intermedio o avanzado. "
        "No usa Ollama; devuelve directamente la explicación y la primera pregunta."
    )
    needs_response = False

    parameters_schema = {
        "type": "object",
        "properties": {
            "level": {"type": "string", "enum": ["facil", "intermedia", "normal", "avanzada"], "default": "facil"},
            "activity": {"type": "string", "description": "Número, id, familia o nombre: saludar, pedir comida, mantener turnos, conversar.", "default": "1"},
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
            message = "No encuentro esa actividad. Puedes decir: saludar, pedir comida, mantener turnos o conversar."
            payload = {"ok": False, "tool": self.name, "error": "unknown_activity", "level": level_id}
            return finish(start, self.name, "iniciar_unknown_activity", payload, message)

        title = act.get("title", f"Actividad {number}")
        prompt = act.get("prompt", "")
        support = act.get("support", "")
        examples = act.get("examples") or []
        example_text = f" Por ejemplo: {examples[0]}" if examples else ""
        message = (
            f"Vamos con {title}, nivel {level.get('label', level_id)}. "
            f"{prompt} "
            f"Pista: {support}{example_text}"
        )
        payload = {
            "ok": True,
            "tool": self.name,
            "level": level_id,
            "level_label": level.get("label", level_id),
            "activity_number": number,
            "activity_family": act.get("family"),
            "activity": act,
            "text": message,
            "robot_say": message,
            "robot_next_instruction": "Di text con pausas. No llames a Ollama. Después espera la respuesta del usuario.",
        }
        return finish(start, self.name, "iniciar", payload, message)
