from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path
from typing import Any, Callable


def now_ms() -> float:
    return time.perf_counter() * 1000.0


def duration_ms(start_ms: float) -> int:
    return int(round(now_ms() - float(start_ms)))


def load_debug_logger():
    try:
        import ahootsa_debug_logger  # type: ignore
        return ahootsa_debug_logger
    except Exception:
        try:
            path = Path(__file__).resolve().with_name("ahootsa_debug_logger.py")
            name = "ahootsa_debug_logger_comm_latency_runtime"
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


def log_event(event: str, data: dict[str, Any] | None = None, tool: str = "communication") -> None:
    mod = load_debug_logger()
    if not mod:
        return
    try:
        mod.log_event(event, data or {}, tool=tool)
    except Exception:
        pass


def direct_payload(payload: dict[str, Any], message: str) -> dict[str, Any]:
    for key in (
        "message", "text", "answer", "content", "response", "final_response",
        "spoken_response", "tts_text", "message_for_user", "robot_say",
        "assistant_response", "speak", "say", "direct_response", "tool_summary",
    ):
        payload[key] = message
    payload.setdefault("needs_extra_model_response", False)
    payload.setdefault("direct_response_mode", "ahootsa_7_0_20")
    return payload


def finish(start_ms: float, tool: str, action: str, payload: dict[str, Any], message: str) -> dict[str, Any]:
    elapsed = duration_ms(start_ms)
    payload["duration_ms"] = elapsed
    payload["latency_category"] = "tool_local_fast" if elapsed < 1000 else "tool_local_slow"
    direct_payload(payload, message)
    log_event("communication_tool_result", {"tool": tool, "action": action, "duration_ms": elapsed, "ok": payload.get("ok"), "message_preview": message[:180]}, tool=tool)
    return payload
