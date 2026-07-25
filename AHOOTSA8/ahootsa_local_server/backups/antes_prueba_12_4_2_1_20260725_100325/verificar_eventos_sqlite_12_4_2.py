#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sqlite3
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', required=True)
    parser.add_argument('--session-id', required=True, type=int)
    parser.add_argument('--ids', required=True)
    args = parser.parse_args()

    db_path = Path(args.db).resolve()
    requested_ids = [int(v) for v in args.ids.split(',') if v.strip()]
    result = {
        'db_path': str(db_path),
        'session_id': args.session_id,
        'requested_ids': requested_ids,
        'found_count': 0,
        'missing_ids': [],
        'wrong_session': [],
        'rows': [],
        'ok': False,
    }

    if not db_path.is_file():
        result['error'] = 'database_not_found'
        print(json.dumps(result, ensure_ascii=False))
        return 2

    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    try:
        placeholders = ','.join('?' for _ in requested_ids)
        sql = (
            'SELECT id, session_id, event_type, source, activity, ' \n            'value_text, success, metadata_json, occurred_at ' \n            'FROM session_events ' \n            f'WHERE id IN ({placeholders}) ' \n            'ORDER BY id'
        )
        rows = connection.execute(sql, requested_ids).fetchall()
    finally:
        connection.close()

    by_id = {int(row['id']): row for row in rows}
    for event_id in requested_ids:
        row = by_id.get(event_id)
        if row is None:
            result['missing_ids'].append(event_id)
            continue
        if int(row['session_id']) != args.session_id:
            result['wrong_session'].append({
                'id': event_id,
                'actual_session_id': int(row['session_id']),
            })
        result['rows'].append({
            'id': int(row['id']),
            'session_id': int(row['session_id']),
            'event_type': row['event_type'],
            'source': row['source'],
            'activity': row['activity'],
            'value_text': row['value_text'],
            'success': None if row['success'] is None else bool(row['success']),
            'metadata_json': row['metadata_json'],
            'occurred_at': row['occurred_at'],
        })

    result['found_count'] = len(result['rows'])
    result['ok'] = not result['missing_ids'] and not result['wrong_session']
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
