# AHOOTSA_5_0_7_DIRECT_RESPONSE: evita bloqueo post-tool con backend realtime/HF.
from __future__ import annotations
# AHOOTSA_5_0_10_TOOL_LOG
try:
    from ahootsa_logging import log_event
except Exception:
    def log_event(*a, **k): pass

import json
import re
import sys
import importlib.util
from pathlib import Path
from typing import Any

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies


def _load_debug_logger():
    try:
        import ahootsa_debug_logger  # type: ignore
        return ahootsa_debug_logger
    except Exception:
        try:
            path = Path(__file__).resolve().with_name("ahootsa_debug_logger.py")
            name = "ahootsa_debug_logger_comm_runtime"
            if name in sys.modules:
                return sys.modules[name]
            spec = importlib.util.spec_from_file_location(name, path)
            if not (spec and spec.loader):
                return None
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
            return mod
        except Exception:
            return None


def _log(event: str, data: dict[str, Any] | None = None, tool: str = "actividades_comunicacion") -> None:
    mod = _load_debug_logger()
    if mod:
        mod.log_event(event, data or {}, tool=tool)


def _load_catalog() -> dict[str, Any]:
    path = Path(__file__).resolve().with_name("communication_activities_catalog.json")
    if not path.exists():
        return {"levels": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize(text: object) -> str:
    t = str(text or "").strip().lower()
    repl = {"á":"a","é":"e","í":"i","ó":"o","ú":"u","ü":"u","ñ":"n"}
    for a,b in repl.items():
        t = t.replace(a,b)
    return t


def _normalize_level(value: object) -> str:
    text = _normalize(value)
    if text in {"facil", "faciles", "fácil", "fáciles", "sencillo", "sencillas", "bajo", "iniciacion", "iniciación", "1", "uno"}:
        return "facil"
    if text in {"normal", "normales", "medio", "intermedio", "2", "dos"}:
        return "normal"
    if text in {"avanzada", "avanzado", "avanzadas", "avanzados", "dificil", "difícil", "alto", "experto", "3", "tres"}:
        return "avanzada"
    return text


def _direct(payload: dict[str, Any], message: str) -> dict[str, Any]:
    for key in ("message","text","answer","content","response","final_response","spoken_response","tts_text","message_for_user","robot_say","assistant_response","speak","say","tool_summary"):
        payload[key] = message
    return payload


def _format_levels() -> str:
    return "¿Qué tipo de actividades quieres hacer: fáciles, normales o avanzadas?"


def _format_activities(level_id: str, level: dict[str, Any], limit: int = 6) -> str:
    label = level.get("label", level_id)
    opening = level.get("opening", f"Estas son actividades de nivel {label}.")
    activities = list(level.get("activities", []))[:max(5, int(limit or 6))]
    lines = [opening, "", f"Actividades {str(label).lower()}:"]
    for i, act in enumerate(activities, start=1):
        title = act.get("title", f"Actividad {i}")
        goal = act.get("goal", "")
        lines.append(f"{i}. {title}. {goal}")
    lines.append("")
    lines.append("Elige una actividad diciendo su número o su nombre. Vamos paso a paso.")
    return "\n".join(lines)


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


def _detect_level(user_text: str) -> str | None:
    t = _normalize(user_text)
    for level in ("facil", "normal", "avanzada"):
        if level in t:
            return level
    if any(w in t for w in ["faciles", "sencillas", "bajo", "iniciacion"]):
        return "facil"
    if any(w in t for w in ["normales", "medio", "intermedio"]):
        return "normal"
    if any(w in t for w in ["avanzadas", "avanzado", "experto", "dificil"]):
        return "avanzada"
    return None


def _detect_activity(user_text: str) -> str | None:
    t = _normalize(user_text)
    m = re.search(r"(?:actividad|numero|número)\s*(\d+)", t)
    if m:
        return m.group(1)
    for w in ["uno", "una", "dos", "tres", "cuatro", "cinco", "seis"]:
        if f"actividad {w}" in t or f"la {w}" in t:
            return w
    m2 = re.search(r"\b([1-6])\b", t)
    if m2:
        return m2.group(1)
    return None

class IniciarActividadComunicacion(Tool):
    name = "iniciar_actividad_comunicacion"
    description = "Alias en español. Inicia una actividad concreta de comunicación por nivel y número."
    needs_response = False
    parameters_schema = {
        "type": "object",
        "properties": {
            "nivel": {"type": "string", "default": "facil"},
            "actividad": {"type": "string", "default": "1"}
        },
        "required": ["nivel", "actividad"]
    }
    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        catalog = _load_catalog()
        nivel = _normalize_level(kwargs.get("nivel", "facil"))
        levels = catalog.get("levels", {})
        if nivel not in levels:
            message = _format_levels()
            result = {"ok": False, "error": "unknown_level", "alias": True}
            _direct(result, message)
            _log("tool_result", result, tool=self.name)
            return result
        number, act = _activity_by_id_or_number(levels[nivel], kwargs.get("actividad", "1"))
        if not act:
            message = "No encuentro esa actividad. Dime un número de la lista, por ejemplo uno, dos o tres."
            result = {"ok": False, "error": "unknown_activity", "level": nivel, "alias": True}
            _direct(result, message)
            _log("tool_result", result, tool=self.name)
            return result
        title = act.get("title", f"Actividad {number}")
        message = (
            f"Vamos con la actividad {number}: {title}. "
            f"{act.get('goal','')} "
            f"Te pregunto: {act.get('prompt','')} "
            f"Si lo necesitas, te doy una pista: {act.get('support','')}"
        )
        result = {"ok": True, "level": nivel, "activity_number": number, "activity": act, "alias": True}
        _direct(result, message)
        _log("tool_result", {"level": nivel, "activity_number": number, "title": title}, tool=self.name)
        return result
