from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_SESSION_START = datetime.now()
_SESSION_STAMP = _SESSION_START.strftime("%Y%m%d_%H%M%S")
_SESSION_PID = os.getpid()
_PROJECT_DIR = Path.cwd()
_LOG_DIR = _PROJECT_DIR / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)
_SESSION_LOG_PATH = _LOG_DIR / f"session_{_SESSION_STAMP}_pid{_SESSION_PID}.log"
_EVENT_LOG_PATH = _LOG_DIR / f"session_{_SESSION_STAMP}_pid{_SESSION_PID}.jsonl"

_CONFIGURED = False


def session_log_path() -> str:
    return str(_SESSION_LOG_PATH)


def event_log_path() -> str:
    return str(_EVENT_LOG_PATH)


def session_start_iso() -> str:
    return _SESSION_START.isoformat(timespec="seconds")


def _json_default(value: Any) -> str:
    try:
        return str(value)
    except Exception:  # noqa: BLE001
        return "<unserializable>"


def configure_logging() -> None:
    """Configura consola + archivo por sesión.

    Cada arranque crea:
    - logs/session_YYYYMMDD_HHMMSS_pidXXXX.log   -> log humano completo.
    - logs/session_YYYYMMDD_HHMMSS_pidXXXX.jsonl -> eventos estructurados para diagnóstico.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Evita duplicar handlers si Uvicorn/imports llaman varias veces.
    for handler in list(root.handlers):
        root.removeHandler(handler)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root.addHandler(console)

    file_handler = logging.FileHandler(_SESSION_LOG_PATH, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    _CONFIGURED = True
    logging.getLogger(__name__).info("Log de sesión iniciado: %s", _SESSION_LOG_PATH)
    log_event("session_start", log_file=str(_SESSION_LOG_PATH), event_file=str(_EVENT_LOG_PATH), pid=_SESSION_PID)


def sanitize_settings(settings: Any) -> dict[str, Any]:
    data: dict[str, Any]
    try:
        data = settings.model_dump()
    except Exception:  # noqa: BLE001
        data = dict(getattr(settings, "__dict__", {}))
    # No guardamos claves completas.
    for key in list(data):
        lower = key.lower()
        sensitive = lower.endswith("api_key") or lower in {"api_key", "openai_api_key"} or "secret" in lower or lower.endswith("token")
        if sensitive:
            value = data.get(key)
            data[key] = "<empty>" if not value else "<hidden>"
    return data


def log_event(event: str, **fields: Any) -> None:
    """Escribe un evento estructurado en el .jsonl y una línea resumida en el .log."""
    record = {
        "ts": datetime.now().isoformat(timespec="milliseconds"),
        "event": event,
        **fields,
    }
    try:
        with _EVENT_LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, default=_json_default) + "\n")
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning("No se pudo escribir evento JSONL %s: %s", event, exc)
    logging.getLogger("ritxi.event").info("%s | %s", event, json.dumps(fields, ensure_ascii=False, default=_json_default))
