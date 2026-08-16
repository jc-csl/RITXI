from __future__ import annotations

import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .session_preparation_service import session_preparation_service


SERVER_ROOT = Path(__file__).resolve().parent.parent


def _decode_process_output(raw: bytes | None) -> str:
    if not raw:
        return ""

    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue

    return raw.decode("utf-8", errors="replace")


class PanelSessionCompletionService:
    """Stops the official app and generates the final report from the panel."""

    @staticmethod
    def _port_open(host: str, port: int, timeout: float = 0.4) -> bool:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False

    def _wait_port_closed(
        self,
        host: str,
        port: int,
        timeout_seconds: float,
    ) -> bool:
        deadline = time.monotonic() + timeout_seconds

        while time.monotonic() < deadline:
            if not self._port_open(host, port):
                return True
            time.sleep(0.5)

        return not self._port_open(host, port)

    @staticmethod
    def _request_daemon_stop(host: str, port: int) -> str | None:
        request = Request(
            url=f"http://{host}:{port}/api/apps/stop-current-app",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=12) as response:
                response.read()
            return None
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            return str(exc)

    @staticmethod
    def _quote_powershell(value: Path | str) -> str:
        return str(value).replace("'", "''")

    def _force_stop_windows(
        self,
        *,
        project_root: Path,
        port: int,
    ) -> str | None:
        if os.name != "nt":
            return "La parada forzada solo está disponible en Windows."

        utility = project_root / "scripts" / "ahootsa_process_utils.ps1"

        if not utility.is_file():
            return f"No existe la utilidad de procesos: {utility}"

        command = (
            f". '{self._quote_powershell(utility)}'; "
            f"Stop-AhootsaPortProcess -Port {port} "
            "-ServiceName 'Reachy Mini Conversation App' | Out-Null"
        )

        completed = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                command,
            ],
            cwd=str(project_root),
            capture_output=True,
            check=False,
            timeout=30,
        )

        if completed.returncode == 0:
            return None

        message = _decode_process_output(
            completed.stderr or completed.stdout
        ).strip()
        return message or f"PowerShell devolvió {completed.returncode}."

    def stop_conversation_app(self) -> dict[str, Any]:
        config = session_preparation_service.load_config()
        app_host = config["conversation_app_host"]
        app_port = config["conversation_app_port"]
        daemon_host = config["daemon_host"]
        daemon_port = config["daemon_port"]

        if not self._port_open(app_host, app_port):
            return {
                "was_running": False,
                "stopped": True,
                "method": "already_stopped",
                "warnings": [],
            }

        warnings: list[str] = []
        daemon_warning = self._request_daemon_stop(
            daemon_host,
            daemon_port,
        )

        if daemon_warning:
            warnings.append(
                "El daemon no confirmó la parada: " + daemon_warning
            )

        if self._wait_port_closed(app_host, app_port, 18):
            return {
                "was_running": True,
                "stopped": True,
                "method": "daemon",
                "warnings": warnings,
            }

        force_warning = self._force_stop_windows(
            project_root=config["project_root"],
            port=app_port,
        )

        if force_warning:
            warnings.append(
                "La parada forzada informó: " + force_warning
            )

        stopped = self._wait_port_closed(app_host, app_port, 12)

        return {
            "was_running": True,
            "stopped": stopped,
            "method": "powershell" if stopped else "failed",
            "warnings": warnings,
        }

    @staticmethod
    def marker_path(session_id: int) -> Path:
        paths = session_preparation_service.session_paths(session_id)
        return paths["session"] / "panel_finish_requested.flag"

    def create_panel_marker(self, session_id: int) -> Path:
        marker = self.marker_path(session_id)
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(
            "El panel profesional completará la sesión y generará el informe.\n",
            encoding="utf-8",
        )
        return marker

    def remove_panel_marker(self, session_id: int) -> None:
        self.marker_path(session_id).unlink(missing_ok=True)

    @staticmethod
    def wait_for_log_stable(
        log_path: Path,
        *,
        timeout_seconds: float = 15.0,
    ) -> dict[str, Any]:
        deadline = time.monotonic() + timeout_seconds
        previous_signature: tuple[int, int] | None = None
        stable_checks = 0

        while time.monotonic() < deadline:
            try:
                stat = log_path.stat()
                signature = (stat.st_size, stat.st_mtime_ns)
            except FileNotFoundError:
                signature = None

            if signature is not None and signature == previous_signature:
                stable_checks += 1
            else:
                stable_checks = 0
                previous_signature = signature

            if signature is not None and stable_checks >= 3:
                return {
                    "exists": True,
                    "stable": True,
                    "size": signature[0],
                }

            time.sleep(0.75)

        if log_path.is_file():
            return {
                "exists": True,
                "stable": False,
                "size": log_path.stat().st_size,
            }

        return {
            "exists": False,
            "stable": False,
            "size": 0,
        }

    def generate_report(self, session_id: int) -> dict[str, Any]:
        config = session_preparation_service.load_config()
        paths = session_preparation_service.session_paths(session_id)
        report_tool = SERVER_ROOT / "tools" / "ahootsa_session_report.py"

        report_paths = {
            "pdf": paths["session"] / "informe_sesion.pdf",
            "html": paths["session"] / "informe_sesion.html",
            "json": paths["session"] / "informe_sesion.json",
            "transcript": paths["session"] / "transcripcion_sesion.txt",
        }

        if not report_tool.is_file():
            return {
                "generated": False,
                "error": f"No existe el generador: {report_tool}",
                "paths": {
                    key: str(value)
                    for key, value in report_paths.items()
                },
            }

        command = [
            sys.executable,
            str(report_tool),
            "--session-id",
            str(session_id),
            "--server-url",
            config["server_url"],
            "--log",
            str(paths["log"]),
            "--session-dir",
            str(paths["session"]),
        ]

        try:
            completed = subprocess.run(
                command,
                cwd=str(SERVER_ROOT),
                capture_output=True,
                check=False,
                timeout=180,
            )
        except subprocess.TimeoutExpired:
            return {
                "generated": False,
                "error": "La generación del informe superó 180 segundos.",
                "paths": {
                    key: str(value)
                    for key, value in report_paths.items()
                },
            }

        stdout = _decode_process_output(completed.stdout).strip()
        stderr = _decode_process_output(completed.stderr).strip()
        existing = {
            key: value.is_file()
            for key, value in report_paths.items()
        }

        return {
            "generated": completed.returncode == 0 and all(existing.values()),
            "return_code": completed.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "files": existing,
            "paths": {
                key: str(value)
                for key, value in report_paths.items()
            },
            "urls": {
                key: f"/panel/api/sessions/{session_id}/report/{key}"
                for key in report_paths
            },
        }


panel_session_completion_service = PanelSessionCompletionService()
