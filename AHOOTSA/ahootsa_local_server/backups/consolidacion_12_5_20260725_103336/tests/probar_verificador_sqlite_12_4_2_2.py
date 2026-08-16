#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile


def decode_output(raw: bytes | None) -> str:
    if not raw:
        return ""

    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue

    return raw.decode("utf-8", errors="replace")


def main() -> int:
    verifier = Path(__file__).with_name(
        "verificar_eventos_sqlite_12_4_2.py"
    )

    with tempfile.TemporaryDirectory(prefix="ahootsa_sqlite_test_") as temp:
        db_path = Path(temp) / "fixture.db"

        connection = sqlite3.connect(str(db_path))
        try:
            connection.executescript(
                """
                CREATE TABLE session_events (
                    id INTEGER PRIMARY KEY,
                    session_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    source TEXT,
                    activity TEXT,
                    value_text TEXT,
                    success INTEGER,
                    metadata_json TEXT,
                    occurred_at TEXT
                );

                INSERT INTO session_events (
                    id,
                    session_id,
                    event_type,
                    source,
                    activity,
                    value_text,
                    success,
                    metadata_json,
                    occurred_at
                ) VALUES
                    (
                        70,
                        9,
                        'user_response',
                        'conversation_app',
                        'express_preferences',
                        'Música.',
                        1,
                        '{"automatic_test": true}',
                        '2026-07-25T09:00:00'
                    ),
                    (
                        71,
                        9,
                        'robot_message',
                        'conversation_app',
                        'express_preferences',
                        'Muy bien.',
                        NULL,
                        '{"automatic_test": true}',
                        '2026-07-25T09:00:01'
                    );
                """
            )
            connection.commit()
        finally:
            connection.close()

        environment = os.environ.copy()
        environment["PYTHONUTF8"] = "1"
        environment["PYTHONIOENCODING"] = "utf-8"

        completed = subprocess.run(
            [
                sys.executable,
                str(verifier),
                "--db",
                str(db_path),
                "--session-id",
                "9",
                "--ids",
                "70,71",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            env=environment,
            check=False,
        )

        stdout_text = decode_output(completed.stdout).strip()
        stderr_text = decode_output(completed.stderr).strip()

        if not stdout_text:
            print(
                "El verificador no devolvió JSON.",
                file=sys.stderr,
            )
            if stderr_text:
                print(stderr_text, file=sys.stderr)
            return 1

        try:
            result = json.loads(stdout_text)
        except json.JSONDecodeError as exc:
            print(f"JSON no válido: {exc}", file=sys.stderr)
            print(stdout_text, file=sys.stderr)
            if stderr_text:
                print(stderr_text, file=sys.stderr)
            return 1

        if completed.returncode != 0:
            print(json.dumps(result, ensure_ascii=True), file=sys.stderr)
            if stderr_text:
                print(stderr_text, file=sys.stderr)
            return 1

        if not result.get("ok"):
            print(json.dumps(result, ensure_ascii=True), file=sys.stderr)
            return 1

        if result.get("found_count") != 2:
            print(json.dumps(result, ensure_ascii=True), file=sys.stderr)
            return 1

        if result.get("missing_ids"):
            print(json.dumps(result, ensure_ascii=True), file=sys.stderr)
            return 1

        print(
            json.dumps(
                {
                    "ok": True,
                    "found_count": result["found_count"],
                    "ids": result["requested_ids"],
                },
                ensure_ascii=True,
            )
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
