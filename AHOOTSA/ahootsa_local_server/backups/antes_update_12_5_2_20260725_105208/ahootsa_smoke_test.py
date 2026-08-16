#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import socket
import sqlite3
import subprocess
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import webbrowser


SERVER_URL = "http://127.0.0.1:8100"
APP_URL = "http://127.0.0.1:7860"
DAEMON_URL = "http://127.0.0.1:8000"
EXPECTED_VERSION = "0.12.5"
TEST_USER_ID = "SMOKE-TEST-01"
TEST_USER_NAME = "Persona de prueba final"
TEST_PREFERRED_NAME = "Álex"
ACTIVITY_KEY = "express_preferences"
ACTIVITY_LEVEL = "initial"
ROLE_PATTERN = re.compile(r"role=(user|assistant)\s+content=(.*)$")


class SmokeTestError(RuntimeError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def print_step(number: int, text: str) -> None:
    print(f"\n{number}. {text}")


def http_json(
    url: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    timeout: float = 15.0,
) -> Any:
    data = None
    headers = {"Accept": "application/json"}

    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"

    request = Request(
        url=url,
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SmokeTestError(
            f"HTTP {exc.code} en {url}: {detail or exc.reason}"
        ) from exc
    except URLError as exc:
        raise SmokeTestError(f"No se puede conectar con {url}: {exc.reason}") from exc

    if not raw:
        return None

    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise SmokeTestError(f"Respuesta JSON inválida de {url}") from exc


def port_open(port: int, timeout: float = 0.4) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=timeout):
            return True
    except OSError:
        return False


def wait_port(port: int, timeout_seconds: float) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if port_open(port):
            return True
        time.sleep(0.5)
    return port_open(port)


def start_powershell(script: Path, cwd: Path) -> None:
    if os.name != "nt":
        raise SmokeTestError("Esta prueba de servicios solo se ejecuta en Windows.")

    creation_flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
    subprocess.Popen(
        [
            "powershell.exe",
            "-NoExit",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
        ],
        cwd=str(cwd),
        creationflags=creation_flags,
    )


def run_powershell_command(command: str, cwd: Path) -> None:
    completed = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise SmokeTestError(
            "Falló una operación PowerShell:\n"
            + (completed.stderr or completed.stdout)
        )


def stop_conversation_app(project_root: Path) -> None:
    if not port_open(7860):
        return

    if port_open(8000):
        try:
            http_json(
                f"{DAEMON_URL}/api/apps/stop-current-app",
                method="POST",
                body={},
                timeout=5,
            )
        except SmokeTestError:
            pass

        deadline = time.monotonic() + 8
        while time.monotonic() < deadline and port_open(7860):
            time.sleep(0.5)

    if not port_open(7860):
        return

    utils = project_root / "scripts" / "ahootsa_process_utils.ps1"
    if not utils.is_file():
        raise SmokeTestError(
            "La Conversation App anterior sigue activa y no se encuentra "
            "ahootsa_process_utils.ps1 para detenerla."
        )

    command = (
        f". '{utils}'; "
        "Stop-AhootsaPortProcess "
        "-Port 7860 "
        "-ServiceName 'Reachy Mini Conversation App' | Out-Null"
    )
    run_powershell_command(command, project_root)

    if port_open(7860):
        raise SmokeTestError("No se pudo liberar el puerto 7860.")


def ensure_server(project_root: Path, server_root: Path) -> dict[str, Any]:
    try:
        health = http_json(f"{SERVER_URL}/health", timeout=3)
    except SmokeTestError:
        launcher = server_root / "3_lanzar_ahootsa_server.ps1"
        if not launcher.is_file():
            raise SmokeTestError(f"No existe el lanzador del servidor: {launcher}")

        print("   El servidor no estaba activo. Se abre una consola nueva.")
        start_powershell(launcher, server_root)

        if not wait_port(8100, 45):
            raise SmokeTestError(
                "Ahootsa Local Server no respondió en el puerto 8100."
            )
        health = http_json(f"{SERVER_URL}/health")

    if str(health.get("version")) != EXPECTED_VERSION:
        raise SmokeTestError(
            f"Versión incorrecta del servidor: {health.get('version')}. "
            f"Se esperaba {EXPECTED_VERSION}."
        )

    return health


def ensure_test_user() -> None:
    users = http_json(f"{SERVER_URL}/users")
    existing = next(
        (
            user
            for user in users
            if user.get("external_id") == TEST_USER_ID
        ),
        None,
    )

    if existing is None:
        http_json(
            f"{SERVER_URL}/users",
            method="POST",
            body={
                "external_id": TEST_USER_ID,
                "name": TEST_USER_NAME,
                "preferred_name": TEST_PREFERRED_NAME,
                "language": "es",
                "notes": (
                    "Usuario técnico de la prueba final. "
                    "No representa una persona real."
                ),
            },
        )
        print("   Usuario técnico creado.")
    else:
        print("   Usuario técnico reutilizado.")

    http_json(
        f"{SERVER_URL}/users/{TEST_USER_ID}/profile",
        method="PUT",
        body={
            "communication_style": "simple",
            "speech_speed": "normal",
            "response_wait_seconds": 5.0,
            "preferred_interaction_mode": "mixed",
            "preferred_reinforcement": "refuerzo verbal positivo",
            "interests": "música y actividades cotidianas",
            "avoid_topics": None,
            "accessibility_notes": (
                "Una pregunta por turno y un máximo de dos opciones."
            ),
            "max_instructions_per_turn": 1,
        },
    )


def close_previous_technical_session() -> None:
    bootstrap = http_json(f"{SERVER_URL}/panel/api/bootstrap")
    active = bootstrap.get("active_session")

    if active is None:
        return

    user = active.get("user") or {}
    external_id = user.get("external_id")
    session_id = active.get("session_id")

    if external_id not in {TEST_USER_ID, "AUTO-CONVERSACION-01"}:
        raise SmokeTestError(
            f"Existe una sesión activa real o no identificada: {session_id}. "
            "Finalízala desde el panel antes de continuar."
        )

    http_json(
        f"{SERVER_URL}/panel/api/session/finish",
        method="POST",
        body={
            "note": (
                "Sesión técnica anterior cerrada automáticamente "
                "por la prueba final 12.5."
            ),
            "decision": "no_decision",
        },
    )
    print(f"   Se cerró la sesión técnica anterior {session_id}.")


def prepare_session() -> dict[str, Any]:
    return http_json(
        f"{SERVER_URL}/panel/api/session/prepare",
        method="POST",
        body={
            "user_external_id": TEST_USER_ID,
            "activity": ACTIVITY_KEY,
            "level": ACTIVITY_LEVEL,
            "started_by": "Prueba final Ahootsa 12.5",
        },
    )


def ensure_daemon(project_root: Path) -> None:
    if port_open(8000):
        print("   Daemon Reachy/MuJoCo ya activo.")
        return

    launcher = project_root / "1_lanzar_daemon_mujoco.ps1"
    if not launcher.is_file():
        raise SmokeTestError(f"No existe el lanzador de MuJoCo: {launcher}")

    print("   Se abre una consola para Reachy Mini daemon/MuJoCo.")
    start_powershell(launcher, project_root)

    if not wait_port(8000, 60):
        raise SmokeTestError("El daemon no respondió en el puerto 8000.")


def launch_conversation_app(project_root: Path) -> None:
    try:
        result = http_json(
            f"{SERVER_URL}/panel/api/launch/conversation-app",
            method="POST",
            body={},
            timeout=20,
        )
        message = result.get("message") if isinstance(result, dict) else None
        if message:
            print(f"   {message}")
    except SmokeTestError:
        launcher = project_root / "2_lanzar_app_ahootsa.ps1"
        if not launcher.is_file():
            raise
        print("   El panel no pudo lanzarla. Se utiliza el lanzador estable.")
        start_powershell(launcher, project_root)

    if not wait_port(7860, 150):
        raise SmokeTestError(
            "La Conversation App no respondió en el puerto 7860 en 150 segundos."
        )


def ensure_profile_and_mic() -> dict[str, Any]:
    profile_status = http_json(f"{APP_URL}/api/v1/personalities")
    current = profile_status.get("current")

    if current != "ahootsa_session":
        print(f"   Perfil actual: {current}. Se aplica ahootsa_session.")
        http_json(
            f"{APP_URL}/api/v1/personalities/apply",
            method="POST",
            body={"name": "ahootsa_session", "persist": True},
            timeout=20,
        )
        time.sleep(3)
        profile_status = http_json(f"{APP_URL}/api/v1/personalities")

    if profile_status.get("current") != "ahootsa_session":
        raise SmokeTestError(
            "La aplicación oficial no ha cargado ahootsa_session."
        )

    loaded = http_json(
        f"{APP_URL}/api/v1/personalities/load?name=ahootsa_session"
    )
    greeting = str(loaded.get("greeting") or "")

    if TEST_PREFERRED_NAME not in greeting:
        raise SmokeTestError(
            "El saludo del perfil activo no contiene el nombre personalizado."
        )

    http_json(
        f"{APP_URL}/api/v1/mic",
        method="POST",
        body={"muted": False},
    )

    mic = http_json(f"{APP_URL}/api/v1/mic")
    if mic.get("muted") is True:
        raise SmokeTestError("El micrófono continúa silenciado.")

    return {
        "profile_status": profile_status,
        "loaded_profile": loaded,
        "greeting": greeting,
    }


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


def read_roles(log_path: Path) -> list[tuple[str, str]]:
    try:
        text = decode_log(log_path.read_bytes())
    except FileNotFoundError:
        return []

    roles: list[tuple[str, str]] = []
    for line in text.splitlines():
        match = ROLE_PATTERN.search(line.strip())
        if not match:
            continue

        role = match.group(1).strip()
        content = match.group(2).strip()

        if not content:
            continue
        if content.startswith("{") and content.endswith("}"):
            continue
        if "tool " in content.lower() and "args" in content.lower():
            continue

        roles.append((role, content))

    return roles


def capture_brief_conversation(
    log_path: Path,
    timeout_seconds: int,
) -> tuple[str, str]:
    deadline_for_log = time.monotonic() + 30
    while time.monotonic() < deadline_for_log and not log_path.exists():
        time.sleep(0.5)

    if not log_path.exists():
        raise SmokeTestError(f"No se creó el log de sesión: {log_path}")

    baseline_count = len(read_roles(log_path))

    print("\n   La aplicación está preparada y el micrófono está abierto.")
    print("   Habla ahora con Aocha.")
    print('   Frase sugerida: "Prefiero la música."')
    print("   Responde una vez más si Aocha hace otra pregunta.")
    print(
        f"   La prueba dispone de {timeout_seconds} segundos para detectar "
        "una intervención y una respuesta."
    )
    print("")

    deadline = time.monotonic() + timeout_seconds
    user_text: str | None = None

    while time.monotonic() < deadline:
        current = read_roles(log_path)
        new_items = current[baseline_count:]

        for role, content in new_items:
            if user_text is None:
                if role == "user":
                    user_text = content
                    print(f"   Usuario detectado: {content}")
                continue

            if role == "assistant":
                print(f"   Aocha detectada: {content}")
                return user_text, content

        time.sleep(1)

    raise SmokeTestError(
        "No se detectó en el log una intervención del usuario seguida de "
        "una respuesta de Aocha."
    )


def register_transcripts(
    *,
    session_id: int,
    user_text: str,
    assistant_text: str,
    log_path: Path,
) -> list[int]:
    metadata_base = {
        "smoke_test": "12.5",
        "captured_from": "conversation_app_log",
        "log_file": str(log_path),
        "captured_at": now_iso(),
    }

    created_user = http_json(
        f"{SERVER_URL}/sessions/{session_id}/events",
        method="POST",
        body={
            "event_type": "user_response",
            "source": "conversation_app",
            "activity": ACTIVITY_KEY,
            "value_text": user_text,
            "success": None,
            "metadata": {
                **metadata_base,
                "role": "user",
            },
        },
    )

    created_assistant = http_json(
        f"{SERVER_URL}/sessions/{session_id}/events",
        method="POST",
        body={
            "event_type": "robot_message",
            "source": "conversation_app",
            "activity": ACTIVITY_KEY,
            "value_text": assistant_text,
            "success": None,
            "metadata": {
                **metadata_base,
                "role": "assistant",
            },
        },
    )

    created_metric = http_json(
        f"{SERVER_URL}/sessions/{session_id}/events",
        method="POST",
        body={
            "event_type": "technical_metric",
            "source": "system",
            "activity": ACTIVITY_KEY,
            "value_text": "Prueba final con servicios 8000, 7860 y 8100 activos.",
            "value_number": 3,
            "success": True,
            "metadata": {
                **metadata_base,
                "ports": [8000, 7860, 8100],
                "profile": "ahootsa_session",
            },
        },
    )

    return [
        int(created_user["id"]),
        int(created_assistant["id"]),
        int(created_metric["id"]),
    ]


def verify_persistence(
    *,
    server_root: Path,
    session_id: int,
    event_ids: list[int],
    user_text: str,
    assistant_text: str,
) -> dict[str, Any]:
    events = http_json(f"{SERVER_URL}/sessions/{session_id}/events")
    by_id = {int(event["id"]): event for event in events}

    missing = [event_id for event_id in event_ids if event_id not in by_id]
    if missing:
        raise SmokeTestError(
            f"La API no devuelve los eventos registrados: {missing}"
        )

    if by_id[event_ids[0]].get("value_text") != user_text:
        raise SmokeTestError("La transcripción de usuario no coincide en la API.")
    if by_id[event_ids[1]].get("value_text") != assistant_text:
        raise SmokeTestError("La respuesta de Aocha no coincide en la API.")

    db_path = server_root / "data" / "ahootsa.db"
    if not db_path.is_file():
        raise SmokeTestError(f"No se encuentra SQLite: {db_path}")

    placeholders = ",".join("?" for _ in event_ids)
    connection = sqlite3.connect(str(db_path))
    try:
        rows = connection.execute(
            f"""
            SELECT id, session_id, event_type, value_text
            FROM session_events
            WHERE id IN ({placeholders})
            ORDER BY id
            """,
            event_ids,
        ).fetchall()
    finally:
        connection.close()

    sqlite_ids = {int(row[0]) for row in rows}
    missing_sqlite = [
        event_id for event_id in event_ids if event_id not in sqlite_ids
    ]
    if missing_sqlite:
        raise SmokeTestError(
            f"SQLite no contiene los eventos registrados: {missing_sqlite}"
        )

    wrong_session = [
        int(row[0]) for row in rows if int(row[1]) != session_id
    ]
    if wrong_session:
        raise SmokeTestError(
            f"Hay eventos asociados a otra sesión: {wrong_session}"
        )

    summary = http_json(f"{SERVER_URL}/sessions/{session_id}/summary")
    if summary.get("status") != "finished":
        raise SmokeTestError("El resumen de la sesión no indica finished.")

    if int(summary.get("user_responses", 0)) < 1:
        raise SmokeTestError("El resumen no registra la respuesta del usuario.")

    return {
        "api_event_count": len(events),
        "sqlite_rows": [
            {
                "id": int(row[0]),
                "session_id": int(row[1]),
                "event_type": row[2],
                "value_text": row[3],
            }
            for row in rows
        ],
        "summary": summary,
    }


def finish_session(note: str, decision: str = "no_decision") -> dict[str, Any]:
    return http_json(
        f"{SERVER_URL}/panel/api/session/finish",
        method="POST",
        body={
            "note": note,
            "decision": decision,
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Prueba final guiada de Ahootsa con servidor, daemon, "
            "Conversation App, audio, perfil y registro."
        )
    )
    parser.add_argument(
        "--timeout-conversation",
        type=int,
        default=180,
    )
    parser.add_argument(
        "--keep-app-running",
        action="store_true",
        help="No detener la Conversation App al finalizar.",
    )
    args = parser.parse_args()

    server_root = Path(__file__).resolve().parent.parent
    project_root = server_root.parent

    prepared: dict[str, Any] | None = None
    session_finished = False
    report_path: Path | None = None

    try:
        print("=" * 70)
        print("PRUEBA FINAL AHOOTSA 12.5")
        print("Servicios reales + conversación breve + registro persistente")
        print("=" * 70)

        print_step(1, "Comprobar y arrancar Ahootsa Local Server")
        health = ensure_server(project_root, server_root)
        print(f"   Servidor {health['version']} activo en 8100.")

        print_step(2, "Limpiar una posible ejecución anterior")
        stop_conversation_app(project_root)
        close_previous_technical_session()
        print("   No hay una Conversation App ni una sesión técnica anterior.")

        print_step(3, "Preparar usuario técnico y sesión personalizada")
        ensure_test_user()
        prepared = prepare_session()
        session_id = int(prepared["session_id"])
        log_path = Path(prepared["log_file"])
        session_directory = Path(prepared["session_directory"])
        report_path = session_directory / "smoke_test_report_12_5.json"

        print(f"   Sesión {session_id} preparada.")
        print(f"   Perfil: {prepared['profile_name']}")
        print(f"   Saludo: {prepared['greeting']}")

        print_step(4, "Arrancar Reachy Mini daemon y MuJoCo")
        ensure_daemon(project_root)
        print("   Puerto 8000 activo.")

        print_step(5, "Arrancar la Conversation App oficial")
        launch_conversation_app(project_root)
        print("   Puerto 7860 activo.")

        print_step(6, "Verificar perfil personalizado, voz y micrófono")
        profile = ensure_profile_and_mic()
        print("   Perfil actual: ahootsa_session")
        print(f"   Voz: {profile['loaded_profile'].get('voice')}")
        print("   Micrófono: activo")

        webbrowser.open(APP_URL)

        print_step(7, "Mantener los tres servicios activos")
        service_ports = {
            "daemon_8000": port_open(8000),
            "conversation_app_7860": port_open(7860),
            "local_server_8100": port_open(8100),
        }
        if not all(service_ports.values()):
            raise SmokeTestError(
                f"No están activos los tres servicios: {service_ports}"
            )
        print("   8000, 7860 y 8100 están activos simultáneamente.")

        print_step(8, "Realizar una conversación breve real")
        user_text, assistant_text = capture_brief_conversation(
            log_path,
            args.timeout_conversation,
        )

        print_step(9, "Registrar las transcripciones en la sesión")
        event_ids = register_transcripts(
            session_id=session_id,
            user_text=user_text,
            assistant_text=assistant_text,
            log_path=log_path,
        )
        print(f"   Eventos registrados: {event_ids}")

        print_step(10, "Finalizar la sesión desde el panel profesional")
        finished = finish_session(
            "Prueba final 12.5 completada con conversación real "
            "capturada desde el log oficial."
        )
        session_finished = True
        print(
            f"   Sesión finalizada. Duración: "
            f"{finished.get('duration_minutes')} min."
        )

        print_step(11, "Verificar API, SQLite y resumen")
        verification = verify_persistence(
            server_root=server_root,
            session_id=session_id,
            event_ids=event_ids,
            user_text=user_text,
            assistant_text=assistant_text,
        )
        print("   API: eventos recuperados.")
        print("   SQLite: eventos persistentes.")
        print("   Resumen: sesión finalizada con respuesta de usuario.")

        report = {
            "test": "AHOOTSA_SMOKE_TEST_12_5",
            "success": True,
            "verified_at": now_iso(),
            "server_version": health["version"],
            "session_id": session_id,
            "session_directory": str(session_directory),
            "profile": profile["profile_status"],
            "voice": profile["loaded_profile"].get("voice"),
            "greeting": profile["greeting"],
            "services": service_ports,
            "conversation": {
                "user": user_text,
                "assistant": assistant_text,
                "log_file": str(log_path),
            },
            "registered_event_ids": event_ids,
            "verification": verification,
        }
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        print("\n" + "=" * 70)
        print("PRUEBA FINAL 12.5 VALIDADA")
        print("Servidor + MuJoCo + Conversation App + perfil + audio + registro")
        print("=" * 70)
        print(f"Sesión: {session_id}")
        print(f"Usuario: {user_text}")
        print(f"Aocha: {assistant_text}")
        print(f"Informe: {report_path}")

        return 0

    except (SmokeTestError, KeyboardInterrupt) as exc:
        message = str(exc) if not isinstance(exc, KeyboardInterrupt) else (
            "Prueba interrumpida por el usuario."
        )
        print(f"\nERROR DE LA PRUEBA FINAL: {message}", file=sys.stderr)

        if prepared is not None and not session_finished:
            try:
                finish_session(
                    "Prueba final 12.5 abortada: " + message,
                    decision="no_decision",
                )
                session_finished = True
            except Exception:
                pass

        if report_path is not None:
            try:
                report_path.parent.mkdir(parents=True, exist_ok=True)
                report_path.write_text(
                    json.dumps(
                        {
                            "test": "AHOOTSA_SMOKE_TEST_12_5",
                            "success": False,
                            "verified_at": now_iso(),
                            "error": message,
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                    encoding="utf-8",
                )
            except Exception:
                pass

        return 1

    finally:
        if not args.keep_app_running:
            try:
                stop_conversation_app(project_root)
            except Exception as exc:
                print(
                    f"AVISO: no se pudo cerrar la Conversation App: {exc}",
                    file=sys.stderr,
                )


if __name__ == "__main__":
    sys.exit(main())
