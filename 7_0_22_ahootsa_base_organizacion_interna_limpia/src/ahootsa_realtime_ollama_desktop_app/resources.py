"""Resource path helpers for Ahootsa 7.0.22.

Tools loaded by Reachy Mini still live in ``tools/``. Static data, templates
and editable configuration are kept outside ``tools/`` so the external tools
folder contains only Python tools and small runtime helpers.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def package_root() -> Path:
    return Path(__file__).resolve().parent


def tool_dir() -> Path:
    return package_root() / "tools"


def data_path(*parts: str) -> Path:
    return package_root() / "data" / Path(*parts)


def config_path(*parts: str) -> Path:
    return package_root() / "config" / Path(*parts)


def template_path(*parts: str) -> Path:
    return package_root() / "templates" / Path(*parts)


def first_existing(*paths: Path) -> Path | None:
    for path in paths:
        try:
            if path.exists():
                return path
        except Exception:
            continue
    return None


def read_json(default: Any, *paths: Path) -> Any:
    path = first_existing(*paths)
    if not path:
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
