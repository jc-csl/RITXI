#!/usr/bin/env python
"""Copy the 16 selected Reachy Mini moves from the Phase 4 downloads into Ahootsa.

This is a one-time preparation utility. It does not launch the daemon or the
conversation app and it does not modify the official application source code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_ROOT = Path(
    r"D:\ritxi\AHOOTSA8\recursos_bailes\datasets_hf"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_catalog(activity_root: Path) -> dict[str, Any]:
    catalog_path = activity_root / "catalogo_bailes.json"
    try:
        return json.loads(catalog_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: no existe {catalog_path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: catálogo JSON no válido: {exc}") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Copia los 16 movimientos seleccionados desde los datasets "
            "descargados en la Fase 4 a la biblioteca local de Ahootsa."
        )
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=DEFAULT_SOURCE_ROOT,
        help=(
            "Carpeta que contiene pollen-robotics__..., "
            "Anne-Charlotte__... y apirrone__..."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Sustituye archivos locales que ya existan y sean diferentes.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    activity_root = Path(__file__).resolve().parent
    destination = activity_root / "dataset" / "data"
    source_root = args.source_root.expanduser().resolve()

    if not source_root.is_dir():
        print(f"ERROR: no existe la carpeta de origen:\n{source_root}")
        return 2

    catalog = load_catalog(activity_root)
    moves = catalog.get("moves", [])

    if len(moves) != 16:
        print(f"ERROR: se esperaban 16 movimientos y hay {len(moves)}.")
        return 3

    planned: list[tuple[dict[str, Any], Path, Path, Path, Path]] = []
    missing: list[Path] = []

    for move in moves:
        dataset_root = source_root / move["dataset_folder"]
        source_json = dataset_root / Path(move["source_json"])
        source_audio = dataset_root / Path(move["source_audio"])
        destination_json = activity_root / Path(move["local_json"])
        destination_audio = activity_root / Path(move["local_audio"])

        if not source_json.is_file():
            missing.append(source_json)
        if not source_audio.is_file():
            missing.append(source_audio)

        planned.append(
            (
                move,
                source_json,
                source_audio,
                destination_json,
                destination_audio,
            )
        )

    if missing:
        print("ERROR: faltan archivos de origen. No se ha copiado nada:")
        for path in missing:
            print(f"  - {path}")
        return 4

    destination.mkdir(parents=True, exist_ok=True)
    inventory: list[dict[str, Any]] = []

    for move, source_json, source_audio, destination_json, destination_audio in planned:
        for src, dst, kind in (
            (source_json, destination_json, "movement"),
            (source_audio, destination_audio, "audio"),
        ):
            dst.parent.mkdir(parents=True, exist_ok=True)

            if dst.exists():
                same = sha256_file(src) == sha256_file(dst)
                if same:
                    action = "already_present"
                elif args.force:
                    shutil.copy2(src, dst)
                    action = "replaced"
                else:
                    print(
                        "ERROR: existe un archivo local diferente:\n"
                        f"  {dst}\n"
                        "Ejecuta de nuevo con --force solo si deseas sustituirlo."
                    )
                    return 5
            else:
                shutil.copy2(src, dst)
                action = "copied"

            inventory.append(
                {
                    "move_id": move["id"],
                    "kind": kind,
                    "source_dataset": move["dataset_repo"],
                    "source_file": str(src),
                    "local_file": str(dst.relative_to(activity_root)),
                    "bytes": dst.stat().st_size,
                    "sha256": sha256_file(dst),
                    "action": action,
                }
            )

            print(
                f"{move['id']:<48} {kind:<8} "
                f"{action:<15} {dst.name}"
            )

    inventory_path = activity_root / "inventario_recursos_locales.json"
    inventory_document = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": str(source_root),
        "activity_root": str(activity_root),
        "move_count": len(moves),
        "file_count": len(inventory),
        "files": inventory,
    }
    inventory_path.write_text(
        json.dumps(inventory_document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print()
    print("PREPARACIÓN COMPLETADA")
    print(f"Movimientos: {len(moves)}")
    print(f"Archivos: {len(inventory)}")
    print(f"Destino: {destination}")
    print(f"Inventario: {inventory_path}")
    print()
    print(
        "La actividad ya contiene sus recursos locales y no necesita la "
        "caché de Hugging Face durante la ejecución."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
