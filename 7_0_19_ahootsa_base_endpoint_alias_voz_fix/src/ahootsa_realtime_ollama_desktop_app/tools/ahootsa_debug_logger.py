from __future__ import annotations

import json
import os
import platform
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

VERSION = "7.0.19"

try:
    from ahootsa_logging import event_log_path, log_event as _central_event
except Exception:
    event_log_path = None
    _central_event = None


def _fallback_path() -> Path:
    root = Path(os.getenv("AHOOTSA_LOG_DIR", r"D:\RITXI\logs"))
    root.mkdir(parents=True, exist_ok=True)
    sid = os.getenv("AHOOTSA_SESSION_ID", datetime.now().strftime("%Y%m%d_%H%M%S"))
    return root / f"ahootsa7_{sid}_eventos.jsonl"


def _safe(value: Any) -> Any:
    try:
        json.dumps(value, ensure_ascii=False)
        return value
    except Exception:
        return repr(value)


def log_event(event: str, data: dict[str, Any] | None = None, *, tool: str | None = None) -> None:
    payload = {
        "tool": tool,
        "python": platform.python_version(),
        "data": _safe(data or {}),
    }
    if _central_event:
        try:
            _central_event(event, **payload)
            return
        except Exception:
            pass

    rec = {
        "ts": datetime.now().isoformat(timespec="milliseconds"),
        "version": VERSION,
        "event": event,
        "session_id": os.getenv("AHOOTSA_SESSION_ID", ""),
        "pid": os.getpid(),
        **payload,
    }
    try:
        path = event_log_path() if event_log_path else _fallback_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False, default=repr) + "\n")
    except Exception:
        pass


def log_exception(event: str, exc: BaseException, data: dict[str, Any] | None = None, *, tool: str | None = None) -> None:
    payload = dict(data or {})
    payload.update({
        "exception_type": type(exc).__name__,
        "exception": str(exc),
        "traceback": traceback.format_exc(),
    })
    log_event(event, payload, tool=tool)


def log_tool_start(tool: str, kwargs: dict[str, Any] | None = None) -> None:
    log_event("tool_start", {"kwargs": _safe(kwargs or {})}, tool=tool)


def log_tool_result(tool: str, result: Any) -> None:
    compact = result
    if isinstance(result, dict):
        compact = {k: v for k, v in result.items() if k not in {"state", "cards", "image_base64"}}
        if "state" in result and isinstance(result["state"], dict):
            st = result["state"]
            compact["state_summary"] = {
                "game_id": st.get("game_id"),
                "last_result": st.get("last_result"),
                "last_move_id": st.get("last_move_id"),
                "matches": st.get("matches"),
                "finished": st.get("finished"),
            }
    log_event("tool_result", {"result": _safe(compact)}, tool=tool)
