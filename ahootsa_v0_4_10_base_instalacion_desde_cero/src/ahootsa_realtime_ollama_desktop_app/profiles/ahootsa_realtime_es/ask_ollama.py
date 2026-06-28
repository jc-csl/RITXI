"""Profile-local tool: ask a local Ollama model.

This tool is loaded by the original Reachy Mini conversation app from the
active profile directory. It lets the realtime voice model consult a local
Ollama model while keeping all original audio, movement and emotion tools.
"""

from __future__ import annotations

import os
import json
import asyncio
import urllib.error
import urllib.request
from typing import Any

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies


DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "ahootsa-local:latest"
DEFAULT_SYSTEM_PROMPT = """Eres Ahootsa, un asistente robótico en español.

Hablas siempre en español claro.
Eres amable, paciente, positivo y breve.
Usas frases cortas.
Haces una sola pregunta cada vez.
Estás pensado para apoyar conversaciones con personas con discapacidad intelectual.
No inventes información.
Si no entiendes algo, pide una aclaración sencilla.
"""


def _ollama_base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).rstrip("/")


def _ollama_model() -> str:
    return os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL).strip() or DEFAULT_OLLAMA_MODEL


def _http_json(url: str, payload: dict[str, Any] | None = None, timeout: float = 120.0) -> dict[str, Any]:
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if payload is not None else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _call_ollama(prompt: str, system_prompt: str | None, model: str | None) -> dict[str, Any]:
    base_url = _ollama_base_url()
    model_name = (model or _ollama_model()).strip() or DEFAULT_OLLAMA_MODEL
    system = (system_prompt or DEFAULT_SYSTEM_PROMPT).strip() or DEFAULT_SYSTEM_PROMPT

    payload = {
        "model": model_name,
        "stream": False,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "options": {
            "temperature": 0.4,
            "num_ctx": 2048,
        },
    }
    data = _http_json(f"{base_url}/api/chat", payload=payload, timeout=180.0)
    message = data.get("message", {}) if isinstance(data, dict) else {}
    content = message.get("content", "") if isinstance(message, dict) else ""
    return {
        "ok": True,
        "reply": content.strip(),
        "model": data.get("model", model_name) if isinstance(data, dict) else model_name,
        "base_url": base_url,
        "total_duration": data.get("total_duration") if isinstance(data, dict) else None,
    }


class AskOllamaTool(Tool):
    """Ask the local Ollama model and return its text answer."""

    name = "ask_ollama"
    description = (
        "Consulta una IA local mediante Ollama y devuelve una respuesta de texto en español. "
        "Úsala cuando el usuario pida IA local, privacidad, una explicación o una segunda opinión local."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Pregunta o tarea que se enviará al modelo local Ollama.",
            },
            "system_prompt": {
                "type": "string",
                "description": "Instrucciones opcionales para el modelo local. Normalmente puede omitirse.",
            },
            "model": {
                "type": "string",
                "description": "Modelo Ollama opcional. Por defecto usa OLLAMA_MODEL o ahootsa-local:latest.",
            },
        },
        "required": ["prompt"],
    }

    async def __call__(
        self,
        deps: ToolDependencies,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        **_: Any,
    ) -> dict[str, Any]:
        prompt = (prompt or "").strip()
        if not prompt:
            return {"ok": False, "error": "prompt vacío"}
        try:
            return await asyncio.to_thread(_call_ollama, prompt, system_prompt, model)
        except urllib.error.URLError as exc:
            return {
                "ok": False,
                "error": f"No se pudo conectar con Ollama en {_ollama_base_url()}: {exc}",
                "hint": "Comprueba que Ollama esté activo y que el modelo exista con 'ollama list'.",
            }
        except Exception as exc:
            return {"ok": False, "error": f"Error consultando Ollama: {type(exc).__name__}: {exc}"}
