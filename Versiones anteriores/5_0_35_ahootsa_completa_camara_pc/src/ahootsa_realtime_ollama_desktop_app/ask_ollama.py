# AHOOTSA_5_0_9_OLLAMA_OPTIONAL_ACTIVITY: ask_ollama es actividad opcional, no cerebro principal.
"""Profile-local tool: ask a local Ollama model.

v0.4.12:
- mantiene la app oficial intacta;
- añade log específico de ask_ollama;
- reduce bloqueos largos;
- devuelve errores claros si Ollama no responde.
"""

from __future__ import annotations
# AHOOTSA_5_0_10_TOOL_LOG
try:
    from ahootsa_logging import log_event
except Exception:
    def log_event(*a, **k): pass

import os
import json
import asyncio
import urllib.error
import urllib.request
import socket
import datetime
from pathlib import Path
from typing import Any

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies


DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "ahootsa-local:latest"
DEFAULT_TIMEOUT_SECONDS = float(os.getenv("AHOOTSA_OLLAMA_TIMEOUT_SECONDS", "45"))

DEFAULT_SYSTEM_PROMPT = """Eres Ahootsa, un asistente en castellano.
Responde en castellano claro, breve y util.
No digas que eres ChatGPT.
No digas que eres Reachy Mini.
Tu nombre es Ahootsa.
Esta herramienta solo se usa como prueba de IA local Ollama, no como motor principal de conversacion.
"""


def _log_file() -> Path:
    try:
        from ahootsa_logging import runtime_log_path
        return runtime_log_path()
    except Exception:
        root = Path(os.getenv("AHOOTSA_LOG_DIR", r"D:\RITXI\logs"))
        root.mkdir(parents=True, exist_ok=True)
        sid = os.getenv("AHOOTSA_SESSION_ID", datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        return root / f"ahootsa5_{sid}_runtime.log"


def _log_event(event: str, data: dict[str, Any] | None = None) -> None:
    payload = {
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "event": event,
        "data": data or {},
    }
    try:
        with _log_file().open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _ollama_base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).rstrip("/")


def _ollama_model() -> str:
    return os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL).strip() or DEFAULT_OLLAMA_MODEL


def _http_json(url: str, payload: dict[str, Any] | None = None, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> dict[str, Any]:
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

    _log_event("call_start", {
        "base_url": base_url,
        "model": model_name,
        "prompt_preview": prompt[:300],
        "timeout_seconds": DEFAULT_TIMEOUT_SECONDS,
    })

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
            "num_predict": 120,
        },
    }

    data = _http_json(f"{base_url}/api/chat", payload=payload, timeout=DEFAULT_TIMEOUT_SECONDS)
    message = data.get("message", {}) if isinstance(data, dict) else {}
    content = message.get("content", "") if isinstance(message, dict) else ""
    reply = content.strip()

    result = {
        "ok": True,
        "reply": reply,
        "message_for_user": reply,
        "model": data.get("model", model_name) if isinstance(data, dict) else model_name,
        "base_url": base_url,
        "log_file": str(_log_file()),
        "total_duration": data.get("total_duration") if isinstance(data, dict) else None,
    }
    _log_event("call_success", {
        "model": result["model"],
        "reply_preview": reply[:300],
        "total_duration": result["total_duration"],
    })
    return result



def _ahootsa_persona_prefix() -> str:
    try:
        from pathlib import Path
        p = Path(__file__).resolve().with_name("communication_profile.md")
        if p.exists():
            return p.read_text(encoding="utf-8")[:4500]
    except Exception:
        pass
    return (
        "Actúa como una monitora experta en comunicación y educación especial. "
        "Usa tono dulce, paciente y motivador. "
        "Nunca uses lenguaje complejo, tecnicismos ni dobles sentidos. "
        "Guía con preguntas sencillas y ejemplos cotidianos."
    )


class AskOllamaTool(Tool):
    """Ask the local Ollama model and return its text answer."""

    name = "ask_ollama"
    description = (
        "Actividad opcional para probar la IA local Ollama. "
        "No es el cerebro principal de la conversacion normal. "
        "Usala solo cuando el usuario pida expresamente probar Ollama, IA local o hacer una consulta a la IA local."
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
            _log_event("call_error", {"error": "prompt vacío"})
            return {
                "ok": False,
                "error": "prompt vacío",
                "message_for_user": "No he recibido la pregunta para la IA local.",
                "log_file": str(_log_file()),
            }

        try:
            return await asyncio.wait_for(
                asyncio.to_thread(_call_ollama, prompt, system_prompt, model),
                timeout=DEFAULT_TIMEOUT_SECONDS + 5,
            )

        except asyncio.TimeoutError:
            msg = (
                f"Ollama local no respondió antes de {DEFAULT_TIMEOUT_SECONDS} segundos. "
                "Comprueba que Ollama esté abierto y que el modelo ahootsa-local:latest exista."
            )
            _log_event("call_timeout", {"error": msg})
            return {"ok": False, "error": msg, "message_for_user": msg, "log_file": str(_log_file())}

        except urllib.error.URLError as exc:
            msg = (
                f"No he podido conectar con Ollama local en {_ollama_base_url()}. "
                "Comprueba Ollama con 'ollama list' y prueba http://127.0.0.1:11434/api/tags."
            )
            _log_event("call_url_error", {"error": repr(exc), "message": msg})
            return {
                "ok": False,
                "error": f"{type(exc).__name__}: {exc}",
                "message_for_user": msg,
                "hint": "Comprueba que Ollama esté activo y que el modelo exista con 'ollama list'.",
                "log_file": str(_log_file()),
            }

        except (ConnectionRefusedError, socket.timeout) as exc:
            msg = "Ollama local no acepta conexiones ahora mismo. Abre Ollama o reinicia el servicio."
            _log_event("call_connection_error", {"error": repr(exc), "message": msg})
            return {"ok": False, "error": repr(exc), "message_for_user": msg, "log_file": str(_log_file())}

        except Exception as exc:
            msg = f"Error consultando Ollama: {type(exc).__name__}: {exc}"
            _log_event("call_exception", {"error": msg})
            return {"ok": False, "error": msg, "message_for_user": msg, "log_file": str(_log_file())}
