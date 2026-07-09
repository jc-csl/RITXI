# -*- coding: utf-8 -*-
"""
Ahootsa 5.0.41 patch autónomo.
Se aplica sobre el paquete instalado en apps_venv:
  ahootsa_realtime_ollama_desktop_app
No depende de carpetas 5_0_25..5_0_40.
"""
from __future__ import annotations
import os, sys, pathlib, datetime, shutil

MARKER_BEGIN = "# >>> AHOOTSA_5_0_41_AUTONOMA_BEGIN"
MARKER_END = "# <<< AHOOTSA_5_0_41_AUTONOMA_END"

BOOTSTRAP = r'''
# >>> AHOOTSA_5_0_41_AUTONOMA_BEGIN
# Parche autónomo Ahootsa 5.0.41: endpoints, Ollama/HF local, cámara PC, audio Windows bloqueado.
try:
    import os as _aos, json as _ajson, base64 as _abase64, datetime as _adt, pathlib as _apathlib, urllib.request as _aurlreq, urllib.error as _aurlerr

    _AHOOTSA_41_DONE = False

    def _ahootsa_41_log(msg):
        try:
            root = _aos.environ.get('AHOOTSA_LOG_ROOT') or r'D:\RITXI\logs'
            _apathlib.Path(root).mkdir(parents=True, exist_ok=True)
            with open(str(_apathlib.Path(root) / 'ahootsa_5_0_41_patch.log'), 'a', encoding='utf-8') as f:
                f.write(_adt.datetime.now().isoformat(timespec='seconds') + ' ' + str(msg) + '\n')
        except Exception:
            pass

    def _ahootsa_41_disable_windows_audio():
        # Evita voz/beeps Windows en actividades. La voz Ahootsa/realtime queda fuera de este bloqueo.
        try:
            import winsound as _winsound
            def _silent_beep(*args, **kwargs):
                return None
            _winsound.Beep = _silent_beep
            _winsound.MessageBeep = _silent_beep
        except Exception:
            pass
        try:
            import pyttsx3 as _pyttsx3
            class _SilentEngine:
                def say(self, *a, **k): return None
                def runAndWait(self, *a, **k): return None
                def stop(self, *a, **k): return None
                def setProperty(self, *a, **k): return None
                def getProperty(self, *a, **k): return None
            _pyttsx3.init = lambda *a, **k: _SilentEngine()
        except Exception:
            pass
        try:
            import win32com.client as _w32
            _orig_dispatch = getattr(_w32, 'Dispatch', None)
            class _SilentSapi:
                def Speak(self, *a, **k): return 0
                def __getattr__(self, name):
                    def _noop(*a, **k): return None
                    return _noop
            def _dispatch(name, *a, **k):
                if str(name).lower() in ('sapi.spvoice','speech.spvoice'):
                    return _SilentSapi()
                return _orig_dispatch(name, *a, **k) if _orig_dispatch else _SilentSapi()
            _w32.Dispatch = _dispatch
        except Exception:
            pass

    def _ahootsa_41_json_response(data, status_code=200):
        try:
            from fastapi.responses import JSONResponse
            return JSONResponse(data, status_code=status_code)
        except Exception:
            try:
                from starlette.responses import JSONResponse
                return JSONResponse(data, status_code=status_code)
            except Exception:
                return data

    def _ahootsa_41_ollama_generate(prompt, model=None, timeout=None):
        base = (_aos.environ.get('AHOOTSA_OLLAMA_BASE_URL') or 'http://127.0.0.1:11434').rstrip('/')
        model = model or _aos.environ.get('AHOOTSA_OLLAMA_MODEL') or 'llama3.2:3b'
        timeout = float(timeout or _aos.environ.get('AHOOTSA_OLLAMA_TIMEOUT') or '25')
        payload = {
            'model': model,
            'prompt': str(prompt or ''),
            'stream': False,
            'options': {
                'num_predict': int(_aos.environ.get('AHOOTSA_OLLAMA_NUM_PREDICT') or '120'),
                'temperature': float(_aos.environ.get('AHOOTSA_OLLAMA_TEMPERATURE') or '0.45'),
                'top_p': float(_aos.environ.get('AHOOTSA_OLLAMA_TOP_P') or '0.9'),
            }
        }
        req = _aurlreq.Request(base + '/api/generate', data=_ajson.dumps(payload).encode('utf-8'), headers={'Content-Type':'application/json'}, method='POST')
        with _aurlreq.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode('utf-8', errors='replace')
        data = _ajson.loads(raw)
        return data.get('response','')

    def _ahootsa_41_hf_generate(prompt, timeout=None):
        # Implementación local sencilla. Requiere transformers/torch y modelo en AHOOTSA_HF_MODEL_PATH.
        model_path = _aos.environ.get('AHOOTSA_HF_MODEL_PATH') or ''
        if not model_path:
            raise RuntimeError('AHOOTSA_HF_MODEL_PATH no está configurado')
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        import torch
        if not hasattr(_ahootsa_41_hf_generate, '_pipe'):
            tok = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
            model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True, torch_dtype='auto', device_map='auto')
            _ahootsa_41_hf_generate._pipe = pipeline('text-generation', model=model, tokenizer=tok)
        out = _ahootsa_41_hf_generate._pipe(str(prompt), max_new_tokens=int(_aos.environ.get('AHOOTSA_HF_MAX_NEW_TOKENS') or '120'), do_sample=True, temperature=float(_aos.environ.get('AHOOTSA_HF_TEMPERATURE') or '0.45'))
        txt = out[0].get('generated_text','') if out else ''
        if txt.startswith(str(prompt)):
            txt = txt[len(str(prompt)):]
        return txt.strip()

    async def _ahootsa_41_status():
        return {'ok': True, 'status': 'running', 'app': 'Ahootsa', 'version_patch': '5.0.41', 'provider': _aos.environ.get('AHOOTSA_LLM_PROVIDER','ollama')}

    async def _ahootsa_41_mic():
        return {'ok': True, 'available': False, 'enabled': False, 'recording': False, 'message': 'Micrófono no gestionado por este endpoint de compatibilidad.'}

    async def _ahootsa_41_voices_current():
        return {'ok': True, 'voice': {'id': _aos.environ.get('AHOOTSA_VOICE','Sohee'), 'name': _aos.environ.get('AHOOTSA_VOICE','Sohee'), 'language': 'es-ES', 'engine': 'ahootsa_realtime'}}

    async def _ahootsa_41_voices():
        cur = _aos.environ.get('AHOOTSA_VOICE','Sohee')
        return {'ok': True, 'current': cur, 'voices': [{'id': cur, 'name': cur, 'language':'es-ES', 'engine':'ahootsa_realtime'}]}

    async def _ahootsa_41_ollama_status():
        base = (_aos.environ.get('AHOOTSA_OLLAMA_BASE_URL') or 'http://127.0.0.1:11434').rstrip('/')
        model = _aos.environ.get('AHOOTSA_OLLAMA_MODEL') or 'llama3.2:3b'
        try:
            with _aurlreq.urlopen(base + '/api/tags', timeout=3) as r:
                data = _ajson.loads(r.read().decode('utf-8', errors='replace'))
            models = [m.get('name') for m in data.get('models', []) if isinstance(m, dict)]
            return {'ok': True, 'base_url': base, 'model': model, 'models': models, 'model_available': model in models}
        except Exception as e:
            return {'ok': False, 'base_url': base, 'model': model, 'error': str(e)}

    async def _ahootsa_41_ollama_models():
        return await _ahootsa_41_ollama_status()

    async def _ahootsa_41_ollama_ask(request):
        try:
            body = await request.json()
        except Exception:
            body = {}
        prompt = body.get('prompt') or body.get('question') or body.get('message') or ''
        provider = (body.get('provider') or _aos.environ.get('AHOOTSA_LLM_PROVIDER') or 'ollama').lower()
        system = _aos.environ.get('AHOOTSA_SYSTEM_PROMPT') or 'Responde en castellano claro, cercano y breve. Haz una sola pregunta cada vez si necesitas continuar.'
        full_prompt = system + '\n\nUsuario: ' + str(prompt).strip() + '\nAhootsa:'
        try:
            if provider in ('hf','hf_local','huggingface'):
                answer = _ahootsa_41_hf_generate(full_prompt)
                used = 'hf_local'
            else:
                answer = _ahootsa_41_ollama_generate(full_prompt, model=body.get('model'))
                used = 'ollama'
            return {'ok': True, 'provider': used, 'answer': answer, 'response': answer, 'text': answer, 'message_for_user': answer, 'robot_say': answer}
        except Exception as e:
            msg = 'No he podido obtener respuesta del modelo local. ' + str(e)
            return _ahootsa_41_json_response({'ok': False, 'error': str(e), 'answer': msg, 'response': msg, 'text': msg}, status_code=200)

    async def _ahootsa_41_camera_health():
        return {'ok': True, 'mode': 'browser_camera', 'note': 'La cámara PC se activa desde el navegador mediante getUserMedia; este endpoint solo guarda fotos.'}

    async def _ahootsa_41_camera_latest():
        root = _apathlib.Path(_aos.environ.get('AHOOTSA_CAMERA_DIR') or r'D:\RITXI\logs\camera')
        imgs = sorted(list(root.glob('*.png')) + list(root.glob('*.jpg')) + list(root.glob('*.jpeg')), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
        if not imgs:
            return {'ok': False, 'message': 'No hay fotos guardadas todavía.', 'dir': str(root)}
        p = imgs[0]
        return {'ok': True, 'path': str(p), 'name': p.name, 'size': p.stat().st_size}

    async def _ahootsa_41_camera_upload(request):
        try:
            body = await request.json()
            data = body.get('image') or body.get('dataUrl') or ''
            if ',' in data:
                data = data.split(',',1)[1]
            raw = _abase64.b64decode(data)
            root = _apathlib.Path(_aos.environ.get('AHOOTSA_CAMERA_DIR') or r'D:\RITXI\logs\camera')
            root.mkdir(parents=True, exist_ok=True)
            name = 'ahootsa_pc_camera_' + _adt.datetime.now().strftime('%Y%m%d_%H%M%S') + '.png'
            path = root / name
            path.write_bytes(raw)
            return {'ok': True, 'path': str(path), 'name': name, 'size': len(raw)}
        except Exception as e:
            return _ahootsa_41_json_response({'ok': False, 'error': str(e)}, status_code=200)

    async def _ahootsa_41_camera_page():
        try:
            from starlette.responses import HTMLResponse
        except Exception:
            from fastapi.responses import HTMLResponse
        return HTMLResponse(_AHOOTSA_41_CAMERA_HTML)

    _AHOOTSA_41_CAMERA_HTML = '''<!doctype html><html><head><meta charset="utf-8"><title>Ahootsa Cámara PC</title>
<style>body{font-family:Arial;margin:24px;background:#fafafa}button{font-size:16px;margin:6px;padding:10px 14px;border-radius:10px;border:1px solid #ccc}video,canvas,img{max-width:720px;width:95%;border:2px solid #d8d8d8;border-radius:14px;background:#eee}.ok{color:#187a2f}.err{color:#b00020}</style></head>
<body><h1>Cámara PC - Ahootsa 5.0.41</h1><p>Esta prueba usa la cámara del ordenador mediante permiso del navegador. No activa el micrófono.</p>
<button onclick="startCam()">Activar cámara</button><button onclick="takePhoto()">Hacer foto</button><button onclick="stopCam()">Parar cámara</button><p id="status"></p><video id="v" autoplay playsinline muted></video><canvas id="c" style="display:none"></canvas><p><img id="preview"></p>
<script>
let stream=null; const st=document.getElementById('status');
function msg(t,ok=true){st.className=ok?'ok':'err'; st.textContent=t;}
async function startCam(){try{stream=await navigator.mediaDevices.getUserMedia({video:true,audio:false});document.getElementById('v').srcObject=stream;msg('Cámara activa.');}catch(e){msg('No se pudo activar la cámara: '+e,false);}}
function stopCam(){if(stream){stream.getTracks().forEach(t=>t.stop());stream=null;msg('Cámara parada.');}}
async function takePhoto(){try{const v=document.getElementById('v'); if(!stream){await startCam(); await new Promise(r=>setTimeout(r,600));} const c=document.getElementById('c'); c.width=v.videoWidth||640; c.height=v.videoHeight||480; c.getContext('2d').drawImage(v,0,0,c.width,c.height); const data=c.toDataURL('image/png'); document.getElementById('preview').src=data; const r=await fetch('/camera/upload',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image:data})}); const j=await r.json(); msg(j.ok?'Foto guardada: '+j.path:'Error guardando: '+JSON.stringify(j),j.ok);}catch(e){msg('Error haciendo foto: '+e,false);}}
</script></body></html>'''

    _AHOOTSA_41_PANEL_JS = r'''
<script id="ahootsa-5-0-41-panel">
(function(){
  if(window.__AHOOTSA_5_0_41_PANEL__) return; window.__AHOOTSA_5_0_41_PANEL__=true;
  try{
    if('speechSynthesis' in window){ window.speechSynthesis.cancel(); const noop=function(){}; window.speechSynthesis.speak=noop; window.speechSynthesis.resume=noop; }
    window.SpeechSynthesisUtterance=function(){return {};};
  }catch(e){}
  function add(){
    if(document.getElementById('ahootsa41box')) return;
    const box=document.createElement('div'); box.id='ahootsa41box';
    box.style.cssText='position:fixed;right:12px;bottom:12px;z-index:999999;background:white;border:2px solid #df2b8c;border-radius:14px;padding:10px;box-shadow:0 4px 18px #0003;font-family:Arial;max-width:330px;font-size:13px';
    box.innerHTML='<b style="color:#df2b8c">Ahootsa 5.0.41</b><br><button id="a41cam">Cámara PC</button> <button id="a41oll">Estado Ollama</button><br><input id="a41q" placeholder="Preguntar al modelo local" style="width:210px;margin-top:6px"><button id="a41ask">Preguntar</button><div id="a41out" style="margin-top:6px;max-height:100px;overflow:auto"></div>';
    document.body.appendChild(box);
    document.getElementById('a41cam').onclick=function(){ window.open('/camera/page','_blank'); };
    document.getElementById('a41oll').onclick=async function(){let o=document.getElementById('a41out'); o.textContent='Comprobando...'; try{let r=await fetch('/ollama/status'); o.textContent=JSON.stringify(await r.json());}catch(e){o.textContent='Error: '+e;}};
    document.getElementById('a41ask').onclick=async function(){let q=document.getElementById('a41q').value||'Di hola brevemente';let o=document.getElementById('a41out'); o.textContent='Preguntando...'; try{let r=await fetch('/ollama/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:q})}); let j=await r.json(); o.textContent=j.answer||j.response||JSON.stringify(j);}catch(e){o.textContent='Error: '+e;}};
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',add); else add();
})();
</script>
'''

    def _ahootsa_41_patch_app(app):
        try:
            if getattr(app, '_ahootsa_5_0_41_patched', False):
                return app
            setattr(app, '_ahootsa_5_0_41_patched', True)
            _ahootsa_41_disable_windows_audio()
            # Rutas de compatibilidad y funciones nuevas.
            routes = [
                ('/status', _ahootsa_41_status, ['GET']),
                ('/mic', _ahootsa_41_mic, ['GET']),
                ('/voices/current', _ahootsa_41_voices_current, ['GET']),
                ('/voices', _ahootsa_41_voices, ['GET']),
                ('/ollama/status', _ahootsa_41_ollama_status, ['GET']),
                ('/ollama/models', _ahootsa_41_ollama_models, ['GET']),
                ('/ollama/ask', _ahootsa_41_ollama_ask, ['POST']),
                ('/camera/health', _ahootsa_41_camera_health, ['GET']),
                ('/camera/page', _ahootsa_41_camera_page, ['GET']),
                ('/camera/upload', _ahootsa_41_camera_upload, ['POST']),
                ('/camera/latest', _ahootsa_41_camera_latest, ['GET']),
            ]
            existing = set()
            try:
                existing = {getattr(r, 'path', '') for r in getattr(app, 'routes', [])}
            except Exception:
                pass
            for path, func, methods in routes:
                if path not in existing and hasattr(app, 'add_api_route'):
                    app.add_api_route(path, func, methods=methods)
            if hasattr(app, 'middleware') and not getattr(app, '_ahootsa_5_0_41_middleware', False):
                setattr(app, '_ahootsa_5_0_41_middleware', True)
                @app.middleware('http')
                async def _ahootsa_41_inject_panel(request, call_next):
                    response = await call_next(request)
                    try:
                        ctype = response.headers.get('content-type','')
                        if 'text/html' in ctype.lower():
                            body = b''
                            async for chunk in response.body_iterator:
                                body += chunk
                            text = body.decode('utf-8', errors='replace')
                            if 'ahootsa-5-0-41-panel' not in text:
                                text = text.replace('</body>', _AHOOTSA_41_PANEL_JS + '</body>') if '</body>' in text else text + _AHOOTSA_41_PANEL_JS
                            try:
                                from starlette.responses import HTMLResponse
                            except Exception:
                                from fastapi.responses import HTMLResponse
                            return HTMLResponse(text, status_code=response.status_code, headers=dict(response.headers))
                    except Exception:
                        pass
                    return response
            _ahootsa_41_log('app patched ok')
        except Exception as e:
            _ahootsa_41_log('app patch error: ' + repr(e))
        return app

    try:
        import fastapi as _fastapi
        _orig_fastapi_init = _fastapi.FastAPI.__init__
        def _new_fastapi_init(self, *a, **k):
            _orig_fastapi_init(self, *a, **k)
            _ahootsa_41_patch_app(self)
        if not getattr(_fastapi.FastAPI.__init__, '_ahootsa_5_0_41_wrapped', False):
            _new_fastapi_init._ahootsa_5_0_41_wrapped = True
            _fastapi.FastAPI.__init__ = _new_fastapi_init
    except Exception as e:
        _ahootsa_41_log('fastapi wrap error: ' + repr(e))

    try:
        import starlette.applications as _sapp
        _orig_starlette_init = _sapp.Starlette.__init__
        def _new_starlette_init(self, *a, **k):
            _orig_starlette_init(self, *a, **k)
            _ahootsa_41_patch_app(self)
        if not getattr(_sapp.Starlette.__init__, '_ahootsa_5_0_41_wrapped', False):
            _new_starlette_init._ahootsa_5_0_41_wrapped = True
            _sapp.Starlette.__init__ = _new_starlette_init
    except Exception as e:
        _ahootsa_41_log('starlette wrap error: ' + repr(e))

    _ahootsa_41_disable_windows_audio()
    _ahootsa_41_log('bootstrap loaded')
except Exception as _e:
    try:
        print('AHOOTSA_5_0_41_BOOTSTRAP_ERROR', repr(_e))
    except Exception:
        pass
# <<< AHOOTSA_5_0_41_AUTONOMA_END
'''

def main() -> int:
    try:
        import ahootsa_realtime_ollama_desktop_app as pkg
    except Exception as e:
        print('[ERROR] No se pudo importar ahootsa_realtime_ollama_desktop_app:', repr(e))
        return 2
    init_path = pathlib.Path(pkg.__file__).resolve()
    print('PACKAGE_INIT=' + str(init_path))
    text = init_path.read_text(encoding='utf-8', errors='ignore')
    if MARKER_BEGIN in text and MARKER_END in text:
        before = text.split(MARKER_BEGIN)[0].rstrip() + '\n'
        after = text.split(MARKER_END, 1)[1].lstrip('\n')
        new = before + BOOTSTRAP.strip() + '\n' + after
    else:
        backup = init_path.with_suffix(init_path.suffix + '.bak_5_0_41_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        shutil.copy2(init_path, backup)
        print('BACKUP=' + str(backup))
        new = BOOTSTRAP.strip() + '\n\n' + text
    init_path.write_text(new, encoding='utf-8')
    print('PATCH_OK=5.0.41')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
