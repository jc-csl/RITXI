#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import sys
from typing import Any


def emit_json(payload: dict[str, Any]) -> None:
    # ASCII-only JSON avoids Windows console/code-page decoding problems.
    print(json.dumps(payload, ensure_ascii=True))


def build_result(
    *,
    db_path: Path,
    session_id: int,
    requested_ids: list[int],
) -> dict[str, Any]:
    return {
        "db_path": str(db_path),
        "session_id": session_id,
        "requested_ids": requested_ids,
        "found_count": 0,
        "missing_ids": [],
        "wrong_session": [],
        "rows": [],
        "ok": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that several events exist in SQLite and belong "
            "to one session."
        )
    )
    parser.add_argument("--db", required=True)
    parser.add_argument("--session-id", required=True, type=int)
    parser.add_argument("--ids", required=True)
    args = parser.parse_args()

    db_path = Path(args.db).resolve()

    try:
        requested_ids = [
            int(value.strip())
            for value in args.ids.split(",")
            if value.strip()
        ]
    except ValueError:
        result = build_result(
            db_path=db_path,
            session_id=args.session_id,
            requested_ids=[],
        )
        result["error"] = "invalid_event_ids"
        emit_json(result)
        return 2

    result = build_result(
        db_path=db_path,
        session_id=args.session_id,
        requested_ids=requested_ids,
    )

    if not requested_ids:
        result["error"] = "empty_event_ids"
        emit_json(result)
        return 2

    if not db_path.is_file():
        result["error"] = "database_not_found"
        emit_json(result)
        return 2

    placeholders = ",".join("?" for _ in requested_ids)
    sql = f"""
        SELECT
            id,
            session_id,
            event_type,
            source,
            activity,
            value_text,
            success,
            metadata_json,
            occurred_at
        FROM session_events
        WHERE id IN ({placeholders})
        ORDER BY id
    """

    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(sql, requested_ids).fetchall()
    except sqlite3.Error as exc:
        result["error"] = "sqlite_query_failed"
        result["detail"] = str(exc)
        emit_json(result)
        return 2
    finally:
        connection.close()

    by_id = {int(row["id"]): row for row in rows}

    for event_id in requested_ids:
        row = by_id.get(event_id)

        if row is None:
            result["missing_ids"].append(event_id)
            continue

        actual_session_id = int(row["session_id"])
        if actual_session_id != args.session_id:
            result["wrong_session"].append(
                {
                    "id": event_id,
                    "actual_session_id": actual_session_id,
                }
            )

        result["rows"].append(
            {
                "id": int(row["id"]),
                "session_id": actual_session_id,
                "event_type": row["event_type"],
                "source": row["source"],
                "activity": row["activity"],
                "value_text": row["value_text"],
                "success": (
                    None
                    if row["success"] is None
                    else bool(row["success"])
                ),
                "metadata_json": row["metadata_json"],
                "occurred_at": row["occurred_at"],
            }
        )

    result["found_count"] = len(result["rows"])
    result["ok"] = (
        not result["missing_ids"]
        and not result["wrong_session"]
        and result["found_count"] == len(requested_ids)
    )

    emit_json(result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
