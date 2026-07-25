from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models


SERVER_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = SERVER_ROOT / "config"
PANEL_CONFIG_PATH = CONFIG_DIR / "panel_config.json"
ACTIVITIES_DIR = CONFIG_DIR / "activities"

LEVELS = {"initial", "intermediate", "advanced"}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"No existe el archivo de configuración: {path}") from exc
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


def _ps_quote(value: Path | str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


class SessionPreparationService:
    """Prepara sesiones personalizadas sin modificar la app oficial."""

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
            "external_tools_directory": resolve_path("external_tools_directory"),
            "daemon_script": resolve_path("daemon_script"),
            "manual_app_script": resolve_path("manual_app_script"),
            "runtime_directory": resolve_path("runtime_directory"),
            "conversation_app_host": str(raw.get("conversation_app_host", "127.0.0.1")),
            "conversation_app_port": int(raw.get("conversation_app_port", 7860)),
            "daemon_host": str(raw.get("daemon_host", "127.0.0.1")),
            "daemon_port": int(raw.get("daemon_port", 8000)),
            "server_url": str(raw.get("server_url", "http://127.0.0.1:8100")),
            "profile_prefix": str(raw.get("profile_prefix", "ahootsa_session")),
        }

    def ensure_runtime_structure(self) -> dict[str, Path]:
        config = self.load_config()
        runtime = config["runtime_directory"]
        paths = {
            "runtime": runtime,
            "sessions": runtime / "sessions",
            "generated_profiles": runtime / "generated_profiles",
            "imports": runtime / "imports",
            "exports": runtime / "exports",
        }
        for path in paths.values():
            path.mkdir(parents=True, exist_ok=True)
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

    def validate_configuration(self) -> dict[str, Any]:
        config = self.load_config()
        paths = self.ensure_runtime_structure()
        checks = {
            "project_root": config["project_root"].exists(),
            "official_app_directory": config["official_app_directory"].exists(),
            "base_profile_directory": config["base_profile_directory"].exists(),
            "external_tools_directory": config["external_tools_directory"].exists(),
            "daemon_script": config["daemon_script"].exists(),
            "manual_app_script": config["manual_app_script"].exists(),
            "runtime_directory": paths["runtime"].exists(),
            "activities": len(self.list_activities()) > 0,
        }
        return {
            "ok": all(checks.values()),
            "checks": checks,
            "resolved_paths": {
                key: str(value)
                for key, value in config.items()
                if isinstance(value, Path)
            },
        }

    @staticmethod
    def service_reachable(host: str, port: int, timeout: float = 0.25) -> bool:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False

    def service_status(self) -> dict[str, Any]:
        config = self.load_config()
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
            },
        }

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

        config = self.load_config()
        paths = self.ensure_runtime_structure()
        session_slug = f"session_{session.id:06d}"
        profile_name = f"{config['profile_prefix']}_{session.id:06d}"
        session_dir = paths["sessions"] / session_slug
        profile_dir = paths["generated_profiles"] / profile_name

        try:
            if session_dir.exists():
                shutil.rmtree(session_dir)
            if profile_dir.exists():
                shutil.rmtree(profile_dir)
            session_dir.mkdir(parents=True, exist_ok=True)
            profile_dir.mkdir(parents=True, exist_ok=True)

            self._copy_base_profile(config["base_profile_directory"], profile_dir)

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

            context_path = session_dir / "session_context.json"
            status_path = session_dir / "session_status.json"
            launcher_path = session_dir / "2_lanzar_app_ahootsa_sesion.ps1"

            _write_json(context_path, context)
            _write_json(
                status_path,
                {
                    "session_id": session.id,
                    "status": "prepared",
                    "prepared_at": _utc_now_iso(),
                    "profile_name": profile_name,
                    "conversation_app_started": False,
                },
            )
            launcher_path.write_text(
                self._build_launcher_script(
                    config=config,
                    profile_name=profile_name,
                    context_path=context_path,
                    session_id=session.id,
                ),
                encoding="utf-8-sig",
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
                                "context_file": str(context_path),
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
            if session_dir.exists():
                shutil.rmtree(session_dir, ignore_errors=True)
            if profile_dir.exists():
                shutil.rmtree(profile_dir, ignore_errors=True)
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
            "session_directory": str(session_dir),
            "context_file": str(context_path),
            "launcher_script": str(launcher_path),
            "greeting": greeting_path.read_text(encoding="utf-8").strip(),
        }

    @staticmethod
    def _copy_base_profile(base_profile: Path, destination: Path) -> None:
        required = ["instructions.txt", "greeting.txt", "tools.txt", "voice.txt"]
        missing = [name for name in required if not (base_profile / name).exists()]
        if missing:
            raise RuntimeError(
                "Faltan archivos en el perfil base Ahootsa: " + ", ".join(missing)
            )
        for name in required:
            shutil.copy2(base_profile / name, destination / name)

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
            "context_version": "1.0",
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

    @staticmethod
    def _build_launcher_script(
        *,
        config: dict[str, Any],
        profile_name: str,
        context_path: Path,
        session_id: int,
    ) -> str:
        app_root = config["official_app_directory"]
        generated_profiles = config["runtime_directory"] / "generated_profiles"
        tools = config["external_tools_directory"]
        server_url = config["server_url"]
        return f"""$ErrorActionPreference = 'Stop'
$projectRoot = {_ps_quote(config['project_root'])}
$appRoot = {_ps_quote(app_root)}

Set-Location $projectRoot

$env:REALTIME_TRANSCRIPTION_LANGUAGE = 'es'
$env:HF_REALTIME_CONNECTION_MODE = 'deployed'
$env:REACHY_MINI_CUSTOM_PROFILE = {_ps_quote(profile_name)}
$env:REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY = {_ps_quote(generated_profiles)}
$env:REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY = {_ps_quote(tools)}
$env:AUTOLOAD_EXTERNAL_TOOLS = 'false'
$env:AHOOTSA_SESSION_ID = '{session_id}'
$env:AHOOTSA_SESSION_CONTEXT_FILE = {_ps_quote(context_path)}
$env:AHOOTSA_LOCAL_SERVER_URL = {_ps_quote(server_url)}

$activate = Join-Path $appRoot '.venv\\Scripts\\Activate.ps1'
if (-not (Test-Path $activate)) {{
    Write-Host 'No se encuentra el entorno virtual de la app oficial:' -ForegroundColor Red
    Write-Host "  $activate"
    exit 1
}}

Set-Location $appRoot
& $activate

Write-Host ''
Write-Host 'Iniciando Reachy Mini Conversation App para Ahootsa' -ForegroundColor Cyan
Write-Host 'Sesión: {session_id}' -ForegroundColor Gray
Write-Host 'Perfil: {profile_name}' -ForegroundColor Gray
Write-Host 'Contexto: {context_path}' -ForegroundColor Gray
Write-Host ''

reachy-mini-conversation-app --ui
# Añadir --debug manualmente cuando sea necesario.
"""

    def launch_daemon(self) -> dict[str, Any]:
        config = self.load_config()
        if self.service_reachable(config["daemon_host"], config["daemon_port"]):
            return {"started": False, "already_running": True, "message": "El daemon ya responde en el puerto 8000."}
        self._launch_powershell(config["daemon_script"], config["project_root"])
        return {"started": True, "already_running": False, "message": "Se ha abierto una consola para el daemon MuJoCo."}

    def launch_conversation_app(self, session_id: int) -> dict[str, Any]:
        config = self.load_config()
        if self.service_reachable(
            config["conversation_app_host"], config["conversation_app_port"]
        ):
            return {
                "started": False,
                "already_running": True,
                "message": (
                    "La Conversation App ya está activa. Ciérrala antes para "
                    "cargar el perfil temporal de esta sesión."
                ),
            }
        paths = self.ensure_runtime_structure()
        launcher = (
            paths["sessions"]
            / f"session_{session_id:06d}"
            / "2_lanzar_app_ahootsa_sesion.ps1"
        )
        if not launcher.exists():
            raise RuntimeError(
                "No existe el lanzador de sesión. Prepara primero la sesión desde el panel."
            )
        self._launch_powershell(launcher, config["project_root"])
        status_path = launcher.parent / "session_status.json"
        status = _read_json(status_path)
        status["conversation_app_started"] = True
        status["launch_requested_at"] = _utc_now_iso()
        _write_json(status_path, status)
        return {
            "started": True,
            "already_running": False,
            "message": "Se ha abierto una consola para la Conversation App personalizada.",
            "launcher_script": str(launcher),
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
