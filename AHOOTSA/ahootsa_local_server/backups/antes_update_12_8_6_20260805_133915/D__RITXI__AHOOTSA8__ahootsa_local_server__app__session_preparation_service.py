from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models


SERVER_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = SERVER_ROOT / "config"
PANEL_CONFIG_PATH = CONFIG_DIR / "panel_config.json"
ACTIVITIES_DIR = CONFIG_DIR / "activities"

LEVELS = {"initial", "intermediate", "advanced"}
PROFILE_FILES = ("instructions.txt", "greeting.txt", "tools.txt", "voice.txt")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"No existe el archivo: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"JSON no válido en {path}: {exc}") from exc

    if not isinstance(value, dict):
        raise RuntimeError(f"El archivo debe contener un objeto JSON: {path}")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _parse_iso(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


class SessionPreparationService:
    """Prepara una sesión usando un único perfil externo fijo."""

    def load_config(self) -> dict[str, Any]:
        raw = _read_json(PANEL_CONFIG_PATH)

        def resolve_path(key: str) -> Path:
            configured = str(raw.get(key, "")).strip()
            if not configured:
                raise RuntimeError(f"Falta '{key}' en {PANEL_CONFIG_PATH}.")
            path = Path(configured)
            if not path.is_absolute():
                path = (SERVER_ROOT / path).resolve()
            return path

        return {
            "project_root": resolve_path("project_root"),
            "official_app_directory": resolve_path("official_app_directory"),
            "base_profile_directory": resolve_path("base_profile_directory"),
            "profile_template_directory": resolve_path("profile_template_directory"),
            "active_session_profile_directory": resolve_path(
                "active_session_profile_directory"
            ),
            "external_tools_directory": resolve_path("external_tools_directory"),
            "daemon_script": resolve_path("daemon_script"),
            "manual_app_script": resolve_path("manual_app_script"),
            "session_data_directory": resolve_path("session_data_directory"),
            "active_session_file": resolve_path("active_session_file"),
            "conversation_app_host": str(
                raw.get("conversation_app_host", "127.0.0.1")
            ),
            "conversation_app_port": int(raw.get("conversation_app_port", 7860)),
            "daemon_host": str(raw.get("daemon_host", "127.0.0.1")),
            "daemon_port": int(raw.get("daemon_port", 8000)),
            "server_url": str(raw.get("server_url", "http://127.0.0.1:8100")),
            "active_profile_name": str(
                raw.get("active_profile_name", "ahootsa_session")
            ),
        }

    def ensure_storage_structure(self) -> dict[str, Path]:
        config = self.load_config()
        paths = {
            "sessions": config["session_data_directory"],
            "active_profile": config["active_session_profile_directory"],
            "template_profile": config["profile_template_directory"],
        }
        paths["sessions"].mkdir(parents=True, exist_ok=True)
        paths["active_profile"].parent.mkdir(parents=True, exist_ok=True)
        paths["template_profile"].parent.mkdir(parents=True, exist_ok=True)
        return paths

    def list_activities(self) -> list[dict[str, Any]]:
        activities: list[dict[str, Any]] = []
        if not ACTIVITIES_DIR.exists():
            return activities
        for path in sorted(ACTIVITIES_DIR.glob("*.json")):
            activity = _read_json(path)
            activity["definition_file"] = str(path)
            activities.append(activity)
        return activities

    def get_activity(self, key: str) -> dict[str, Any]:
        for activity in self.list_activities():
            if activity.get("key") == key:
                return activity
        raise KeyError(key)

    @staticmethod
    def _profile_complete(path: Path) -> bool:
        return path.is_dir() and all((path / name).is_file() for name in PROFILE_FILES)

    def validate_configuration(self) -> dict[str, Any]:
        config = self.load_config()
        paths = self.ensure_storage_structure()
        checks = {
            "project_root": config["project_root"].exists(),
            "official_app_directory": config["official_app_directory"].exists(),
            "base_profile_directory": self._profile_complete(
                config["base_profile_directory"]
            ),
            "profile_template_directory": self._profile_complete(
                config["profile_template_directory"]
            ),
            "active_session_profile_directory": self._profile_complete(
                config["active_session_profile_directory"]
            ),
            "external_tools_directory": config["external_tools_directory"].exists(),
            "daemon_script": config["daemon_script"].exists(),
            "manual_app_script": config["manual_app_script"].exists(),
            "session_data_directory": paths["sessions"].exists(),
            "activities": len(self.list_activities()) > 0,
            "runtime_not_configured": "runtime" not in str(PANEL_CONFIG_PATH).lower()
            and "runtime_directory" not in _read_json(PANEL_CONFIG_PATH),
            "fixed_profile_name": config["active_profile_name"] == "ahootsa_session",
        }
        return {
            "ok": all(checks.values()),
            "checks": checks,
            "resolved_paths": {
                key: str(value)
                for key, value in config.items()
                if isinstance(value, Path)
            },
            "active_profile_name": config["active_profile_name"],
        }

    @staticmethod
    def service_reachable(host: str, port: int, timeout: float = 0.25) -> bool:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False

    def official_profile_status(self) -> dict[str, Any]:
        config = self.load_config()
        expected = config["active_profile_name"]
        url = (
            f"http://{config['conversation_app_host']}:"
            f"{config['conversation_app_port']}/api/v1/personalities"
        )
        if not self.service_reachable(
            config["conversation_app_host"], config["conversation_app_port"]
        ):
            return {
                "available": False,
                "expected": expected,
                "current": None,
                "startup": None,
                "matches": False,
            }

        try:
            with urlopen(url, timeout=2.0) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError, json.JSONDecodeError, OSError):
            return {
                "available": False,
                "expected": expected,
                "current": None,
                "startup": None,
                "matches": False,
            }

        current = payload.get("current") if isinstance(payload, dict) else None
        startup = payload.get("startup") if isinstance(payload, dict) else None
        return {
            "available": True,
            "expected": expected,
            "current": current,
            "startup": startup,
            "matches": current == expected,
        }

    def service_status(self) -> dict[str, Any]:
        config = self.load_config()
        profile = self.official_profile_status()
        return {
            "local_server": {
                "running": True,
                "url": config["server_url"],
            },
            "daemon": {
                "running": self.service_reachable(
                    config["daemon_host"], config["daemon_port"]
                ),
                "url": f"http://{config['daemon_host']}:{config['daemon_port']}",
            },
            "conversation_app": {
                "running": self.service_reachable(
                    config["conversation_app_host"],
                    config["conversation_app_port"],
                ),
                "url": (
                    f"http://{config['conversation_app_host']}:"
                    f"{config['conversation_app_port']}"
                ),
                "profile": profile,
            },
        }

    def session_paths(self, session_id: int) -> dict[str, Path]:
        config = self.load_config()
        session_dir = config["session_data_directory"] / f"session_{session_id:06d}"
        return {
            "session": session_dir,
            "context": session_dir / "session_context.json",
            "status": session_dir / "session_status.json",
            "snapshot": session_dir / "profile_snapshot",
            "log": session_dir / "conversation_app.log",
            "summary": session_dir / "summary.json",
        }

    def active_profile_is_prepared_for(self, session_id: int) -> bool:
        config = self.load_config()
        instructions = config["active_session_profile_directory"] / "instructions.txt"
        if not instructions.is_file():
            return False
        marker = f"Este bloque solo se aplica a la sesión {session_id}."
        try:
            return marker in instructions.read_text(encoding="utf-8")
        except OSError:
            return False

    def prepare_session(
        self,
        *,
        db: Session,
        user: models.User,
        activity_key: str,
        level: str,
        started_by: str,
    ) -> dict[str, Any]:
        if level not in LEVELS:
            raise ValueError(f"Nivel no válido: {level}")

        config = self.load_config()
        if self.service_reachable(
            config["conversation_app_host"], config["conversation_app_port"]
        ):
            raise RuntimeError(
                "La Conversation App está activa. Ciérrala antes de preparar "
                "otra sesión para que pueda cargar el nuevo contexto."
            )

        activity = self.get_activity(activity_key)
        levels = activity.get("levels")
        if not isinstance(levels, dict) or level not in levels:
            raise ValueError(
                f"La actividad '{activity_key}' no define el nivel '{level}'."
            )
        level_data = levels[level]
        if not isinstance(level_data, dict):
            raise ValueError("La definición del nivel no es válida.")

        active = db.scalar(
            select(models.SessionRecord).where(models.SessionRecord.status == "active")
        )
        if active is not None:
            raise RuntimeError(
                f"Ya existe una sesión activa (id={active.id}). Finalízala antes."
            )

        if user.profile is None:
            user.profile = models.UserProfile()
            db.flush()

        session = models.SessionRecord(
            user_id=user.id,
            started_by=started_by.strip() or "professional",
            status="active",
        )
        db.add(session)
        db.flush()

        paths = self.session_paths(session.id)
        profile_name = config["active_profile_name"]
        profile_dir = config["active_session_profile_directory"]

        try:
            if paths["session"].exists():
                shutil.rmtree(paths["session"])
            paths["session"].mkdir(parents=True, exist_ok=True)

            self._replace_profile(
                source=config["profile_template_directory"],
                destination=profile_dir,
            )

            preferred_name = user.preferred_name or user.name
            context = self._build_context(
                session=session,
                user=user,
                activity=activity,
                level=level,
                level_data=level_data,
                profile_name=profile_name,
                started_by=started_by,
            )

            instructions_path = profile_dir / "instructions.txt"
            base_instructions = instructions_path.read_text(encoding="utf-8")
            instructions_path.write_text(
                base_instructions.rstrip()
                + "\n\n"
                + self._build_instruction_block(context),
                encoding="utf-8",
            )

            greeting_path = profile_dir / "greeting.txt"
            greeting_template = str(
                level_data.get(
                    "greeting_template",
                    "Hola, {preferred_name}. Soy Aocha. Vamos a empezar.",
                )
            )
            greeting_path.write_text(
                greeting_template.format(preferred_name=preferred_name).strip() + "\n",
                encoding="utf-8",
            )

            self._copy_profile(profile_dir, paths["snapshot"])
            _write_json(paths["context"], context)
            _write_json(
                paths["status"],
                {
                    "session_id": session.id,
                    "status": "prepared",
                    "prepared_at": _utc_now_iso(),
                    "profile_name": profile_name,
                    "conversation_app_started": False,
                    "conversation_app_running": False,
                    "active_profile_directory": str(profile_dir),
                    "session_directory": str(paths["session"]),
                    "log_file": str(paths["log"]),
                },
            )
            _write_json(
                config["active_session_file"],
                {
                    "session_id": session.id,
                    "profile_name": profile_name,
                    "session_directory": str(paths["session"]),
                    "context_file": str(paths["context"]),
                    "log_file": str(paths["log"]),
                },
            )

            db.add_all(
                [
                    models.SessionEvent(
                        session_id=session.id,
                        event_type="session_started",
                        source="panel",
                        value_text=f"Sesión iniciada por {session.started_by}",
                        metadata_json=json.dumps(
                            {
                                "profile_name": profile_name,
                                "context_file": str(paths["context"]),
                            },
                            ensure_ascii=False,
                        ),
                    ),
                    models.SessionEvent(
                        session_id=session.id,
                        event_type="activity_started",
                        source="panel",
                        activity=activity_key,
                        value_text=str(activity.get("title", activity_key)),
                        metadata_json=json.dumps(
                            {
                                "level": level,
                                "level_title": level_data.get("title", level),
                                "mode": "professional_panel_mvp",
                            },
                            ensure_ascii=False,
                        ),
                    ),
                    models.SessionEvent(
                        session_id=session.id,
                        event_type="robot_message",
                        source="system",
                        activity=activity_key,
                        value_text=greeting_path.read_text(encoding="utf-8").strip(),
                        metadata_json=json.dumps(
                            {
                                "level": level,
                                "action": "session_greeting",
                                "generated_profile": profile_name,
                            },
                            ensure_ascii=False,
                        ),
                    ),
                ]
            )
            db.commit()
            db.refresh(session)
        except Exception:
            db.rollback()
            if paths["session"].exists():
                shutil.rmtree(paths["session"], ignore_errors=True)
            self.reset_active_profile()
            config["active_session_file"].unlink(missing_ok=True)
            raise

        return {
            "session_id": session.id,
            "session_status": session.status,
            "user_external_id": user.external_id,
            "preferred_name": preferred_name,
            "activity": activity_key,
            "activity_title": activity.get("title", activity_key),
            "level": level,
            "level_title": level_data.get("title", level),
            "profile_name": profile_name,
            "profile_directory": str(profile_dir),
            "session_directory": str(paths["session"]),
            "context_file": str(paths["context"]),
            "profile_snapshot": str(paths["snapshot"]),
            "log_file": str(paths["log"]),
            "greeting": greeting_path.read_text(encoding="utf-8").strip(),
        }

    @staticmethod
    def _copy_profile(source: Path, destination: Path) -> None:
        missing = [name for name in PROFILE_FILES if not (source / name).is_file()]
        if missing:
            raise RuntimeError(
                "Faltan archivos en el perfil: " + ", ".join(missing)
            )
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True, exist_ok=True)
        for name in PROFILE_FILES:
            shutil.copy2(source / name, destination / name)

    def _replace_profile(self, source: Path, destination: Path) -> None:
        self._copy_profile(source, destination)

    def reset_active_profile(self) -> None:
        config = self.load_config()
        self._replace_profile(
            source=config["profile_template_directory"],
            destination=config["active_session_profile_directory"],
        )

    @staticmethod
    def _build_context(
        *,
        session: models.SessionRecord,
        user: models.User,
        activity: dict[str, Any],
        level: str,
        level_data: dict[str, Any],
        profile_name: str,
        started_by: str,
    ) -> dict[str, Any]:
        profile = user.profile
        return {
            "context_version": "1.1",
            "generated_at": _utc_now_iso(),
            "session": {
                "id": session.id,
                "started_by": started_by.strip() or "professional",
                "status": "prepared",
                "profile_name": profile_name,
            },
            "user": {
                "external_id": user.external_id,
                "name": user.name,
                "preferred_name": user.preferred_name or user.name,
                "language": user.language,
                "notes": user.notes,
            },
            "profile": {
                "communication_style": profile.communication_style,
                "speech_speed": profile.speech_speed,
                "response_wait_seconds": profile.response_wait_seconds,
                "preferred_interaction_mode": profile.preferred_interaction_mode,
                "preferred_reinforcement": profile.preferred_reinforcement,
                "interests": profile.interests,
                "avoid_topics": profile.avoid_topics,
                "accessibility_notes": profile.accessibility_notes,
                "max_instructions_per_turn": profile.max_instructions_per_turn,
            },
            "activity": {
                "key": activity.get("key"),
                "title": activity.get("title"),
                "description": activity.get("description"),
                "level": level,
                "level_title": level_data.get("title", level),
                "objective": level_data.get("objective"),
                "max_options": level_data.get("max_options"),
                "rules": level_data.get("rules", []),
                "first_prompt": level_data.get("first_prompt"),
            },
            "professional_control": {
                "system_may_recommend_level": False,
                "professional_confirms_level_change": True,
                "evaluation_mode": "manual_quick_marks",
            },
        }

    @staticmethod
    def _build_instruction_block(context: dict[str, Any]) -> str:
        user = context["user"]
        profile = context["profile"]
        activity = context["activity"]
        rules = activity.get("rules") or []
        rules_text = "\n".join(f"- {rule}" for rule in rules)
        interests = profile.get("interests") or "No consta información adicional."
        avoid_topics = profile.get("avoid_topics") or "No consta información adicional."
        accessibility = (
            profile.get("accessibility_notes") or "No constan apoyos adicionales."
        )

        return f"""# CONTEXTO TEMPORAL DE SESIÓN — PRIORIDAD ALTA

Este bloque solo se aplica a la sesión {context['session']['id']}.
No lo conviertas en información permanente ni decidas cambios de nivel.

PERSONA USUARIA
- Nombre preferido: {user['preferred_name']}
- Idioma: {user['language']}
- Estilo comunicativo: {profile['communication_style']}
- Velocidad de habla recomendada: {profile['speech_speed']}
- Tiempo de espera antes de repetir: {profile['response_wait_seconds']} segundos
- Máximo de instrucciones por turno: {profile['max_instructions_per_turn']}
- Intereses conocidos: {interests}
- Temas que evitar: {avoid_topics}
- Apoyos y accesibilidad: {accessibility}

ACTIVIDAD ACTUAL
- Actividad: {activity['title']}
- Nivel: {activity['level_title']}
- Objetivo: {activity.get('objective') or 'Trabajar la comunicación de forma guiada.'}
- Máximo de opciones: {activity.get('max_options') or 'según el contexto'}

REGLAS DE ESTA ACTIVIDAD
{rules_text or '- Sigue las instrucciones generales del perfil Ahootsa.'}

INICIO DEL EJEMPLO
Empieza con esta propuesta, adaptándola de forma natural:
“{activity.get('first_prompt') or 'Vamos a empezar con una pregunta sencilla.'}”

CONTROL PROFESIONAL
- No evalúes clínicamente a la persona.
- No decidas subir o bajar de nivel.
- El profesional registrará las respuestas, las pistas y la decisión final.
- Mantén una actitud positiva, clara y respetuosa.
# FIN DEL CONTEXTO TEMPORAL DE SESIÓN
"""

    def mark_launch_requested(self, session_id: int) -> dict[str, Any]:
        paths = self.session_paths(session_id)
        if not paths["status"].is_file():
            raise RuntimeError("No existe session_status.json para la sesión.")
        status = _read_json(paths["status"])
        status.update(
            {
                "status": "launching",
                "conversation_app_started": True,
                "launch_requested_at": _utc_now_iso(),
            }
        )
        _write_json(paths["status"], status)
        return status

    def sync_running_status(self, session_id: int) -> dict[str, Any] | None:
        paths = self.session_paths(session_id)
        if not paths["status"].is_file():
            return None
        status = _read_json(paths["status"])
        config = self.load_config()
        running = self.service_reachable(
            config["conversation_app_host"], config["conversation_app_port"]
        )
        status["conversation_app_running"] = running

        if running and not status.get("running_at"):
            status["running_at"] = _utc_now_iso()
            status["status"] = "running"
        _write_json(paths["status"], status)
        return status

    def timing_summary(
        self,
        session_id: int,
        *,
        fallback_started_at: datetime,
        fallback_finished_at: datetime | None,
    ) -> dict[str, Any]:
        paths = self.session_paths(session_id)
        status = _read_json(paths["status"]) if paths["status"].is_file() else {}

        start = (
            _parse_iso(status.get("running_at"))
            or _parse_iso(status.get("prepared_at"))
            or fallback_started_at.replace(tzinfo=timezone.utc)
        )
        end = (
            _parse_iso(status.get("finished_at"))
            or (
                fallback_finished_at.replace(tzinfo=timezone.utc)
                if fallback_finished_at is not None
                else _utc_now()
            )
        )
        duration = max((end - start).total_seconds(), 0.0)
        source = "running" if status.get("running_at") else "prepared"
        return {
            "duration_seconds": round(duration, 1),
            "duration_minutes": round(duration / 60, 2),
            "duration_source": source,
            "prepared_at": status.get("prepared_at"),
            "running_at": status.get("running_at"),
            "finished_at": status.get("finished_at"),
            "conversation_app_running": bool(status.get("conversation_app_running")),
            "file_status": status.get("status"),
        }

    def finalize_session_files(
        self,
        session_id: int,
        *,
        finished_at: datetime,
        decision: str,
        summary: dict[str, Any],
    ) -> None:
        config = self.load_config()
        paths = self.session_paths(session_id)
        if paths["status"].is_file():
            status = _read_json(paths["status"])
        else:
            status = {"session_id": session_id}
        status.update(
            {
                "status": "finished",
                "finished_at": finished_at.replace(tzinfo=timezone.utc).isoformat(),
                "professional_decision": decision,
                "conversation_app_running": self.service_reachable(
                    config["conversation_app_host"],
                    config["conversation_app_port"],
                ),
            }
        )
        _write_json(paths["status"], status)
        _write_json(paths["summary"], summary)
        self.reset_active_profile()
        status["active_profile_reset"] = True
        status["profile_reset_at"] = _utc_now_iso()
        _write_json(paths["status"], status)
        config["active_session_file"].unlink(missing_ok=True)

    def launch_daemon(self) -> dict[str, Any]:
        config = self.load_config()
        if self.service_reachable(config["daemon_host"], config["daemon_port"]):
            return {
                "started": False,
                "already_running": True,
                "message": "El daemon ya responde en el puerto 8000.",
            }
        self._launch_powershell(config["daemon_script"], config["project_root"])
        return {
            "started": True,
            "already_running": False,
            "message": "Se ha abierto una consola para el daemon MuJoCo.",
        }

    def launch_conversation_app(self, session_id: int) -> dict[str, Any]:
        config = self.load_config()
        if not self.active_profile_is_prepared_for(session_id):
            raise RuntimeError(
                "El perfil ahootsa_session no contiene el contexto de esta sesión. "
                "Vuelve a preparar la sesión."
            )

        if self.service_reachable(
            config["conversation_app_host"], config["conversation_app_port"]
        ):
            profile = self.official_profile_status()
            message = (
                "La Conversation App ya está activa con el perfil correcto."
                if profile.get("matches")
                else "La Conversation App ya está activa con otro perfil. Ciérrala y vuelve a lanzarla."
            )
            return {
                "started": False,
                "already_running": True,
                "message": message,
                "profile": profile,
            }

        self.mark_launch_requested(session_id)
        self._launch_powershell(config["manual_app_script"], config["project_root"])
        return {
            "started": True,
            "already_running": False,
            "message": (
                "Se ha abierto una consola para la Conversation App. "
                "El perfil esperado es ahootsa_session."
            ),
            "launcher_script": str(config["manual_app_script"]),
            "expected_profile": config["active_profile_name"],
        }

    @staticmethod
    def _launch_powershell(script: Path, cwd: Path) -> None:
        if os.name != "nt":
            raise RuntimeError("El lanzamiento automático solo está disponible en Windows.")
        if not script.exists():
            raise RuntimeError(f"No existe el script de lanzamiento: {script}")

        creation_flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
        subprocess.Popen(
            [
                "powershell.exe",
                "-NoExit",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
            ],
            cwd=str(cwd),
            creationflags=creation_flags,
        )


session_preparation_service = SessionPreparationService()
