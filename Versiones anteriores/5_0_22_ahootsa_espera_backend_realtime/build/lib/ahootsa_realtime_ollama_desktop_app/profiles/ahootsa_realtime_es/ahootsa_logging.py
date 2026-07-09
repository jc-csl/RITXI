from __future__ import annotations
import json, os, time, traceback
from datetime import datetime
from pathlib import Path
LOG_ROOT = Path(os.getenv("AHOOTSA_LOG_DIR", r"D:\RITXI\logs"))
def ensure_log_root():
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    return LOG_ROOT
def session_id():
    sid = os.getenv("AHOOTSA_SESSION_ID", "").strip()
    if not sid:
        sid = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.environ["AHOOTSA_SESSION_ID"] = sid
    return sid
def log_event(event, **data):
    ensure_log_root()
    rec = {"ts": datetime.now().isoformat(timespec="milliseconds"), "event": event, "session_id": session_id(), "pid": os.getpid()}
    rec.update(data)
    try:
        with (LOG_ROOT / ("ahootsa_events_" + session_id() + ".jsonl")).open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False, default=repr) + "\n")
    except Exception:
        pass
    return rec
def timed(name, **data):
    class _T:
        def __enter__(self):
            self.t=time.perf_counter(); log_event(name+".start", **data); return self
        def __exit__(self, et, ex, tb):
            elapsed=round((time.perf_counter()-self.t)*1000,2)
            if ex: log_event(name+".error", elapsed_ms=elapsed, error=repr(ex), traceback="".join(traceback.format_exception(et,ex,tb)), **data)
            else: log_event(name+".end", elapsed_ms=elapsed, **data)
            return False
    return _T()
def log_conversation(direction, text, **data):
    log_event("conversation.message", direction=direction, text=text, **data)
