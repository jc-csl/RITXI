from __future__ import annotations

import datetime as _dt
import json
import os
import platform
import traceback
from pathlib import Path
from typing import Any

VERSION = "0.4.57.2"


def log_dir() -> Path:
    explicit = os.getenv("AHOOTSA_LOG_DIR", "").strip()
    if explicit:
        d = Path(explicit)
    else:
        base = os.getenv("LOCALAPPDATA") or os.getenv("TEMP") or "."
        d = Path(base) / "Reachy Mini Control" / "ahootsa_logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _safe(value: Any) -> Any:
    try:
        json.dumps(value, ensure_ascii=False)
        return value
    except Exception:
        try:
            return repr(value)
        except Exception:
            return "<unserializable>"


def log_event(event: str, data: dict[str, Any] | None = None, *, tool: str | None = None) -> None:
    payload = {
        "ts": _dt.datetime.now().isoformat(timespec="milliseconds"),
        "version": VERSION,
        "event": event,
        "tool": tool,
        "pid": os.getpid(),
        "python": platform.python_version(),
        "data": _safe(data or {}),
    }
    try:
        path = log_dir() / f"ahootsa_events_{_dt.datetime.now().strftime('%Y%m%d')}.jsonl"
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
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
        compact = {k: v for k, v in result.items() if k not in {"state", "cards"}}
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
