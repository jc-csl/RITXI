#!/usr/bin/env python3
"""Generate centralized Ahootsa conversation and diagnostic logs."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TIMESTAMP_PATTERN = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}"


def decode_log(raw: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def join_wrapped_content(content: str) -> str:
    parts = content.splitlines()

    if not parts:
        return ""

    rebuilt = parts[0]

    for part in parts[1:]:
        if not part:
            continue

        if not rebuilt:
            rebuilt = part
            continue

        previous = rebuilt[-1]
        first = part[0]

        if previous.isspace() or first.isspace():
            rebuilt += part
        elif previous.isalnum() and first.islower():
            rebuilt += part
        elif previous in "-/":
            rebuilt += part
        else:
            rebuilt += " " + part

    return " ".join(rebuilt.split())


def is_internal_assistant_message(content: str) -> bool:
    lowered = content.lower()

    if "the tool is now running" in lowered:
        return True

    if "used tool " in lowered and " args " in lowered:
        return True

    if content.startswith("{") and (
        '"status"' in content
        or '"dance_id"' in content
        or '"activity"' in content
        or '"tool"' in content
    ):
        return True

    return False


def parse_interactions(log_text: str) -> tuple[list[dict[str, Any]], int]:
    pattern = re.compile(
        rf"(?ms)^(?P<timestamp>{TIMESTAMP_PATTERN}) "
        r"[^\r\n]*?\| role="
        r"(?P<role>user_partial|user|assistant) "
        r"content=(?P<content>.*?)"
        rf"(?=^{TIMESTAMP_PATTERN} |^\*{{10,}}|\Z)"
    )

    interactions: list[dict[str, Any]] = []
    partial_count = 0

    for source_index, match in enumerate(pattern.finditer(log_text)):
        role = match.group("role")
        content = join_wrapped_content(
            match.group("content")
        ).strip()

        if not content:
            continue

        if role == "user_partial":
            partial_count += 1
            continue

        if role == "assistant" and is_internal_assistant_message(content):
            continue

        interactions.append(
            {
                "source_index": source_index,
                "timestamp": match.group("timestamp"),
                "role": role,
                "content": content,
            }
        )

    return interactions, partial_count


def extract_log_lines(
    log_text: str,
    level: str,
    limit: int = 100,
) -> list[str]:
    marker = f" {level} "
    lines: list[str] = []

    for line in log_text.splitlines():
        if marker in line:
            lines.append(line.strip())

    return lines[-limit:]


def extract_first_group(
    pattern: str,
    text: str,
) -> str | None:
    match = re.search(pattern, text)

    if match is None:
        return None

    return match.group(1).strip()


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d %H:%M:%S,%f",
        )
    except ValueError:
        return None


def transcript_end_time(log_text: str) -> datetime | None:
    match = re.search(
        r"Hora de finalización:\s*(\d{14})",
        log_text,
    )

    if match is None:
        return None

    try:
        return datetime.strptime(
            match.group(1),
            "%Y%m%d%H%M%S",
        )
    except ValueError:
        return None


def startup_time(log_text: str) -> datetime | None:
    match = re.search(
        r"Hora de inicio:\s*(\d{14})",
        log_text,
    )

    if match is None:
        return None

    try:
        return datetime.strptime(
            match.group(1),
            "%Y%m%d%H%M%S",
        )
    except ValueError:
        return None


def build_audio_diagnostics(log_text: str) -> dict[str, Any]:
    compact_log = re.sub(r"\s+", "", log_text).lower()

    latency_matches = re.findall(
        r"Audio pipeline latency "
        r"\(live=True, min_latency=(\d+), max_latency=(\d+)\)",
        log_text,
    )

    last_latency = None

    if latency_matches:
        minimum, maximum = latency_matches[-1]
        last_latency = {
            "minimum_nanoseconds": int(minimum),
            "maximum_nanoseconds": int(maximum),
        }

    return {
        "reachy_audio_usb_missing": (
            "noreachyminiaudiousbdevicefound" in compact_log
        ),
        "default_audio_source_used": (
            "usingdefaultaudiosource" in compact_log
        ),
        "default_audio_sink_used": (
            "usingdefaultaudiosink" in compact_log
        ),
        "echo_cancellation_enabled": (
            "enablingwebrtcechocancellation" in compact_log
        ),
        "startup_config_not_applied": (
            "reachyaudiostartupconfigwasnotapplied" in compact_log
        ),
        "last_pipeline_latency": last_latency,
    }


def build_dance_diagnostics(
    log_text: str,
) -> dict[str, Any]:
    promise_pattern = re.compile(
        rf"(?ms)^(?P<timestamp>{TIMESTAMP_PATTERN}) "
        r"[^\r\n]*?\| role=assistant content="
        r"(?P<content>.*?)"
        rf"(?=^{TIMESTAMP_PATTERN} |^\*{{10,}}|\Z)"
    )
    log_entry_pattern = re.compile(
        rf"(?ms)^(?P<timestamp>{TIMESTAMP_PATTERN}) "
        r"(?P<body>.*?)"
        rf"(?=^{TIMESTAMP_PATTERN} |^\*{{10,}}|\Z)"
    )

    promises: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []

    for match in promise_pattern.finditer(log_text):
        content = join_wrapped_content(
            match.group("content")
        ).strip()
        normalized = content.lower()

        if "vamos a bailar" not in normalized:
            continue

        timestamp = match.group("timestamp")
        parsed = parse_timestamp(timestamp)

        if parsed is None:
            continue

        promises.append(
            {
                "timestamp": timestamp,
                "datetime": parsed,
                "content": content,
            }
        )

    for match in log_entry_pattern.finditer(log_text):
        body = " ".join(
            match.group("body").split()
        )
        compact_body = re.sub(
            r"\s+",
            "",
            body,
        )

        if (
            "Toolcallreceived" not in compact_body
            or "tool_name='play_ahootsa_dance'"
            not in compact_body
        ):
            continue

        dance_match = re.search(
            r'args=\{"dance_id":"([^"]+)"\}',
            compact_body,
        )

        if dance_match is None:
            continue

        timestamp = match.group("timestamp")
        parsed = parse_timestamp(timestamp)

        if parsed is None:
            continue

        calls.append(
            {
                "timestamp": timestamp,
                "datetime": parsed,
                "dance_id": dance_match.group(1),
            }
        )

    delayed_calls: list[dict[str, Any]] = []
    used_call_indexes: set[int] = set()

    for promise in promises:
        matched_index: int | None = None

        # The correct flow may emit the tool call a few milliseconds before
        # the spoken "Vamos a bailar". Treat that as the same immediate turn.
        previous_candidates = [
            index
            for index, call in enumerate(calls)
            if index not in used_call_indexes
            and -3.0
            <= (
                call["datetime"] - promise["datetime"]
            ).total_seconds()
            <= 0.0
        ]

        if previous_candidates:
            matched_index = previous_candidates[-1]
        else:
            matched_index = next(
                (
                    index
                    for index, call in enumerate(calls)
                    if index not in used_call_indexes
                    and call["datetime"] >= promise["datetime"]
                ),
                None,
            )

        if matched_index is None:
            delayed_calls.append(
                {
                    "promise_at": promise["timestamp"],
                    "tool_call_at": None,
                    "dance_id": None,
                    "delay_seconds": None,
                    "missing_tool_call": True,
                }
            )
            continue

        used_call_indexes.add(matched_index)
        matched_call = calls[matched_index]
        delay_seconds = max(
            0.0,
            (
                matched_call["datetime"] - promise["datetime"]
            ).total_seconds(),
        )

        if delay_seconds > 5.0:
            delayed_calls.append(
                {
                    "promise_at": promise["timestamp"],
                    "tool_call_at": matched_call["timestamp"],
                    "dance_id": matched_call["dance_id"],
                    "delay_seconds": round(delay_seconds, 3),
                    "missing_tool_call": False,
                }
            )

    duplicate_calls: list[dict[str, Any]] = []

    for previous, current in zip(calls, calls[1:]):
        if previous["dance_id"] != current["dance_id"]:
            continue

        interval = (
            current["datetime"] - previous["datetime"]
        ).total_seconds()

        if 0.0 <= interval <= 10.0:
            duplicate_calls.append(
                {
                    "dance_id": current["dance_id"],
                    "first_call_at": previous["timestamp"],
                    "duplicate_call_at": current["timestamp"],
                    "interval_seconds": round(interval, 3),
                }
            )

    return {
        "spoken_start_promises": len(promises),
        "tool_calls": len(calls),
        "delayed_or_missing_calls": delayed_calls,
        "duplicate_calls": duplicate_calls,
        "possible_orchestration_issue": bool(
            delayed_calls or duplicate_calls
        ),
    }


def build_terminal_diagnostic(
    interactions: list[dict[str, Any]],
    log_text: str,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "last_role": None,
        "last_turn_at": None,
        "transcript_finished_at": None,
        "terminal_silence_seconds": None,
        "possible_listening_stall": False,
        "observation": None,
    }

    if not interactions:
        return result

    last_turn = interactions[-1]
    result["last_role"] = last_turn["role"]
    result["last_turn_at"] = last_turn["timestamp"]

    end_time = transcript_end_time(log_text)

    if end_time is None:
        return result

    result["transcript_finished_at"] = end_time.isoformat()

    last_time = parse_timestamp(last_turn["timestamp"])

    if last_time is None:
        return result

    silence_seconds = max(
        0.0,
        (end_time - last_time).total_seconds(),
    )
    result["terminal_silence_seconds"] = round(
        silence_seconds,
        2,
    )

    if (
        last_turn["role"] == "assistant"
        and silence_seconds >= 90
    ):
        result["possible_listening_stall"] = True
        result["observation"] = (
            "Posible incidencia de escucha: no se registró una "
            "intervención final de la persona durante "
            f"{silence_seconds / 60.0:.1f} minutos antes del cierre."
        )

    return result


def format_interactions(
    interactions: list[dict[str, Any]],
    *,
    mode: str,
    session_id: int | None,
    run_id: str | None,
) -> str:
    title = "AHOOTSA - INTERACCIONES DE CONVERSACIÓN"
    lines = [
        title,
        "=" * len(title),
        f"Modo: {mode}",
    ]

    if session_id is not None:
        lines.append(f"Sesión: {session_id}")

    if run_id:
        lines.append(f"Ejecución: {run_id}")

    lines.append("")

    for item in interactions:
        speaker = (
            "Persona usuaria"
            if item["role"] == "user"
            else "Aocha"
        )
        lines.append(
            f'[{item["timestamp"]}] {speaker}: {item["content"]}'
        )

    lines.append("")

    return "\n".join(lines)


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def copy_log_if_needed(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        if source.resolve() == destination.resolve():
            return
    except OSError:
        pass

    if destination.exists():
        try:
            if (
                source.stat().st_size == destination.stat().st_size
                and source.read_bytes() == destination.read_bytes()
            ):
                return
        except OSError:
            pass

    shutil.copy2(source, destination)


def generate(
    *,
    log_path: Path,
    output_dir: Path,
    mode: str,
    state: str,
    session_id: int | None,
    run_id: str | None,
    profile: str | None,
    voice: str | None,
    source_session_dir: Path | None,
) -> dict[str, Any]:
    if not log_path.is_file():
        raise FileNotFoundError(
            f"No existe el log: {log_path}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    central_log = output_dir / "conversation_app.log"
    copy_log_if_needed(log_path, central_log)

    raw = central_log.read_bytes()
    log_text = decode_log(raw)
    interactions, partial_count = parse_interactions(log_text)

    warnings = extract_log_lines(log_text, "WARNING")
    errors = extract_log_lines(log_text, "ERROR")
    tool_calls = len(
        re.findall(
            r"Tool call received",
            log_text,
        )
    )
    user_interventions = len(
        re.findall(
            r"User intervention:",
            log_text,
        )
    )

    start_time = startup_time(log_text)
    end_time = transcript_end_time(log_text)

    duration_seconds = None

    if start_time is not None and end_time is not None:
        duration_seconds = round(
            max(0.0, (end_time - start_time).total_seconds()),
            2,
        )

    profile_from_log = extract_first_group(
        r"Realtime session initialized with "
        r"profile='([^']+)'",
        log_text,
    )
    voice_from_log = extract_first_group(
        r"Realtime session initialized with "
        r"profile='[^']+' voice='([^']+)'",
        log_text,
    )
    backend_mode = extract_first_group(
        r"Configured Hugging Face realtime backend, "
        r"connection mode:\s*([^\r\n]+)",
        log_text,
    )

    terminal = build_terminal_diagnostic(
        interactions,
        log_text,
    )
    dance = build_dance_diagnostics(log_text)

    diagnostic = {
        "diagnostic_version": "1.0",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "mode": mode,
        "state": state,
        "session_id": session_id,
        "run_id": run_id,
        "profile": profile_from_log or profile,
        "voice": voice_from_log or voice,
        "backend_mode": backend_mode,
        "paths": {
            "central_log": str(central_log),
            "source_log": str(log_path),
            "source_session_directory": (
                str(source_session_dir)
                if source_session_dir is not None
                else None
            ),
        },
        "timing": {
            "transcript_started_at": (
                start_time.isoformat()
                if start_time is not None
                else None
            ),
            "transcript_finished_at": (
                end_time.isoformat()
                if end_time is not None
                else None
            ),
            "duration_seconds": duration_seconds,
        },
        "counts": {
            "final_interactions": len(interactions),
            "user_turns": sum(
                1
                for item in interactions
                if item["role"] == "user"
            ),
            "assistant_turns": sum(
                1
                for item in interactions
                if item["role"] == "assistant"
            ),
            "partial_user_transcripts": partial_count,
            "user_interventions": user_interventions,
            "tool_calls": tool_calls,
            "warnings": len(warnings),
            "errors": len(errors),
        },
        "audio": build_audio_diagnostics(log_text),
        "dance": dance,
        "terminal": terminal,
        "last_interaction": (
            interactions[-1]
            if interactions
            else None
        ),
        "warnings": warnings,
        "errors": errors,
    }

    atomic_write_text(
        output_dir / "interacciones.txt",
        format_interactions(
            interactions,
            mode=mode,
            session_id=session_id,
            run_id=run_id,
        ),
    )
    atomic_write_text(
        output_dir / "diagnostico.json",
        json.dumps(
            diagnostic,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )

    return diagnostic


def migrate_existing_sessions(
    sessions_root: Path,
    logs_root: Path,
) -> int:
    migrated = 0

    if not sessions_root.is_dir():
        return migrated

    for directory in sorted(sessions_root.glob("session_*")):
        if not directory.is_dir():
            continue

        match = re.fullmatch(
            r"session_(\d+)",
            directory.name,
        )

        if match is None:
            continue

        log_path = directory / "conversation_app.log"

        if not log_path.is_file():
            continue

        session_id = int(match.group(1))
        output_dir = (
            logs_root
            / "sessions"
            / f"session_{session_id:06d}"
        )

        try:
            generate(
                log_path=log_path,
                output_dir=output_dir,
                mode="identified_session",
                state="historical",
                session_id=session_id,
                run_id=None,
                profile="ahootsa_session",
                voice=None,
                source_session_dir=directory,
            )
            migrated += 1
        except Exception as exc:
            print(
                f"AVISO: no se pudo migrar {directory}: {exc}",
                file=sys.stderr,
            )

    return migrated


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("--log", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--mode",
        choices=("anonymous", "identified_session"),
    )
    parser.add_argument("--state", default="finished")
    parser.add_argument("--session-id", type=int)
    parser.add_argument("--run-id")
    parser.add_argument("--profile")
    parser.add_argument("--voice")
    parser.add_argument("--source-session-dir", type=Path)
    parser.add_argument("--migrate-sessions-root", type=Path)
    parser.add_argument("--logs-root", type=Path)

    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.migrate_sessions_root is not None:
        if args.logs_root is None:
            raise SystemExit(
                "--logs-root es obligatorio durante la migración."
            )

        count = migrate_existing_sessions(
            args.migrate_sessions_root,
            args.logs_root,
        )
        print(f"Sesiones históricas migradas: {count}")
        return 0

    required = {
        "--log": args.log,
        "--output-dir": args.output_dir,
        "--mode": args.mode,
    }
    missing = [
        name
        for name, value in required.items()
        if value is None
    ]

    if missing:
        raise SystemExit(
            "Faltan argumentos: " + ", ".join(missing)
        )

    diagnostic = generate(
        log_path=args.log,
        output_dir=args.output_dir,
        mode=args.mode,
        state=args.state,
        session_id=args.session_id,
        run_id=args.run_id,
        profile=args.profile,
        voice=args.voice,
        source_session_dir=args.source_session_dir,
    )

    print(
        json.dumps(
            {
                "output_dir": str(args.output_dir),
                "interactions": diagnostic["counts"][
                    "final_interactions"
                ],
                "warnings": diagnostic["counts"]["warnings"],
                "errors": diagnostic["counts"]["errors"],
                "possible_listening_stall": diagnostic[
                    "terminal"
                ]["possible_listening_stall"],
            },
            ensure_ascii=False,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
