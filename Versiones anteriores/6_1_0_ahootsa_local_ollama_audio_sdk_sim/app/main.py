
from __future__ import annotations

import asyncio
import json
import os
import re
import time
import uuid
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

APP_VERSION = "6.1.0"
APP_NAME = "Ahootsa Local Fallback + SDK Sim"
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "ahootsa-local:latest")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
LOG_DIR = Path(os.environ.get("AHOOTSA_LOG_DIR", r"D:\RITXI\logs"))
MAX_HISTORY_TURNS = 10

ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "static"
DATA_DIR = ROOT / "data"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


REACHY_CONTROL_DIR = Path(os.environ.get("REACHY_MINI_CONTROL_DIR", str(Path.home() / "AppData" / "Local" / "Reachy Mini Control")))
REACHY_CONTROL_PYTHON = Path(os.environ.get("REACHY_MINI_CONTROL_PYTHON", str(REACHY_CONTROL_DIR / "apps_venv" / "Scripts" / "python.exe")))
SDK_COMMAND = ROOT / "app" / "sdk_command.py"


def run_sdk_command(command: str, timeout: int = 20) -> Dict[str, Any]:
    """Runs a short SDK command with the Python environment installed by Reachy Mini Control."""
    if not REACHY_CONTROL_PYTHON.exists():
        return {
            "ok": False,
            "command": command,
            "error": f"No existe Python de Reachy Mini Control: {REACHY_CONTROL_PYTHON}",
        }

    cmd = [str(REACHY_CONTROL_PYTHON), str(SDK_COMMAND), command]
    started = time.time()
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        elapsed = round(time.time() - started, 3)
        payload = {
            "ok": completed.returncode == 0,
            "command": command,
            "returncode": completed.returncode,
            "elapsed_sec": elapsed,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "python": str(REACHY_CONTROL_PYTHON),
        }
        try:
            parsed = json.loads(completed.stdout.strip().splitlines()[-1])
            if isinstance(parsed, dict):
                payload.update(parsed)
        except Exception:
            pass
        log_event("robot.sdk_command", **payload)
        return payload
    except subprocess.TimeoutExpired as exc:
        payload = {
            "ok": False,
            "command": command,
            "error": f"Timeout ejecutando SDK: {exc}",
            "python": str(REACHY_CONTROL_PYTHON),
        }
        log_event("robot.sdk_timeout", **payload)
        return payload
    except Exception as exc:
        payload = {
            "ok": False,
            "command": command,
            "error": str(exc),
            "python": str(REACHY_CONTROL_PYTHON),
        }
        log_event("robot.sdk_error", **payload)
        return payload


async def check_daemon_http() -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get("http://127.0.0.1:8000/api/daemon/status")
            r.raise_for_status()
            return {"ok": True, "url": "http://127.0.0.1:8000/api/daemon/status", "status": r.json()}
    except Exception as exc:
        return {"ok": False, "url": "http://127.0.0.1:8000/api/daemon/status", "error": str(exc)}

app = FastAPI(title=APP_NAME, version=APP_VERSION)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="milliseconds")


def log_event(event: str, **data: Any) -> None:
    payload = {
        "ts": now_iso(),
        "event": event,
        "version": APP_VERSION,
        **data,
    }
    try:
        path = LOG_DIR / f"ahootsa6_events_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


SYSTEM_PROMPT = """Eres Ahootsa, un asistente educativo local.
Hablas siempre en castellano.
Tu objetivo es ayudar a personas con discapacidad intelectual con lenguaje sencillo.
Responde con naturalidad y rapidez.
Usa 1 o 2 frases, salvo que pidan más detalle.
Haz solo una pregunta cada vez.
No digas que eres un modelo de lenguaje.
No inventes que usas Hugging Face. Estás funcionando en modo local con Ollama.
Refuerza positivamente: "Buen trabajo", "Vamos paso a paso", "Te escucho".
Si no entiendes algo, pide repetirlo de forma breve.
Para actividades, guía paso a paso y espera respuesta.
"""


COMMUNICATION_LEVELS = {
    "facil": {
        "label": "Iniciación",
        "description": "Frases cortas, vocabulario sencillo y una instrucción cada vez.",
        "activities": [
            {
                "id": "oral_acciones_facil",
                "title": "Expresión oral: acciones sencillas",
                "steps": [
                    "Di en voz alta una acción que hagas por la mañana.",
                    "Muy bien. Ahora di una acción que haces en clase.",
                    "Perfecto. Di una frase con la palabra ayudar.",
                ],
            },
            {
                "id": "grafica_pictos_facil",
                "title": "Expresión gráfica: interpretar pictogramas",
                "steps": [
                    "Imagina un pictograma de una persona comiendo. ¿Qué acción representa?",
                    "Ahora imagina una persona leyendo. ¿Qué acción representa?",
                    "Muy bien. Dime una acción que pueda dibujarse fácil.",
                ],
            },
        ],
    },
    "normal": {
        "label": "Avanzado",
        "description": "Frases completas, pequeñas explicaciones y relación imagen-acción.",
        "activities": [
            {
                "id": "oral_describir_normal",
                "title": "Expresión oral: describir una situación",
                "steps": [
                    "Describe con una frase qué haces cuando llegas a clase.",
                    "Ahora añade un detalle: ¿con quién estás?",
                    "Muy bien. Resume la situación en una frase corta.",
                ],
            },
            {
                "id": "escrita_frase_normal",
                "title": "Expresión escrita: ordenar una frase",
                "steps": [
                    "Ordena mentalmente estas palabras: yo / ayuda / pido.",
                    "Ahora di una frase con: compañero, tarea y terminar.",
                    "Muy bien. ¿Qué palabra indica la acción?",
                ],
            },
        ],
    },
    "avanzada": {
        "label": "Experto",
        "description": "Explicación breve, elección de vocabulario y justificación.",
        "activities": [
            {
                "id": "oral_opinion_avanzada",
                "title": "Expresión oral: dar opinión",
                "steps": [
                    "Dime una actividad que te guste y explica por qué.",
                    "Ahora dime una actividad difícil y qué ayuda necesitarías.",
                    "Muy bien. Termina con una frase de conclusión.",
                ],
            },
            {
                "id": "grafica_secuencia_avanzada",
                "title": "Expresión gráfica: secuencia de acciones",
                "steps": [
                    "Imagina tres pictogramas: entrar, saludar y sentarse. Ordénalos.",
                    "Ahora explica por qué ese orden tiene sentido.",
                    "Perfecto. Crea otra secuencia de tres acciones.",
                ],
            },
        ],
    },
}


MEMORY_GAMES = {
    "animales": ["perro", "gato", "oso", "pez", "perro", "gato", "oso", "pez"],
    "acciones": ["leer", "comer", "correr", "dormir", "leer", "comer", "correr", "dormir"],
}


@dataclass
class SessionState:
    session_id: str
    history: List[Dict[str, str]] = field(default_factory=list)
    active_activity: Optional[Dict[str, Any]] = None
    active_step: int = 0
    memory_game: Optional[Dict[str, Any]] = None
    created_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)


sessions: Dict[str, SessionState] = {}


def get_session(session_id: Optional[str]) -> SessionState:
    if not session_id:
        session_id = str(uuid.uuid4())
    if session_id not in sessions:
        sessions[session_id] = SessionState(session_id=session_id)
        log_event("session.created", session_id=session_id)
    sessions[session_id].last_seen = time.time()
    return sessions[session_id]


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    mode: str = "auto"


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    source: str
    speak: bool = True
    activity: Optional[Dict[str, Any]] = None


class ActivityStartRequest(BaseModel):
    level: str
    activity_id: Optional[str] = None
    session_id: Optional[str] = None


class MemoryStartRequest(BaseModel):
    game: str = "animales"
    session_id: Optional[str] = None


class MemoryPickRequest(BaseModel):
    first: int
    second: int
    session_id: Optional[str] = None


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    return text


def level_from_text(text: str) -> Optional[str]:
    t = normalize(text)
    if any(w in t for w in ["iniciacion", "facil", "sencillo", "basico", "nivel 1"]):
        return "facil"
    if any(w in t for w in ["avanzado", "normal", "medio", "nivel 2"]):
        return "normal"
    if any(w in t for w in ["experto", "dificil", "alto", "nivel 3"]):
        return "avanzada"
    return None


def wants_activity(text: str) -> bool:
    t = normalize(text)
    return any(w in t for w in ["actividad", "actividades", "comunicacion", "expresion", "pictograma", "oral", "escrita", "grafica"])


def wants_memory(text: str) -> bool:
    t = normalize(text)
    return any(w in t for w in ["memory", "memoria", "parejas", "cartas", "juego"])


def wants_ollama(text: str) -> bool:
    t = normalize(text)
    return any(w in t for w in ["ollama", "ia local", "modelo local", "pregunta al modelo"])


def direct_rule_response(text: str, session: SessionState) -> Optional[str]:
    t = normalize(text)

    if re.search(r"\b(hola|buenas|kaixo)\b", t):
        return "¡Hola! Soy Ahootsa. Te escucho. ¿Qué quieres hacer?"

    if "que sabes hacer" in t or "qué sabes hacer" in text.lower():
        return "Puedo conversar, guiar actividades de comunicación y hacer un juego de memoria. ¿Qué prefieres?"

    if "como estas" in t or "cómo estás" in text.lower():
        return "Estoy lista para ayudarte. ¿Quieres hablar o hacer una actividad?"

    if wants_memory(text):
        return "Podemos jugar a Memory con cartas. Pulsa el botón Memory o dime: empezar juego de animales."

    level = level_from_text(text)
    if wants_activity(text) and not level:
        return "Podemos trabajar comunicación. Elige nivel: iniciación, avanzado o experto."

    if level:
        info = COMMUNICATION_LEVELS[level]
        acts = info["activities"]
        titles = "; ".join(a["title"] for a in acts)
        return f"Nivel {info['label']}. Puedes hacer: {titles}. ¿Cuál quieres empezar?"

    if session.active_activity:
        return next_activity_step(session, user_answer=text)

    return None


def start_activity(session: SessionState, level: str, activity_id: Optional[str] = None) -> str:
    level = level_from_text(level) or normalize(level)
    if level not in COMMUNICATION_LEVELS:
        return "No encuentro ese nivel. Elige iniciación, avanzado o experto."

    activities = COMMUNICATION_LEVELS[level]["activities"]
    selected = activities[0]
    if activity_id:
        selected = next((a for a in activities if a["id"] == activity_id), activities[0])

    session.active_activity = {
        "level": level,
        "activity": selected,
    }
    session.active_step = 0
    log_event("activity.started", session_id=session.session_id, level=level, activity_id=selected["id"])
    return f"Empezamos: {selected['title']}. {selected['steps'][0]}"


def next_activity_step(session: SessionState, user_answer: str = "") -> str:
    if not session.active_activity:
        return "No hay actividad iniciada."
    activity = session.active_activity["activity"]
    steps = activity["steps"]
    if user_answer:
        prefix = "Bien. "
    else:
        prefix = ""
    session.active_step += 1
    if session.active_step >= len(steps):
        title = activity["title"]
        session.active_activity = None
        session.active_step = 0
        return f"Buen trabajo. Hemos terminado {title}. ¿Quieres otra actividad?"
    return prefix + steps[session.active_step]


async def ask_ollama(message: str, session: SessionState) -> str:
    history = session.history[-MAX_HISTORY_TURNS:]
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.4,
            "num_predict": 140,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()
            content = data.get("message", {}).get("content", "").strip()
            if not content:
                raise RuntimeError("Ollama ha respondido vacío.")
            return content
    except Exception as exc:
        log_event("ollama.error", session_id=session.session_id, error=str(exc))
        return "Ahora no puedo conectar con Ollama local. Revisa que Ollama esté abierto y que exista el modelo ahootsa-local:latest."


async def check_ollama() -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            r.raise_for_status()
            data = r.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            return {
                "ok": True,
                "base_url": OLLAMA_BASE_URL,
                "model": DEFAULT_MODEL,
                "model_available": DEFAULT_MODEL in models,
                "models": models,
            }
    except Exception as exc:
        return {
            "ok": False,
            "base_url": OLLAMA_BASE_URL,
            "model": DEFAULT_MODEL,
            "model_available": False,
            "error": str(exc),
            "models": [],
        }


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/favicon.ico")
async def favicon() -> FileResponse:
    path = STATIC_DIR / "favicon.svg"
    if path.exists():
        return FileResponse(path)
    raise HTTPException(status_code=404)


@app.get("/api/status")
async def status() -> Dict[str, Any]:
    ollama = await check_ollama()
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "mode": "local_fallback_ollama_audio_sdk_sim",
        "huggingface_used": False,
        "reachy_sdk_python": str(REACHY_CONTROL_PYTHON),
        "reachy_sdk_python_exists": REACHY_CONTROL_PYTHON.exists(),
        "ollama": ollama,
        "log_dir": str(LOG_DIR),
        "sessions": len(sessions),
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    session = get_session(req.session_id)
    msg = req.message.strip()
    log_event("chat.user", session_id=session.session_id, message=msg, mode=req.mode)

    rule = direct_rule_response(msg, session)
    if rule and not wants_ollama(msg):
        reply = rule
        source = "local_rules"
    else:
        reply = await ask_ollama(msg, session)
        source = "ollama"

    session.history.append({"role": "user", "content": msg})
    session.history.append({"role": "assistant", "content": reply})
    session.history = session.history[-MAX_HISTORY_TURNS * 2 :]

    log_event("chat.assistant", session_id=session.session_id, reply=reply, source=source)
    return ChatResponse(session_id=session.session_id, reply=reply, source=source)


@app.get("/api/activities/levels")
async def activity_levels() -> Dict[str, Any]:
    return {"levels": COMMUNICATION_LEVELS}


@app.post("/api/activities/start", response_model=ChatResponse)
async def api_start_activity(req: ActivityStartRequest) -> ChatResponse:
    session = get_session(req.session_id)
    reply = start_activity(session, req.level, req.activity_id)
    return ChatResponse(session_id=session.session_id, reply=reply, source="activity")


@app.post("/api/activities/next", response_model=ChatResponse)
async def api_next_activity(req: ChatRequest) -> ChatResponse:
    session = get_session(req.session_id)
    reply = next_activity_step(session, req.message)
    return ChatResponse(session_id=session.session_id, reply=reply, source="activity")


@app.post("/api/memory/start", response_model=ChatResponse)
async def memory_start(req: MemoryStartRequest) -> ChatResponse:
    session = get_session(req.session_id)
    cards = MEMORY_GAMES.get(req.game, MEMORY_GAMES["animales"])[:]
    # fixed layout intentionally, easy for demo
    session.memory_game = {
        "game": req.game,
        "cards": cards,
        "found": [],
        "attempts": 0,
    }
    log_event("memory.started", session_id=session.session_id, game=req.game)
    return ChatResponse(
        session_id=session.session_id,
        reply="Juego Memory iniciado. Elige dos cartas por número, por ejemplo: 1 y 4.",
        source="memory",
        activity={"cards_count": len(cards), "found": []},
    )


@app.post("/api/memory/pick", response_model=ChatResponse)
async def memory_pick(req: MemoryPickRequest) -> ChatResponse:
    session = get_session(req.session_id)
    if not session.memory_game:
        return ChatResponse(session_id=session.session_id, reply="Primero inicia un juego Memory.", source="memory")

    game = session.memory_game
    cards = game["cards"]
    i, j = req.first - 1, req.second - 1
    if i == j or i < 0 or j < 0 or i >= len(cards) or j >= len(cards):
        reply = "Elige dos cartas distintas entre 1 y 8."
    else:
        game["attempts"] += 1
        a, b = cards[i], cards[j]
        if a == b:
            pair = sorted([req.first, req.second])
            if pair not in game["found"]:
                game["found"].append(pair)
            reply = f"¡Pareja encontrada! Las dos cartas son {a}."
        else:
            reply = f"No son pareja: {a} y {b}. Prueba otra vez."

        if len(game["found"]) == 4:
            attempts = game["attempts"]
            session.memory_game = None
            reply += f" Has terminado el juego en {attempts} intentos. Buen trabajo."

    return ChatResponse(
        session_id=session.session_id,
        reply=reply,
        source="memory",
        activity=game if session.memory_game else None,
    )



@app.get("/api/robot/status")
async def robot_status() -> Dict[str, Any]:
    daemon = await check_daemon_http()
    return {
        "ok": daemon.get("ok", False),
        "mode": "sdk_sim",
        "daemon": daemon,
        "sdk_python": str(REACHY_CONTROL_PYTHON),
        "sdk_python_exists": REACHY_CONTROL_PYTHON.exists(),
    }


@app.post("/api/robot/probe")
async def robot_probe() -> Dict[str, Any]:
    return run_sdk_command("probe", timeout=20)


@app.post("/api/robot/action/{action_name}")
async def robot_action(action_name: str) -> Dict[str, Any]:
    allowed = {"saludo", "wiggle", "nod", "look_left_right", "reset"}
    if action_name not in allowed:
        raise HTTPException(status_code=400, detail=f"Accion no permitida. Usa una de: {sorted(allowed)}")
    return run_sdk_command(action_name, timeout=30)


@app.post("/api/session/reset")
async def reset_session(req: Request) -> Dict[str, Any]:
    data = await req.json()
    sid = data.get("session_id")
    if sid and sid in sessions:
        del sessions[sid]
    return {"ok": True}
