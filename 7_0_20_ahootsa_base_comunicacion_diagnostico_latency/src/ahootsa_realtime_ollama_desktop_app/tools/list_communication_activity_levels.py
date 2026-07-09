# AHOOTSA_7_0_20_COMMUNICATION_DIRECT_LATENCY
from __future__ import annotations

import json
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


class ListCommunicationActivityLevels(Tool):
    name = "list_communication_activity_levels"
    description = (
        "Responde de forma directa y rápida con los niveles de actividades de comunicación: "
        "fácil, intermedia o avanzada. No usa Ollama."
    )
    # 7.0.20: respuesta directa para evitar el minuto de espera post-tool en HF.
    needs_response = False

    parameters_schema = {"type": "object", "properties": {}, "required": []}

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        start = now_ms()
        log_event("communication_tool_start", {"tool": self.name, "kwargs": kwargs}, tool=self.name)
        catalog = _load_catalog()
        levels = catalog.get("levels", {})
        message = (
            "Podemos hacer actividades fáciles, intermedias o avanzadas. "
            "Dime el nivel que prefieres y te muestro varias opciones."
        )
        payload = {
            "ok": True,
            "tool": self.name,
            "levels": [
                {"id": "facil", "label": levels.get("facil", {}).get("label", "Fácil")},
                {"id": "normal", "label": levels.get("normal", {}).get("label", "Intermedia")},
                {"id": "avanzada", "label": levels.get("avanzada", {}).get("label", "Avanzada")},
            ],
            "robot_next_instruction": "Di text exactamente. No llames a Ollama. Después espera el nivel elegido.",
        }
        return finish(start, self.name, "niveles", payload, message)
