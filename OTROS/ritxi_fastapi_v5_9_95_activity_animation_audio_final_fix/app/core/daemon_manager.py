from __future__ import annotations

import os
import shutil
import signal
import socket
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.logging import log_event

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = PROJECT_ROOT / "logs"
DAEMON_LOG = LOG_DIR / "reachy_daemon_current.log"


def _is_windows() -> bool:
    return os.name == "nt"


def _port_open(host: str = "127.0.0.1", port: int = 8000, timeout: float = 0.35) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _candidate_commands() -> list[list[str]]:
    cmds: list[list[str]] = []
    exe = shutil.which("reachy-mini-daemon")
    if exe:
        cmds.append([exe, "--sim"])

    venv_exe = PROJECT_ROOT / ".venv" / ("Scripts" if _is_windows() else "bin") / ("reachy-mini-daemon.exe" if _is_windows() else "reachy-mini-daemon")
    if venv_exe.exists():
        cmds.append([str(venv_exe), "--sim"])

    # Último recurso: módulo Python dentro del entorno actual.
    cmds.append([sys.executable, "-m", "reachy_mini.daemon.app.main", "--sim"])
    return cmds


@dataclass
class DaemonStatus:
    running: bool
    port: int
    host: str
    pid: int | None
    started_by_app: bool
    log_file: str
    last_lines: list[str]
    message: str


class ReachyDaemonManager:
    """Gestor ligero del daemon simulado de Reachy Mini.

    No incrusta la ventana nativa de MuJoCo dentro del navegador porque MuJoCo
    abre una ventana gráfica propia del sistema operativo. Lo que sí hace es
    arrancar el daemon, comprobar el puerto 8000 y volcar su salida de terminal
    en `logs/reachy_daemon_current.log`, que el panel muestra en tiempo real.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        self.host = host
        self.port = port
        self.process: subprocess.Popen[str] | None = None
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    def read_lines(self, limit: int = 120) -> list[str]:
        if not DAEMON_LOG.exists():
            return []
        try:
            lines = DAEMON_LOG.read_text(encoding="utf-8", errors="replace").splitlines()
            return lines[-limit:]
        except Exception as exc:  # noqa: BLE001
            return [f"[Ritxi] No se pudo leer log del daemon: {exc}"]

    def status(self, limit: int = 120) -> DaemonStatus:
        running = _port_open(self.host, self.port)
        pid = self.process.pid if self.process and self.process.poll() is None else None
        return DaemonStatus(
            running=running,
            port=self.port,
            host=self.host,
            pid=pid,
            started_by_app=pid is not None,
            log_file=str(DAEMON_LOG),
            last_lines=self.read_lines(limit),
            message="Daemon Reachy disponible" if running else "Daemon Reachy no disponible en puerto 8000",
        )

    def start(self) -> DaemonStatus:
        if _port_open(self.host, self.port):
            log_event("daemon_start_skipped", reason="already_running", port=self.port)
            return self.status()

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with DAEMON_LOG.open("a", encoding="utf-8", errors="replace") as fh:
            fh.write("\n" + "=" * 80 + "\n")
            fh.write("[Ritxi] Arrancando reachy-mini-daemon --sim desde el panel/script.\n")
            fh.write("=" * 80 + "\n")

        last_error: str | None = None
        for cmd in _candidate_commands():
            try:
                log_event("daemon_start_attempt", command=" ".join(cmd), log_file=str(DAEMON_LOG))
                log_handle = DAEMON_LOG.open("a", encoding="utf-8", errors="replace")
                kwargs: dict[str, Any] = {
                    "stdout": log_handle,
                    "stderr": subprocess.STDOUT,
                    "stdin": subprocess.DEVNULL,
                    "text": True,
                    "cwd": str(PROJECT_ROOT),
                }
                if _is_windows():
                    kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]
                else:
                    kwargs["start_new_session"] = True
                self.process = subprocess.Popen(cmd, **kwargs)  # noqa: S603
                log_event("daemon_process_started", pid=self.process.pid, command=" ".join(cmd))
                return self.status()
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                log_event("daemon_start_command_failed", command=" ".join(cmd), error=last_error)

        with DAEMON_LOG.open("a", encoding="utf-8", errors="replace") as fh:
            fh.write(f"[Ritxi] ERROR arrancando daemon: {last_error}\n")
        return self.status()

    def stop(self) -> DaemonStatus:
        if self.process and self.process.poll() is None:
            try:
                log_event("daemon_stop_requested", pid=self.process.pid)
                if _is_windows():
                    self.process.send_signal(signal.CTRL_BREAK_EVENT)  # type: ignore[attr-defined]
                else:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            except Exception as exc:  # noqa: BLE001
                log_event("daemon_stop_error", error=str(exc))
                try:
                    self.process.terminate()
                except Exception:
                    pass
        return self.status()
