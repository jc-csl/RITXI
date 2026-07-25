#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


IMPORTER_NAME = "ahootsa_session_report_12_6"


class ReportError(RuntimeError):
    pass


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def http_json(
    url: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    timeout: float = 20.0,
    allow_404: bool = False,
) -> Any:
    data = None
    headers = {"Accept": "application/json"}

    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"

    request = Request(url, data=data, headers=headers, method=method)

    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except HTTPError as exc:
        if allow_404 and exc.code == 404:
            return None
        detail = exc.read().decode("utf-8", errors="replace")
        raise ReportError(
            f"HTTP {exc.code} en {url}: {detail or exc.reason}"
        ) from exc
    except URLError as exc:
        raise ReportError(
            f"No se puede conectar con {url}: {exc.reason}"
        ) from exc

    if not raw:
        return None

    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ReportError(f"Respuesta JSON no válida de {url}") from exc


def decode_log(raw: bytes) -> str:
    if not raw:
        return ""

    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")

    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig", errors="replace")

    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue

    return raw.decode("utf-8", errors="replace")


def join_wrapped_content(content: str) -> str:
    """Reconstruct text split by a Windows PowerShell transcript."""
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


def parse_final_roles(log_path: Path) -> list[dict[str, Any]]:
    if not log_path.is_file():
        return []

    log_text = decode_log(log_path.read_bytes())
    entry_pattern = re.compile(
        r"(?ms)^\d{4}-\d{2}-\d{2} [^\r\n]*?\| "
        r"role=(user|assistant) content=(.*?)"
        r"(?=^\d{4}-\d{2}-\d{2} |^\*{10,}|\Z)"
    )

    roles: list[dict[str, Any]] = []

    for source_index, match in enumerate(entry_pattern.finditer(log_text)):
        role = match.group(1).strip()
        content = join_wrapped_content(match.group(2)).strip()
        lowered = content.lower()

        if not content:
            continue
        if content.startswith("{") and content.endswith("}"):
            continue
        if "used tool " in lowered and "args" in lowered:
            continue
        if content.startswith("[error]"):
            continue

        roles.append(
            {
                "source_index": source_index,
                "role": role,
                "content": content,
            }
        )

    return roles


def dialogue_from_first_user(
    roles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    for index, item in enumerate(roles):
        if item["role"] == "user":
            return roles[index:]
    return []


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}

    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}

    return value if isinstance(value, dict) else {}


def import_key(
    *,
    session_id: int,
    source_index: int,
    role: str,
    content: str,
) -> str:
    raw = f"{session_id}\0{source_index}\0{role}\0{content}".encode("utf-8")
    return sha256(raw).hexdigest()


def existing_import_keys(events: list[dict[str, Any]]) -> set[str]:
    keys: set[str] = set()

    for event in events:
        metadata = event.get("metadata")
        if not isinstance(metadata, dict):
            continue

        if metadata.get("importer") != IMPORTER_NAME:
            continue

        value = metadata.get("import_key")
        if isinstance(value, str) and value:
            keys.add(value)

    return keys


def import_dialogue(
    *,
    server_url: str,
    session_id: int,
    activity_key: str | None,
    log_path: Path,
    dialogue: list[dict[str, Any]],
) -> list[int]:
    current_events = http_json(
        f"{server_url}/sessions/{session_id}/events"
    )
    keys = existing_import_keys(current_events)
    created_ids: list[int] = []

    for item in dialogue:
        role = str(item["role"])
        content = str(item["content"])
        source_index = int(item["source_index"])
        key = import_key(
            session_id=session_id,
            source_index=source_index,
            role=role,
            content=content,
        )

        if key in keys:
            continue

        payload = {
            "event_type": (
                "user_response" if role == "user" else "robot_message"
            ),
            "source": "conversation_app",
            "activity": activity_key,
            "value_text": content,
            "success": None,
            "metadata": {
                "importer": IMPORTER_NAME,
                "import_key": key,
                "log_source_index": source_index,
                "role": role,
                "log_file": str(log_path),
                "imported_at": utc_now_iso(),
                "automatic_evaluation": False,
            },
        }

        created = http_json(
            f"{server_url}/sessions/{session_id}/events",
            method="POST",
            body=payload,
        )
        created_ids.append(int(created["id"]))
        keys.add(key)

    return created_ids


def finish_if_active(
    *,
    server_url: str,
    session_id: int,
) -> dict[str, Any] | None:
    bootstrap = http_json(f"{server_url}/panel/api/bootstrap")
    active = bootstrap.get("active_session")

    if not isinstance(active, dict):
        return None

    if int(active.get("session_id", -1)) != session_id:
        raise ReportError(
            "Hay otra sesión activa. No se finaliza automáticamente."
        )

    return http_json(
        f"{server_url}/panel/api/session/finish",
        method="POST",
        body={
            "note": (
                "Sesión finalizada al cerrar la Conversation App. "
                "La transcripción se ha importado automáticamente. "
                "La evaluación y el cambio de nivel corresponden "
                "al profesional."
            ),
            "decision": "no_decision",
        },
    )


def safe_get_summary(
    *,
    server_url: str,
    session_id: int,
) -> dict[str, Any]:
    summary = http_json(
        f"{server_url}/sessions/{session_id}/summary",
        allow_404=True,
    )
    return summary if isinstance(summary, dict) else {}


def make_report(
    *,
    session_id: int,
    context: dict[str, Any],
    status: dict[str, Any],
    summary: dict[str, Any],
    events: list[dict[str, Any]],
    roles: list[dict[str, Any]],
    dialogue: list[dict[str, Any]],
    created_ids: list[int],
    log_path: Path,
) -> dict[str, Any]:
    user = context.get("user")
    activity = context.get("activity")
    profile = context.get("profile")

    return {
        "report_version": "1.0",
        "generated_at": utc_now_iso(),
        "mode": "identified_session",
        "session_id": session_id,
        "status": summary.get("status") or status.get("status"),
        "user": user if isinstance(user, dict) else {},
        "profile": profile if isinstance(profile, dict) else {},
        "activity": activity if isinstance(activity, dict) else {},
        "timing": {
            "prepared_at": status.get("prepared_at"),
            "running_at": status.get("running_at"),
            "finished_at": status.get("finished_at"),
            "duration_seconds": summary.get("duration_seconds"),
            "duration_minutes": summary.get("duration_minutes"),
        },
        "professional_control": {
            "decision": status.get("professional_decision", "no_decision"),
            "automatic_level_change": False,
            "automatic_clinical_evaluation": False,
        },
        "counts": {
            "total_events": summary.get("total_events"),
            "user_responses": summary.get("user_responses"),
            "correct_responses": summary.get("correct_responses"),
            "incorrect_responses": summary.get("incorrect_responses"),
            "unanswered_responses": summary.get("unanswered_responses"),
            "hints_given": summary.get("hints_given"),
            "silences_detected": summary.get("silences_detected"),
            "errors_detected": summary.get("errors_detected"),
        },
        "automatic_observations": summary.get(
            "automatic_observations", []
        ),
        "automatic_summary_text": summary.get(
            "automatic_summary_text", ""
        ),
        "transcription": {
            "log_file": str(log_path),
            "final_roles_detected": len(roles),
            "dialogue_roles_imported_or_existing": len(dialogue),
            "created_event_ids_this_run": created_ids,
            "turns": dialogue,
        },
        "event_ids": [
            int(event["id"])
            for event in events
            if isinstance(event, dict) and "id" in event
        ],
    }


def render_html(report: dict[str, Any]) -> str:
    user = report.get("user") or {}
    activity = report.get("activity") or {}
    timing = report.get("timing") or {}
    counts = report.get("counts") or {}
    transcription = report.get("transcription") or {}
    turns = transcription.get("turns") or []

    turn_rows = []
    for item in turns:
        role = "Persona usuaria" if item.get("role") == "user" else "Aocha"
        turn_rows.append(
            "<tr>"
            f"<td>{escape(role)}</td>"
            f"<td>{escape(str(item.get('content', '')))}</td>"
            "</tr>"
        )

    if not turn_rows:
        turn_rows.append(
            "<tr><td colspan='2'>No se detectaron turnos finales "
            "en el log.</td></tr>"
        )

    observations = report.get("automatic_observations") or []
    observation_items = "".join(
        f"<li>{escape(str(value))}</li>" for value in observations
    )
    if not observation_items:
        observation_items = "<li>Sin observaciones automáticas.</li>"

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Informe de sesión Ahootsa {report.get('session_id')}</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 32px; color: #1f2937; }}
h1, h2 {{ color: #123b63; }}
.card {{ border: 1px solid #d1d5db; border-radius: 8px; padding: 16px; margin: 14px 0; }}
.grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }}
.label {{ font-weight: bold; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #d1d5db; padding: 8px; vertical-align: top; }}
th {{ background: #eef3f8; text-align: left; }}
.note {{ background: #fff8db; padding: 12px; border-left: 4px solid #d6a800; }}
</style>
</head>
<body>
<h1>Informe de sesión Ahootsa</h1>

<div class="card grid">
<div><span class="label">Sesión:</span> {escape(str(report.get('session_id', '')))}</div>
<div><span class="label">Estado:</span> {escape(str(report.get('status', '')))}</div>
<div><span class="label">Persona:</span> {escape(str(user.get('preferred_name') or user.get('name') or ''))}</div>
<div><span class="label">Identificador:</span> {escape(str(user.get('external_id', '')))}</div>
<div><span class="label">Actividad:</span> {escape(str(activity.get('title') or activity.get('key') or ''))}</div>
<div><span class="label">Nivel:</span> {escape(str(activity.get('level_title') or activity.get('level') or ''))}</div>
<div><span class="label">Inicio:</span> {escape(str(timing.get('running_at') or timing.get('prepared_at') or ''))}</div>
<div><span class="label">Duración:</span> {escape(str(timing.get('duration_minutes') or ''))} minutos</div>
</div>

<h2>Resumen de registro</h2>
<div class="card grid">
<div><span class="label">Respuestas:</span> {escape(str(counts.get('user_responses', 0)))}</div>
<div><span class="label">Adecuadas:</span> {escape(str(counts.get('correct_responses', 0)))}</div>
<div><span class="label">Incorrectas:</span> {escape(str(counts.get('incorrect_responses', 0)))}</div>
<div><span class="label">Sin evaluación automática:</span> {escape(str(counts.get('unanswered_responses', 0)))}</div>
<div><span class="label">Pistas:</span> {escape(str(counts.get('hints_given', 0)))}</div>
<div><span class="label">Silencios:</span> {escape(str(counts.get('silences_detected', 0)))}</div>
</div>

<h2>Conversación</h2>
<table>
<thead><tr><th>Interlocutor</th><th>Texto</th></tr></thead>
<tbody>
{''.join(turn_rows)}
</tbody>
</table>

<h2>Observaciones automáticas</h2>
<ul>{observation_items}</ul>

<p class="note">
Este informe no realiza una evaluación clínica ni decide cambios de nivel.
La valoración final corresponde al profesional.
</p>
</body>
</html>
"""


def write_report_files(
    *,
    session_dir: Path,
    report: dict[str, Any],
) -> dict[str, str]:
    session_dir.mkdir(parents=True, exist_ok=True)

    json_path = session_dir / "informe_sesion.json"
    html_path = session_dir / "informe_sesion.html"
    transcript_path = session_dir / "transcripcion_sesion.txt"

    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    html_path.write_text(render_html(report), encoding="utf-8")

    lines = []
    for item in report["transcription"]["turns"]:
        label = "Usuario" if item["role"] == "user" else "Aocha"
        lines.append(f"{label}: {item['content']}")

    transcript_path.write_text(
        "\n".join(lines) + ("\n" if lines else ""),
        encoding="utf-8",
    )

    return {
        "json": str(json_path),
        "html": str(html_path),
        "transcript": str(transcript_path),
    }


def resolve_session_dir(
    *,
    context_path: Path,
    status_path: Path,
) -> Path:
    if context_path.is_file():
        return context_path.parent
    if status_path.is_file():
        return status_path.parent
    raise ReportError("No se puede resolver la carpeta de la sesión.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Importa la conversación final, cierra una sesión identificada "
            "y genera su informe."
        )
    )
    parser.add_argument("--session-id", required=True, type=int)
    parser.add_argument("--server-url", default="http://127.0.0.1:8100")
    parser.add_argument("--log", required=True)
    parser.add_argument("--session-dir", required=True)
    args = parser.parse_args()

    session_id = args.session_id
    server_url = args.server_url.rstrip("/")
    log_path = Path(args.log).resolve()
    session_dir = Path(args.session_dir).resolve()
    context_path = session_dir / "session_context.json"
    status_path = session_dir / "session_status.json"

    try:
        context = load_json(context_path)
        status = load_json(status_path)
        activity = context.get("activity")
        activity_key = (
            activity.get("key")
            if isinstance(activity, dict)
            else None
        )

        roles = parse_final_roles(log_path)
        dialogue = dialogue_from_first_user(roles)

        created_ids = import_dialogue(
            server_url=server_url,
            session_id=session_id,
            activity_key=activity_key,
            log_path=log_path,
            dialogue=dialogue,
        )

        finish_if_active(
            server_url=server_url,
            session_id=session_id,
        )

        summary = safe_get_summary(
            server_url=server_url,
            session_id=session_id,
        )
        events = http_json(
            f"{server_url}/sessions/{session_id}/events"
        )

        status = load_json(status_path)

        report = make_report(
            session_id=session_id,
            context=context,
            status=status,
            summary=summary,
            events=events,
            roles=roles,
            dialogue=dialogue,
            created_ids=created_ids,
            log_path=log_path,
        )
        paths = write_report_files(
            session_dir=session_dir,
            report=report,
        )

        print("")
        print("INFORME DE SESION GENERADO")
        print(f"Sesion: {session_id}")
        print(f"Turnos detectados: {len(dialogue)}")
        print(f"Eventos nuevos: {len(created_ids)}")
        print(f"HTML: {paths['html']}")
        print(f"JSON: {paths['json']}")
        print(f"Transcripcion: {paths['transcript']}")
        return 0

    except ReportError as exc:
        pending_path = session_dir / "informe_sesion_pendiente.json"
        pending_path.parent.mkdir(parents=True, exist_ok=True)
        pending_path.write_text(
            json.dumps(
                {
                    "generated_at": utc_now_iso(),
                    "session_id": session_id,
                    "error": str(exc),
                    "log_file": str(log_path),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"ERROR AL GENERAR EL INFORME: {exc}", file=sys.stderr)
        print(f"Pendiente: {pending_path}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
