#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile


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
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        if not completed.stdout.strip():
            print("El verificador no devolvió JSON.", file=sys.stderr)
            if completed.stderr:
                print(completed.stderr, file=sys.stderr)
            return 1

        try:
            result = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            print(f"JSON no válido: {exc}", file=sys.stderr)
            print(completed.stdout, file=sys.stderr)
            return 1

        if completed.returncode != 0:
            print(result, file=sys.stderr)
            return 1

        if not result.get("ok"):
            print(result, file=sys.stderr)
            return 1

        if result.get("found_count") != 2:
            print(result, file=sys.stderr)
            return 1

        if result.get("missing_ids"):
            print(result, file=sys.stderr)
            return 1

        print(
            json.dumps(
                {
                    "ok": True,
                    "found_count": result["found_count"],
                    "ids": result["requested_ids"],
                },
                ensure_ascii=False,
            )
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
