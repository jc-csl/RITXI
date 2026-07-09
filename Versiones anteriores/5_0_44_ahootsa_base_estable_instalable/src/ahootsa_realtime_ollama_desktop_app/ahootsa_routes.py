# Rutas HTML/API propias de Ahootsa. No sustituyen la conversación oficial Hugging Face.
from __future__ import annotations

import base64
import json
import os
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse

VERSION = "5.0.44"


def _log_root() -> Path:
    d = Path(os.getenv("AHOOTSA_LOG_DIR", r"D:\RITXI\logs"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _ollama_base() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")


def _ollama_model() -> str:
    return os.getenv("OLLAMA_MODEL", "llama3.2:3b").strip() or "llama3.2:3b"


def _http_json(url: str, payload: dict[str, Any] | None = None, timeout: float = 20.0) -> dict[str, Any]:
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if payload is not None else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8")
    return json.loads(raw) if raw else {}


def _html() -> str:
    model = _ollama_model()
    base = _ollama_base()
    return f"""<!doctype html>
<html lang='es'><head><meta charset='utf-8'/><meta name='viewport' content='width=device-width, initial-scale=1'/><title>Ahootsa 5.0.44</title>
<style>
body{{margin:0;font-family:Arial,sans-serif;background:#f6f7fb;color:#17213a}}.header{{display:flex;align-items:center;gap:16px;padding:12px 16px;background:#17213a;color:white}}.header b{{color:#ff2fa6}}.layout{{display:grid;grid-template-columns:minmax(0,1fr) 390px;height:calc(100vh - 56px)}}iframe{{width:100%;height:100%;border:0;background:white}}.panel{{border-left:1px solid #d6d9e6;background:white;padding:14px;overflow:auto}}.card{{border:1px solid #d6d9e6;border-radius:14px;padding:12px;margin-bottom:12px;background:#fff;box-shadow:0 1px 6px rgba(0,0,0,.05)}}button{{border:0;border-radius:10px;padding:10px 12px;background:#17213a;color:white;cursor:pointer;margin:4px 4px 4px 0}}button.secondary{{background:#ff2fa6}}textarea{{width:100%;box-sizing:border-box;min-height:96px;border:1px solid #c9ccda;border-radius:10px;padding:10px}}pre{{white-space:pre-wrap;background:#f1f3f8;padding:10px;border-radius:10px;max-height:260px;overflow:auto}}.small{{font-size:12px;color:#5d667c}}a{{color:#ff2fa6}}
</style></head><body>
<div class='header'><strong>Ahootsa <b>5.0.44</b></strong><span>Motor principal: Hugging Face Realtime oficial · Ollama auxiliar: {model}</span></div>
<div class='layout'><iframe src='/' title='Conversación principal Reachy/Ahootsa'></iframe><aside class='panel'>
<div class='card'><h3>Estado</h3><div class='small'>HF principal: <b id='hf'>comprobando...</b></div><div class='small'>Ollama: <b id='ol'>comprobando...</b></div><div class='small'>Modelo Ollama: <code>{model}</code></div><div class='small'>Base Ollama: <code>{base}</code></div><button onclick='status()'>Actualizar estado</button></div>
<div class='card'><h3>Preguntar a Ollama local</h3><p class='small'>Consulta directa por texto. No pasa por el motor principal Hugging Face.</p><textarea id='prompt' placeholder='Escribe una pregunta para llama3.2:3b...'></textarea><button class='secondary' onclick='ask()'>Preguntar a Ollama</button><pre id='answer'></pre></div>
<div class='card'><h3>Cámara PC</h3><p class='small'>La cámara oficial del robot/MuJoCo sigue siendo la herramienta <code>camera</code>. Esta opción usa la webcam del PC.</p><button onclick="window.open('/camera_pc/page','_blank')">Abrir cámara PC</button></div>
<div class='card'><h3>Actividades estables</h3><p class='small'>Perfil recomendado: <code>ahootsa_realtime_es</code>. Incluye memory, comunicación, cámara PC, bailes y Ollama auxiliar sin duplicados en tools.txt.</p><a href='/ahootsa/status' target='_blank'>Ver JSON de diagnóstico</a></div>
</aside></div>
<script>
async function status(){{try{{const r=await fetch('/ahootsa/status');const j=await r.json();document.getElementById('hf').textContent=j.hf_mode+(j.hf_ws_url?' local':' deployed');document.getElementById('ol').textContent=j.ollama.ok?'OK':'NO';}}catch(e){{document.getElementById('ol').textContent='error';}}}}
async function ask(){{const el=document.getElementById('answer');el.textContent='Consultando Ollama local...';try{{const r=await fetch('/ollama/ask',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{prompt:document.getElementById('prompt').value}})}});const j=await r.json();el.textContent=j.reply||j.message_for_user||JSON.stringify(j,null,2);}}catch(e){{el.textContent='Error: '+e;}}}}
status();
</script></body></html>"""


def _camera_html() -> str:
    return """<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Cámara PC Ahootsa</title><style>body{font-family:Arial,sans-serif;background:#f6f7fb;color:#17213a;margin:20px}button{border:0;border-radius:10px;padding:10px 12px;background:#17213a;color:white;margin:4px;cursor:pointer}.pink{background:#ff2fa6}video,canvas,img{max-width:100%;border-radius:12px;border:1px solid #ccc;background:#000}pre{white-space:pre-wrap;background:white;padding:10px;border-radius:10px}</style></head><body><h1>Cámara PC Ahootsa</h1><p>Permite hacer una foto con la webcam del ordenador. No activa el micrófono.</p><button onclick='startCam()'>Activar cámara</button><button class='pink' onclick='takePhoto()'>Hacer foto</button><br><video id='v' autoplay playsinline width='640' height='360'></video><canvas id='c' width='640' height='360' style='display:none'></canvas><pre id='out'></pre><script>let stream=null;async function startCam(){try{stream=await navigator.mediaDevices.getUserMedia({video:{width:640,height:360},audio:false});document.getElementById('v').srcObject=stream;document.getElementById('out').textContent='Cámara activada.';}catch(e){document.getElementById('out').textContent='No se pudo activar cámara: '+e;}}async function takePhoto(){try{const v=document.getElementById('v'),c=document.getElementById('c');const ctx=c.getContext('2d');ctx.drawImage(v,0,0,c.width,c.height);const data=c.toDataURL('image/jpeg',0.88);const r=await fetch('/camera_pc/upload',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image:data})});const j=await r.json();document.getElementById('out').textContent=JSON.stringify(j,null,2);}catch(e){document.getElementById('out').textContent='Error foto: '+e;}}</script></body></html>"""


def mount_ahootsa_routes(app: Any) -> None:
    if app is None or getattr(app, '_ahootsa_5_0_44_routes', False):
        return
    setattr(app, '_ahootsa_5_0_44_routes', True)

    @app.get('/ahootsa')
    def _ahootsa_home() -> HTMLResponse:
        return HTMLResponse(_html())

    @app.get('/status')
    def _compat_status() -> JSONResponse:
        return JSONResponse({'ok': True, 'app': 'Ahootsa', 'version': VERSION, 'backend_status_ok': True})

    @app.get('/ahootsa/status')
    def _ahootsa_status() -> JSONResponse:
        ollama = {'ok': False}
        try:
            tags = _http_json(f'{_ollama_base()}/api/tags', timeout=4.0)
            names = [m.get('name') for m in tags.get('models', []) if isinstance(m, dict)]
            ollama = {'ok': True, 'models': names, 'selected': _ollama_model(), 'selected_available': _ollama_model() in names}
        except Exception as exc:
            ollama = {'ok': False, 'error': f'{type(exc).__name__}: {exc}'}
        return JSONResponse({'ok': True, 'version': VERSION, 'profile': os.getenv('REACHY_MINI_CUSTOM_PROFILE', ''), 'hf_mode': os.getenv('HF_REALTIME_CONNECTION_MODE', 'deployed'), 'hf_ws_url': os.getenv('HF_REALTIME_WS_URL', ''), 'ollama': ollama, 'camera_pc_upload_dir': str(_log_root() / 'camera_pc')})

    @app.get('/ollama/status')
    def _ollama_status() -> JSONResponse:
        try:
            tags = _http_json(f'{_ollama_base()}/api/tags', timeout=4.0)
            names = [m.get('name') for m in tags.get('models', []) if isinstance(m, dict)]
            return JSONResponse({'ok': True, 'base_url': _ollama_base(), 'model': _ollama_model(), 'models': names, 'selected_available': _ollama_model() in names})
        except Exception as exc:
            return JSONResponse({'ok': False, 'base_url': _ollama_base(), 'model': _ollama_model(), 'error': f'{type(exc).__name__}: {exc}'}, status_code=503)

    @app.get('/ollama/models')
    def _ollama_models() -> JSONResponse:
        try:
            return JSONResponse(_http_json(f'{_ollama_base()}/api/tags', timeout=6.0))
        except Exception as exc:
            return JSONResponse({'ok': False, 'error': f'{type(exc).__name__}: {exc}'}, status_code=503)

    async def _ask_request(request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except Exception:
            body = {}
        prompt = (body.get('prompt') or body.get('message') or body.get('text') or '').strip()
        if not prompt:
            return JSONResponse({'ok': False, 'error': 'prompt vacío', 'message_for_user': 'Escribe una pregunta para Ollama.'}, status_code=400)
        model = (body.get('model') or _ollama_model()).strip() or _ollama_model()
        system = (body.get('system_prompt') or 'Eres Ahootsa. Responde en castellano claro, breve y natural.').strip()
        payload = {'model': model, 'stream': False, 'messages': [{'role':'system','content':system},{'role':'user','content':prompt}], 'options': {'temperature':0.4, 'num_predict':160, 'num_ctx':2048}}
        try:
            data = _http_json(f'{_ollama_base()}/api/chat', payload=payload, timeout=float(os.getenv('AHOOTSA_OLLAMA_TIMEOUT_SECONDS','20')))
            msg = data.get('message', {}) if isinstance(data, dict) else {}
            reply = (msg.get('content') if isinstance(msg, dict) else '') or data.get('response','')
            return JSONResponse({'ok': True, 'reply': str(reply).strip(), 'message_for_user': str(reply).strip(), 'model': data.get('model', model), 'raw': data})
        except Exception as exc:
            return JSONResponse({'ok': False, 'error': f'{type(exc).__name__}: {exc}', 'message_for_user': 'Ollama local no ha respondido. Comprueba que Ollama está abierto y que existe el modelo llama3.2:3b.'}, status_code=503)

    app.post('/ollama/ask')(_ask_request)
    app.post('/ask_ollama')(_ask_request)
    app.post('/api/ask_ollama')(_ask_request)
    app.post('/api/ollama/ask')(_ask_request)
    app.post('/local-ai/ask')(_ask_request)
    app.post('/llm/ask')(_ask_request)
    app.post('/ask')(_ask_request)
    app.post('/chat')(_ask_request)

    @app.get('/camera_pc/page')
    def _camera_page() -> HTMLResponse:
        return HTMLResponse(_camera_html())

    @app.post('/camera_pc/upload')
    async def _camera_upload(request: Request) -> JSONResponse:
        try:
            body = await request.json()
            img = body.get('image','')
            if ',' in img:
                img = img.split(',', 1)[1]
            data = base64.b64decode(img)
            out_dir = _log_root() / 'camera_pc'
            out_dir.mkdir(parents=True, exist_ok=True)
            path = out_dir / f"camera_pc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            path.write_bytes(data)
            return JSONResponse({'ok': True, 'path': str(path), 'bytes': len(data)})
        except Exception as exc:
            return JSONResponse({'ok': False, 'error': f'{type(exc).__name__}: {exc}'}, status_code=400)

    @app.get('/camera_pc/latest')
    def _camera_latest() -> JSONResponse:
        out_dir = _log_root() / 'camera_pc'
        files = sorted(out_dir.glob('camera_pc_*.jpg')) if out_dir.exists() else []
        return JSONResponse({'ok': bool(files), 'latest': str(files[-1]) if files else None, 'count': len(files)})

    @app.get('/voices/current')
    def _voice_current() -> JSONResponse:
        return JSONResponse({'ok': True, 'voice': {'id': os.getenv('VOICE','Sohee'), 'name': os.getenv('VOICE','Sohee'), 'language':'es-ES', 'engine':'hf_realtime'}})

    @app.get('/voices')
    def _voices() -> JSONResponse:
        return JSONResponse({'ok': True, 'current': os.getenv('VOICE','Sohee'), 'voices': ['Sohee', 'Aiden', 'Serena', 'Vivian']})

    @app.get('/mic')
    def _mic() -> JSONResponse:
        return JSONResponse({'ok': True, 'muted': False})
