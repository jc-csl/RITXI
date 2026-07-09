"""Public route entrypoint for Ahootsa 7.0.23.

The implementation is kept under ``routes/`` so this file remains a stable
import target for ``main.py`` and earlier launchers.
"""
from __future__ import annotations

from ahootsa_realtime_ollama_desktop_app.routes.combined_routes import mount_ahootsa_routes

__all__ = ["mount_ahootsa_routes"]
