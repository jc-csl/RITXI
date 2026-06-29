"""Ahootsa Ollama Local app for Reachy Mini Desktop. v0.3.6

This is intentionally separate from the official realtime conversation app.
It provides a local text-chat panel at http://127.0.0.1:7862 and calls Ollama
on http://127.0.0.1:11434/api/chat.

It does not implement realtime voice. The official conversation app remains
available through the entry point ``ahootsa_reachy_mini_conversation_app``.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
import threading
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# The Reachy Mini Desktop runner may launch local apps with its embedded
# CPython interpreter, where the reachy_mini package is not always importable.
# Ahootsa Ollama Local is only a text-chat panel and does not need robot APIs,
# so we provide a tiny fallback app base for that execution mode.
try:
    from reachy_mini import ReachyMini, ReachyMiniApp
except ModuleNotFoundError:  # pragma: no cover - used by Desktop embedded CPython
    class ReachyMini:  # type: ignore[no-redef]
        pass

    class ReachyMiniApp:  # type: ignore[no-redef]
        custom_app_url = "http://0.0.0.0:7862/"
        dont_start_webserver = True

        def wrapped_run(self) -> None:
            stop_event = threading.Event()
            self.run(None, stop_event)  # type: ignore[arg-type]

        def stop(self) -> None:
            pass


APP_NAME = "ahootsa_ollama_local_app"
DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "ahootsa-local:latest"
DEFAULT_UI_PORT = int(os.getenv("AHOOTSA_OLLAMA_UI_PORT", "7862"))
APP_VERSION = "0.3.6"
DEFAULT_SYSTEM_PROMPT = """Eres Ahootsa, un asistente robótico en español.

Hablas siempre en español claro.
Eres amable, paciente, positivo y breve.
Usas frases cortas.
Haces una sola pregunta cada vez.
Estás pensado para apoyar conversaciones con personas con discapacidad intelectual.
No inventes información.
Si no entiendes algo, pide una aclaración sencilla.
"""


_LOG_LOCK = threading.Lock()
_LOG_FILE: Path | None = None


def _default_log_dir() -> Path:
    base = os.getenv("LOCALAPPDATA")
    if base:
        return Path(base) / "Reachy Mini Control" / "ahootsa_logs"
    return Path.cwd() / "ahootsa_logs"


def _ensure_log_file() -> Path:
    global _LOG_FILE
    if _LOG_FILE is None:
        log_dir = Path(os.getenv("AHOOTSA_LOG_DIR", str(_default_log_dir())))
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        _LOG_FILE = log_dir / f"ahootsa_ollama_{timestamp}.log"
    return _LOG_FILE


def _log_step(step: str, **data: Any) -> None:
    """Write a timestamped diagnostic line for support/debugging."""
    try:
        payload = ""
        if data:
            safe = {k: str(v) for k, v in data.items()}
            payload = " | " + json.dumps(safe, ensure_ascii=False)
        line = f"{datetime.now().isoformat(timespec='seconds')} | {step}{payload}\n"
        with _LOG_LOCK:
            _ensure_log_file().open("a", encoding="utf-8").write(line)
    except Exception:
        # Logging must never break the app.
        pass


def _log_file_path() -> str:
    return str(_ensure_log_file())


HTML = r"""
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Ahootsa! Ollama Local Chat</title>
  <style>
    :root { color-scheme: light dark; font-family: system-ui, -apple-system, Segoe UI, sans-serif; }
    body { margin: 0; background: #f5f7fb; color: #172033; }
    header { display: flex; align-items: center; gap: 16px; padding: 18px 22px; background: #fff; box-shadow: 0 1px 10px #0001; }
    header img { width: 54px; height: 54px; object-fit: contain; border-radius: 14px; background: #eef5ff; padding: 4px; }
    h1 { margin: 0; font-size: 22px; }
    .sub { color: #667085; font-size: 14px; margin-top: 2px; }
    main { max-width: 980px; margin: 22px auto; padding: 0 16px; }
    .card { background: #fff; border-radius: 18px; box-shadow: 0 1px 16px #00000012; padding: 18px; margin-bottom: 16px; }
    .row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
    input, textarea, button { font: inherit; border-radius: 12px; border: 1px solid #d0d5dd; }
    input { padding: 10px 12px; min-width: 260px; flex: 1; }
    textarea { width: 100%; min-height: 74px; padding: 12px; box-sizing: border-box; resize: vertical; }
    button { padding: 10px 14px; background: #0b65c2; color: white; border: 0; cursor: pointer; }
    button.secondary { background: #344054; }
    button.light { background: #e7f0ff; color: #0b65c2; }
    button:disabled { opacity: .55; cursor: wait; }
    #chat { display: flex; flex-direction: column; gap: 10px; min-height: 320px; max-height: 54vh; overflow: auto; border: 1px solid #e5e7eb; border-radius: 16px; padding: 12px; background: #fafafa; }
    .msg { padding: 12px 14px; border-radius: 14px; line-height: 1.45; white-space: pre-wrap; }
    .chat-title { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 12px; }
    .chat-title h2 { margin: 0; font-size: 18px; }
    .user { align-self: flex-end; background: #dbeafe; max-width: 80%; }
    .assistant { align-self: flex-start; background: #eef2f6; max-width: 80%; }
    .system { align-self: center; background: #fff7d6; color: #574500; max-width: 90%; font-size: 14px; }
    .ok { color: #087443; font-weight: 600; }
    .bad { color: #b42318; font-weight: 600; }
    code { background: #eef2f6; padding: 2px 5px; border-radius: 6px; }
    @media (prefers-color-scheme: dark) {
      body { background: #111827; color: #f8fafc; }
      header, .card { background: #1f2937; }
      .sub { color: #cbd5e1; }
      input, textarea { background: #111827; color: #f8fafc; border-color: #475467; }
      .assistant { background: #374151; }
      .user { background: #1e3a8a; }
      .system { background: #4a3b0a; color: #fff3bf; }
      #chat { background: #111827; border-color: #374151; }
      code { background: #111827; }
    }
  </style>
</head>
<body>
<header>
  <img src="/logo.png" onerror="this.style.display='none'" alt="Ahootsa" />
  <div>
    <h1>Ahootsa! Ollama Local</h1>
    <div class="sub">IA local por texto usando Ollama. No usa la nube para el LLM.</div>
  </div>
</header>
<main>
  <section class="card">
    <div class="row">
      <strong>Estado:</strong> <span id="status">Comprobando Ollama...</span>
      <button class="light" onclick="checkStatus()">Comprobar</button>
      <button class="secondary" onclick="resetChat()">Reiniciar chat</button>
      <button class="secondary" onclick="window.open('/api/log','_blank')">Ver log</button>
    </div>
    <p class="sub">Ollama debe estar activo en <code id="baseUrl"></code> y el modelo debe existir: <code id="modelName"></code>.</p>
  </section>
  <section class="card">
    <div class="chat-title">
      <h2>Chat local con Ollama</h2>
      <span class="sub">Escribe abajo y pulsa Enviar</span>
    </div>
    <div id="chat"></div>
  </section>
  <section class="card">
    <label for="message"><strong>Mensaje</strong></label>
    <textarea id="message" placeholder="Escribe aquí tu mensaje para Ahootsa..."></textarea>
    <div class="row" style="margin-top: 10px; justify-content: flex-end;">
      <button onclick="sendMessage()" id="sendBtn">Enviar</button>
    </div>
  </section>
</main>
<script>
let busy = false;
const chat = document.getElementById('chat');
const message = document.getElementById('message');
const sendBtn = document.getElementById('sendBtn');
function addMsg(role, text) {
  const div = document.createElement('div');
  div.className = 'msg ' + role;
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}
async function checkStatus() {
  const st = document.getElementById('status');
  st.textContent = 'Comprobando...';
  try {
    const r = await fetch('/api/status');
    const j = await r.json();
    document.getElementById('baseUrl').textContent = j.base_url;
    document.getElementById('modelName').textContent = j.model;
    if (j.ok) st.innerHTML = '<span class="ok">Ollama OK</span>';
    else st.innerHTML = '<span class="bad">' + (j.error || 'Ollama no disponible') + '</span>';
  } catch (e) { st.innerHTML = '<span class="bad">No se pudo comprobar Ollama</span>'; }
}
async function sendMessage() {
  if (busy) return;
  const text = message.value.trim();
  if (!text) return;
  message.value = '';
  addMsg('user', text);
  busy = true; sendBtn.disabled = true; sendBtn.textContent = 'Pensando...';
  try {
    const r = await fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({message:text})});
    const j = await r.json();
    if (!r.ok || !j.ok) addMsg('system', (j.error || 'Error al llamar a Ollama') + (j.log_file ? '\nLog: ' + j.log_file : ''));
    else addMsg('assistant', j.reply);
  } catch (e) { addMsg('system', 'No se pudo conectar con Ahootsa/Ollama.'); }
  busy = false; sendBtn.disabled = false; sendBtn.textContent = 'Enviar';
}
async function resetChat() {
  await fetch('/api/reset', {method:'POST'});
  chat.innerHTML = '';
  addMsg('system', 'Chat reiniciado.');
}
message.addEventListener('keydown', (e) => { if (e.ctrlKey && e.key === 'Enter') sendMessage(); });
addMsg('system', 'Modo local de prueba. Para voz realtime usa la app Ahootsa clásica con Hugging Face Hosted.');
checkStatus();
</script>
</body>
</html>
"""


def _ollama_base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).rstrip("/")


def _ollama_model() -> str:
    return os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL).strip() or DEFAULT_OLLAMA_MODEL


def _model_aliases(model: str) -> list[str]:
    """Return acceptable Ollama names for a configured model.

    Ollama usually shows local models with an explicit tag, for example
    ``ahootsa-local:latest``. Users often configure the shorter name
    ``ahootsa-local``. We accept both.
    """
    model = model.strip()
    if not model:
        return []
    aliases = [model]
    if ":" not in model:
        aliases.append(f"{model}:latest")
    return aliases


def _resolve_model_name(available_models: list[str] | None = None) -> str:
    """Resolve configured model to the exact name exposed by Ollama."""
    configured = _ollama_model()
    if available_models:
        for alias in _model_aliases(configured):
            if alias in available_models:
                return alias
    return configured


def _system_prompt() -> str:
    return os.getenv("AHOOTSA_OLLAMA_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT).strip() or DEFAULT_SYSTEM_PROMPT


def _http_json(url: str, payload: dict[str, Any] | None = None, timeout: float = 120.0) -> dict[str, Any]:
    data = None
    headers = {"Content-Type": "application/json"}
    method = "GET"
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        method = "POST"
    _log_step("http.request", method=method, url=url, timeout=timeout, has_payload=payload is not None)
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
        _log_step("http.response", url=url, status=getattr(response, "status", "unknown"), bytes=len(raw))
        return json.loads(raw)


def _call_ollama_chat(messages: list[dict[str, str]]) -> str:
    resolved = _resolve_model_name()
    payload = {
        "model": resolved,
        "stream": False,
        "messages": messages,
        "options": {"temperature": 0.4, "num_ctx": 2048},
    }
    _log_step("ollama.chat.start", base_url=_ollama_base_url(), model=resolved, message_count=len(messages))
    started = time.perf_counter()
    result = _http_json(f"{_ollama_base_url()}/api/chat", payload, timeout=180.0)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    msg = result.get("message") or {}
    content = str(msg.get("content") or "").strip()
    _log_step("ollama.chat.done", elapsed_ms=elapsed_ms, reply_chars=len(content), done=result.get("done"), reason=result.get("done_reason"))
    return content


def create_app():
    from fastapi import Body, FastAPI, Query
    from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, PlainTextResponse

    _log_step(
        "app.create",
        version=APP_VERSION,
        python=sys.executable,
        cwd=os.getcwd(),
        module=__file__,
        base_url=_ollama_base_url(),
        model=_ollama_model(),
        ui_port=DEFAULT_UI_PORT,
        log_file=_log_file_path(),
    )

    app = FastAPI(title="Ahootsa Ollama Local", version=APP_VERSION)
    history: list[dict[str, str]] = [{"role": "system", "content": _system_prompt()}]

    @app.get("/", response_class=HTMLResponse)
    def index():
        return HTML

    @app.get("/logo.png")
    def logo():
        logo_path = Path(__file__).resolve().parent / "assets" / "ahootsa_logo.png"
        if logo_path.exists():
            return FileResponse(str(logo_path), media_type="image/png")
        return JSONResponse({"error": "logo not found"}, status_code=404)

    @app.get("/api/log")
    def api_log():
        path = _ensure_log_file()
        if not path.exists():
            return PlainTextResponse("", media_type="text/plain")
        return PlainTextResponse(path.read_text(encoding="utf-8", errors="replace"), media_type="text/plain")

    @app.get("/api/log-path")
    def api_log_path():
        return {"ok": True, "log_file": _log_file_path()}

    @app.get("/api/status")
    def status():
        _log_step("api.status.start")
        base_url = _ollama_base_url()
        model = _ollama_model()
        try:
            tags = _http_json(f"{base_url}/api/tags", timeout=5.0)
            models = [m.get("name") for m in tags.get("models", []) if m.get("name")]
            resolved_model = _resolve_model_name(models)
            model_ok = resolved_model in models
            return {
                "ok": model_ok,
                "base_url": base_url,
                "model": resolved_model,
                "configured_model": model,
                "available_models": models,
                "error": None if model_ok else f"Modelo no encontrado en Ollama: {model}. Disponibles: {', '.join(models) or 'ninguno'}",
            }
        except Exception as exc:
            return {"ok": False, "base_url": base_url, "model": model, "available_models": [], "error": str(exc)}

    @app.post("/api/reset")
    def reset():
        history.clear()
        history.append({"role": "system", "content": _system_prompt()})
        return {"ok": True}

    @app.post("/api/chat")
    async def chat_endpoint(payload: dict[str, Any] | None = Body(default=None), message: str | None = Query(default=None)):
        # v0.3.6: accept normal JSON body {"message":"..."} and also ?message=...
        # This avoids FastAPI treating a local Pydantic class as a required query field named "req".
        body_message = ""
        if isinstance(payload, dict):
            body_message = str(payload.get("message") or payload.get("text") or "")
        text = (message or body_message).strip()
        _log_step("api.chat.received", has_payload=isinstance(payload, dict), chars=len(text))
        if not text:
            _log_step("api.chat.empty")
            return JSONResponse({"ok": False, "error": "Mensaje vacío"}, status_code=400)
        history.append({"role": "user", "content": text})
        try:
            reply = _call_ollama_chat(history[-12:])
            if not reply:
                reply = "No he podido generar una respuesta. Prueba otra vez."
            history.append({"role": "assistant", "content": reply})
            _log_step("api.chat.success", reply_chars=len(reply), history_items=len(history))
            return {"ok": True, "reply": reply, "log_file": _log_file_path()}
        except urllib.error.URLError as exc:
            _log_step("api.chat.ollama_unreachable", error=exc)
            return JSONResponse({"ok": False, "error": f"Ollama no responde: {exc}", "log_file": _log_file_path()}, status_code=503)
        except Exception as exc:
            _log_step("api.chat.error", error=exc)
            return JSONResponse({"ok": False, "error": str(exc), "log_file": _log_file_path()}, status_code=500)

    return app


class AhootsaOllamaLocalApp(ReachyMiniApp):  # type: ignore[misc]
    """Local Ollama text-chat app for Reachy Mini Desktop."""

    custom_app_url = "http://0.0.0.0:7862/"
    # Important: prevent Reachy Mini base class from starting an empty default
    # webserver on 7862. This app starts its own FastAPI with /, /api/chat, etc.
    dont_start_webserver = True

    def run(self, reachy_mini: ReachyMini, stop_event: threading.Event) -> None:
        import uvicorn

        _log_step("app.run.start", port=DEFAULT_UI_PORT)
        app = create_app()
        server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=DEFAULT_UI_PORT, log_level="info"))
        thread = threading.Thread(target=server.run, daemon=True, name="ahootsa-ollama-ui")
        thread.start()
        try:
            while not stop_event.is_set():
                time.sleep(0.25)
        finally:
            _log_step("app.run.stop_requested")
            server.should_exit = True
            thread.join(timeout=5.0)
            _log_step("app.run.stopped")


if __name__ == "__main__":
    app = AhootsaOllamaLocalApp()
    try:
        app.wrapped_run()
    except KeyboardInterrupt:
        app.stop()
