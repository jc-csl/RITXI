from __future__ import annotations

import json
import os
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

VERSION = "7.0.16"


def log_root() -> Path:
    root = Path(os.getenv("AHOOTSA_LOG_DIR", r"D:\RITXI\logs"))
    root.mkdir(parents=True, exist_ok=True)
    return root


def session_id() -> str:
    sid = os.getenv("AHOOTSA_SESSION_ID", "").strip()
    if not sid:
        sid = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.environ["AHOOTSA_SESSION_ID"] = sid
    return sid


def event_log_path() -> Path:
    explicit = os.getenv("AHOOTSA_LOG_FILE_EVENTS", "").strip()
    if explicit:
        return Path(explicit)
    return log_root() / f"ahootsa7_{session_id()}_eventos.jsonl"


def runtime_log_path() -> Path:
    explicit = os.getenv("AHOOTSA_LOG_FILE_RUNTIME", "").strip()
    if explicit:
        return Path(explicit)
    return log_root() / f"ahootsa7_{session_id()}_runtime.log"


def screen_log_path() -> Path:
    explicit = os.getenv("AHOOTSA_LOG_FILE_SCREEN", "").strip()
    if explicit:
        return Path(explicit)
    return log_root() / f"ahootsa7_{session_id()}_pantalla.log"


def _safe(value: Any) -> Any:
    try:
        json.dumps(value, ensure_ascii=False)
        return value
    except Exception:
        return repr(value)


def log_event(event: str, **data: Any) -> dict[str, Any]:
    rec = {
        "ts": datetime.now().isoformat(timespec="milliseconds"),
        "version": VERSION,
        "event": event,
        "session_id": session_id(),
        "pid": os.getpid(),
    }
    rec.update({k: _safe(v) for k, v in data.items()})
    try:
        path = event_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False, default=repr) + "\n")
    except Exception:
        pass
    return rec


def log_runtime(line: str, **data: Any) -> None:
    try:
        path = runtime_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        extra = ""
        if data:
            extra = " | " + " | ".join(f"{k}={_safe(v)}" for k, v in data.items())
        with path.open("a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat(timespec='milliseconds')} | {line}{extra}\n")
    except Exception:
        pass


def timed(name: str, **data: Any):
    class _T:
        def __enter__(self):
            self.t = time.perf_counter()
            log_event(name + ".start", **data)
            return self

        def __exit__(self, et, ex, tb):
            elapsed = round((time.perf_counter() - self.t) * 1000, 2)
            if ex:
                log_event(
                    name + ".error",
                    elapsed_ms=elapsed,
                    error=repr(ex),
                    traceback="".join(traceback.format_exception(et, ex, tb)),
                    **data,
                )
            else:
                log_event(name + ".end", elapsed_ms=elapsed, **data)
            return False
    return _T()


def log_conversation(direction: str, text: str, **data: Any) -> None:
    log_event("conversation.message", direction=direction, text=text, **data)
