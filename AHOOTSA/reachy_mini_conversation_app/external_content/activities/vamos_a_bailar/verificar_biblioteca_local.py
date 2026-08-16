#!/usr/bin/env python
"""Verify the local Ahootsa dance library created in Phase 5."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from local_recorded_moves import LocalRecordedMoves


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: no existe {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: JSON no válido en {path}: {exc}") from exc


def main() -> int:
    activity_root = Path(__file__).resolve().parent
    dataset_root = activity_root / "dataset"
    catalog = load_json(activity_root / "catalogo_bailes.json")
    moves = catalog.get("moves", [])

    errors: list[str] = []
    checks: list[dict[str, Any]] = []

    if len(moves) != 16:
        errors.append(f"El catálogo contiene {len(moves)} movimientos, no 16.")

    for move in moves:
        json_path = activity_root / Path(move["local_json"])
        audio_path = activity_root / Path(move["local_audio"])

        json_ok = json_path.is_file()
        audio_ok = audio_path.is_file()

        if not json_ok:
            errors.append(f"Falta movimiento: {json_path}")
        if not audio_ok:
            errors.append(f"Falta audio: {audio_path}")

        checks.append(
            {
                "id": move["id"],
                "json_ok": json_ok,
                "audio_ok": audio_ok,
                "json_bytes": json_path.stat().st_size if json_ok else 0,
                "audio_bytes": audio_path.stat().st_size if audio_ok else 0,
                "json_sha256": sha256_file(json_path) if json_ok else "",
                "audio_sha256": sha256_file(audio_path) if audio_ok else "",
            }
        )

    loaded_names: list[str] = []
    sdk_error = ""

    if not errors:
        try:
            library = LocalRecordedMoves(dataset_root)
            loaded_names = sorted(library.list_moves())
            loaded_set = set(loaded_names)

            for move in moves:
                move_id = move["id"]

                if move_id not in loaded_set:
                    errors.append(
                        f"La biblioteca local no ha registrado: {move_id}"
                    )
                    continue

                loaded_move = library.get(move_id)

                if not loaded_move.sound_path:
                    errors.append(
                        f"No se ha asociado audio a: {move_id}"
                    )

                # Force validation of the main RecordedMove fields.
                if loaded_move.duration <= 0:
                    errors.append(
                        f"Duración no válida para: {move_id}"
                    )

                if not loaded_move.timestamps:
                    errors.append(
                        f"Sin marcas de tiempo: {move_id}"
                    )

                if not loaded_move.trajectory:
                    errors.append(
                        f"Sin trayectoria: {move_id}"
                    )

        except Exception as exc:
            sdk_error = f"{type(exc).__name__}: {exc}"
            errors.append(
                f"Error al construir movimientos locales con el SDK: "
                f"{sdk_error}"
            )

    report = {
        "schema_version": 2,
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "activity_root": str(activity_root),
        "dataset_root": str(dataset_root),
        "loader": "LocalRecordedMoves + SDK RecordedMove",
        "catalog_move_count": len(moves),
        "sdk_loaded_move_count": len(loaded_names),
        "sdk_loaded_moves": loaded_names,
        "sdk_error": sdk_error,
        "checks": checks,
        "errors": errors,
        "status": "OK" if not errors else "ERROR",
    }

    report_path = activity_root / "verificacion_biblioteca_local.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print()
    print("VERIFICACIÓN DE LA BIBLIOTECA LOCAL")
    print("=" * 72)

    for check in checks:
        state = (
            "OK"
            if check["json_ok"] and check["audio_ok"]
            else "ERROR"
        )
        print(
            f"{check['id']:<48} {state:<6} "
            f"json={check['json_bytes']} "
            f"audio={check['audio_bytes']}"
        )

    print()
    print(f"Catálogo: {len(moves)} movimientos")
    print(f"SDK RecordedMove: {len(loaded_names)} movimientos construidos")
    print(f"Informe: {report_path}")

    if errors:
        print()
        print("ERRORES:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print()
    print("RESULTADO: OK")
    print(
        "Los 16 movimientos y sus audios están dentro de la aplicación "
        "y se construyen como objetos RecordedMove del SDK."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
