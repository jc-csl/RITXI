# -*- coding: utf-8 -*-
"""
Ahootsa 5.0.43 parche autónomo completo.
- No depende de carpetas antiguas 5_0_25..5_0_42.
- Parchea el paquete instalado en apps_venv: ahootsa_realtime_ollama_desktop_app.
- Añade endpoints estables y alias para IA local/Ollama.
- Añade cámara PC y bloqueo de audio Windows.
"""
from __future__ import annotations
import pathlib, datetime, shutil

MARKER_BEGIN = "# >>> AHOOTSA_5_0_43_AUTONOMA_BEGIN"
MARKER_END = "# <<< AHOOTSA_5_0_43_AUTONOMA_END"

BOOTSTRAP = r"""
# >>> AHOOTSA_5_0_43_AUTONOMA_BEGIN
try:
    import os as _aos, json as _ajson, base64 as _abase64, datetime as _adt, pathlib as _apathlib, urllib.request as _aurlreq, urllib.error as _aurlerr

    def _ah43_log(msg):
        try:
            root = _aos.environ.get('AHOOTSA_LOG_ROOT') or r'D:\RITXI\logs'
            _apathlib.Path(root).mkdir(parents=True, exist_ok=True)
            with open(str(_apathlib.Path(root) / 'ahootsa_5_0_43_patch.log'), 'a', encoding='utf-8') as f:
                f.write(_adt.datetime.now().isoformat(timespec='seconds') + ' ' + str(msg) + '\n')
        except Exception:
            pass

    def _ah43_disable_windows_audio():
        try:
            import winsound as _winsound
            _winsound.Beep = lambda *a, **k: None
            _winsound.MessageBeep = lambda *a, **k: None
        except Exception:
            pass
        try:
            import pyttsx3 as _pyttsx3
            class _SilentEngine:
                def say(self,*a,**k): return None
                def runAndWait(self,*a,**k): return None
                def stop(self,*a,**k): return None
                def setProperty(self,*a,**k): return None
                def getProperty(self,*a,**k): return None
            _pyttsx3.init = lambda *a, **k: _SilentEngine()
        except Exception:
            pass
        try:
            import win32com.client as _w32
            _orig = getattr(_w32, 'Dispatch', None)
            class _SilentSapi:
                def Speak(self,*a,**k): return 0
                def __getattr__(self, name):
                    return lambda *a, **k: None
            def _dispatch(name,*a,**k):
                if str(name).lower().replace(' ','') in ('sapi.spvoice','speech.spvoice'):
                    return _SilentSapi()
                return _orig(name,*a,**k) if _orig else _SilentSapi()
            _w32.Dispatch = _dispatch
        except Exception:
            pass

    def _ah43_json(data, status_code=200):
        try:
            from fastapi.responses import JSONResponse
            return JSONResponse(data, status_code=status_code)
        except Exception:
            try:
                from starlette.responses import JSONResponse
                return JSONResponse(data, status_code=status_code)
            except Exception:
                return data

    def _ah43_ollama_models_raw(base=None):
        base = (base or _aos.environ.get('AHOOTSA_OLLAMA_BASE_URL') or 'http://127.0.0.1:11434').rstrip('/')
        with _aurlreq.urlopen(base + '/api/tags', timeout=4) as r:
            data = _ajson.loads(r.read().decode('utf-8', errors='replace'))
        return [m.get('name') for m in data.get('models', []) if isinstance(m, dict) and m.get('name')]

    def _ah43_select_model(requested=None):
        requested = requested or _aos.environ.get('AHOOTSA_OLLAMA_MODEL') or 'llama3.2:3b'
        try:
            models = _ah43_ollama_models_raw()
            if requested in models:
                return requested, models, False
            for pref in ('llama3.2:3b','llama3.2','qwen2.5:3b','mistral:7b'):
                if pref in models:
                    return pref, models, True
            if models:
                return models[0], models, True
            return requested, models, False
        except Exception:
            return requested, [], False

    def _ah43_ollama_generate(prompt, model=None, timeout=None):
        base = (_aos.environ.get('AHOOTSA_OLLAMA_BASE_URL') or 'http://127.0.0.1:11434').rstrip('/')
        model, models, auto = _ah43_select_model(model)
        timeout = float(timeout or _aos.environ.get('AHOOTSA_OLLAMA_TIMEOUT') or '25')
        payload = {
            'model': model,
            'prompt': str(prompt or ''),
            'stream': False,
            'options': {
                'num_predict': int(_aos.environ.get('AHOOTSA_OLLAMA_NUM_PREDICT') or '140'),
                'temperature': float(_aos.environ.get('AHOOTSA_OLLAMA_TEMPERATURE') or '0.45'),
                'top_p': float(_aos.environ.get('AHOOTSA_OLLAMA_TOP_P') or '0.9'),
            }
        }
        _ah43_log('ollama_generate model=' + str(model) + ' prompt=' + str(prompt)[:120])
        req = _aurlreq.Request(base + '/api/generate', data=_ajson.dumps(payload).encode('utf-8'), headers={'Content-Type':'application/json'}, method='POST')
        try:
            with _aurlreq.urlopen(req, timeout=timeout) as r:
                raw = r.read().decode('utf-8', errors='replace')
            data = _ajson.loads(raw)
            ans = data.get('response','') or ''
            return {'ok': True, 'answer': ans.strip(), 'response': ans.strip(), 'text': ans.strip(), 'model': model, 'models': models, 'auto_model': auto}
        except Exception as e:
            return {'ok': False, 'answer': '', 'response': '', 'text': '', 'model': model, 'models': models, 'error': repr(e)}

    def _ah43_hf_generate(prompt):
        model_path = _aos.environ.get('AHOOTSA_HF_MODEL_PATH') or ''
        if not model_path:
            raise RuntimeError('AHOOTSA_HF_MODEL_PATH no está configurado')
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        if not hasattr(_ah43_hf_generate, '_pipe'):
            tok = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
            model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True, torch_dtype='auto', device_map='auto')
            _ah43_hf_generate._pipe = pipeline('text-generation', model=model, tokenizer=tok)
        out = _ah43_hf_generate._pipe(str(prompt), max_new_tokens=int(_aos.environ.get('AHOOTSA_HF_MAX_NEW_TOKENS') or '140'), do_sample=True, temperature=float(_aos.environ.get('AHOOTSA_HF_TEMPERATURE') or '0.45'))
        txt = out[0].get('generated_text','') if out else ''
        if txt.startswith(str(prompt)):
            txt = txt[len(str(prompt)):]
        return txt.strip()

    async def _ah43_status():
        return {'ok': True, 'status': 'running', 'app': 'Ahootsa', 'version_patch': '5.0.43', 'provider': _aos.environ.get('AHOOTSA_LLM_PROVIDER','ollama'), 'ollama_model': _aos.environ.get('AHOOTSA_OLLAMA_MODEL','llama3.2:3b')}

    async def _ah43_mic():
        return {'ok': True, 'available': False, 'enabled': False, 'recording': False}

    async def _ah43_voices_current():
        cur = _aos.environ.get('AHOOTSA_VOICE','Sohee')
        return {'ok': True, 'voice': {'id': cur, 'name': cur, 'language': 'es-ES', 'engine': 'ahootsa_realtime'}}

    async def _ah43_voices():
        cur = _aos.environ.get('AHOOTSA_VOICE','Sohee')
        return {'ok': True, 'current': cur, 'voices': [{'id': cur, 'name': cur, 'language':'es-ES', 'engine':'ahootsa_realtime'}]}

    async def _ah43_ollama_status():
        base = (_aos.environ.get('AHOOTSA_OLLAMA_BASE_URL') or 'http://127.0.0.1:11434').rstrip('/')
        req_model = _aos.environ.get('AHOOTSA_OLLAMA_MODEL') or 'llama3.2:3b'
        try:
            model, models, auto = _ah43_select_model(req_model)
            return {'ok': True, 'base_url': base, 'requested_model': req_model, 'model': model, 'models': models, 'model_available': req_model in models, 'auto_model': auto}
        except Exception as e:
            return {'ok': False, 'base_url': base, 'requested_model': req_model, 'error': repr(e)}

    async def _ah43_ollama_models():
        return await _ah43_ollama_status()

    async def _ah43_ask(request=None):
        body = {}
        query_params = {}
        try:
            if request is not None:
                query_params = dict(getattr(request, 'query_params', {}) or {})
                if getattr(request, 'method', 'GET').upper() in ('POST','PUT','PATCH'):
                    try: body = await request.json()
                    except Exception: body = {}
        except Exception:
            body = {}
        prompt = body.get('prompt') or body.get('question') or body.get('message') or body.get('text') or query_params.get('prompt') or query_params.get('q') or query_params.get('question') or ''
        provider = (body.get('provider') or query_params.get('provider') or _aos.environ.get('AHOOTSA_LLM_PROVIDER') or 'ollama').lower()
        system = _aos.environ.get('AHOOTSA_SYSTEM_PROMPT') or 'Eres Ahootsa, un asistente educativo amable. Responde en castellano natural, claro y breve. Usa frases cortas. Haz solo una pregunta de seguimiento si aporta valor.'
        full_prompt = system + '\n\nUsuario: ' + str(prompt).strip() + '\nAhootsa:'
        try:
            if provider in ('hf','hf_local','huggingface'):
                ans = _ah43_hf_generate(full_prompt)
                data = {'ok': True, 'provider': 'hf_local', 'answer': ans, 'response': ans, 'text': ans, 'message': ans, 'message_for_user': ans, 'robot_say': ans, 'speak': ans}
            else:
                data = _ah43_ollama_generate(full_prompt, model=body.get('model') or query_params.get('model'))
                data.update({'provider':'ollama', 'message': data.get('answer',''), 'message_for_user': data.get('answer',''), 'robot_say': data.get('answer',''), 'speak': data.get('answer','')})
            if not data.get('ok'):
                data['answer'] = 'No he podido responder con la IA local. Revisa Ollama y el modelo configurado.'
                data['response'] = data['answer']; data['text'] = data['answer']; data['message_for_user'] = data['answer']
            return data
        except Exception as e:
            msg = 'No he podido obtener respuesta del modelo local: ' + repr(e)
            return _ah43_json({'ok': False, 'error': repr(e), 'answer': msg, 'response': msg, 'text': msg, 'message_for_user': msg}, 200)

    async def _ah43_camera_health():
        return {'ok': True, 'mode': 'browser_camera', 'requires': 'permiso de cámara del navegador/WebView', 'audio': False}

    async def _ah43_camera_latest():
        root = _apathlib.Path(_aos.environ.get('AHOOTSA_CAMERA_DIR') or r'D:\RITXI\logs\camera')
        imgs = sorted(list(root.glob('*.png')) + list(root.glob('*.jpg')) + list(root.glob('*.jpeg')), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
        if not imgs: return {'ok': False, 'message': 'No hay fotos guardadas todavía.', 'dir': str(root)}
        p = imgs[0]
        return {'ok': True, 'path': str(p), 'name': p.name, 'size': p.stat().st_size}

    async def _ah43_camera_upload(request):
        try:
            body = await request.json()
            data = body.get('image') or body.get('dataUrl') or ''
            if ',' in data: data = data.split(',',1)[1]
            raw = _abase64.b64decode(data)
            root = _apathlib.Path(_aos.environ.get('AHOOTSA_CAMERA_DIR') or r'D:\RITXI\logs\camera')
            root.mkdir(parents=True, exist_ok=True)
            name = 'ahootsa_pc_camera_' + _adt.datetime.now().strftime('%Y%m%d_%H%M%S') + '.png'
            path = root / name
            path.write_bytes(raw)
            return {'ok': True, 'path': str(path), 'name': name, 'size': len(raw)}
        except Exception as e:
            return _ah43_json({'ok': False, 'error': repr(e)}, 200)

    async def _ah43_camera_page():
        try:
            from starlette.responses import HTMLResponse
        except Exception:
            from fastapi.responses import HTMLResponse
        return HTMLResponse(_AH43_CAMERA_HTML)

    _AH43_CAMERA_HTML = '''<!doctype html><html><head><meta charset="utf-8"><title>Ahootsa Cámara PC</title><style>body{font-family:Arial;margin:24px;background:#fafafa}button{font-size:16px;margin:6px;padding:10px 14px;border-radius:10px;border:1px solid #ccc}video,canvas,img{max-width:720px;width:95%;border:2px solid #d8d8d8;border-radius:14px;background:#eee}.ok{color:#187a2f}.err{color:#b00020}</style></head><body><h1>Cámara PC - Ahootsa 5.0.43</h1><p>Usa la cámara del ordenador mediante permiso del navegador. No activa el micrófono.</p><button onclick="startCam()">Activar cámara</button><button onclick="takePhoto()">Hacer foto</button><button onclick="stopCam()">Parar cámara</button><p id="status"></p><video id="v" autoplay playsinline muted></video><canvas id="c" style="display:none"></canvas><p><img id="preview"></p><script>let stream=null; const st=document.getElementById('status'); function msg(t,ok=true){st.className=ok?'ok':'err'; st.textContent=t;} async function startCam(){try{if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){msg('Este navegador/WebView no permite getUserMedia.',false);return;} stream=await navigator.mediaDevices.getUserMedia({video:true,audio:false});document.getElementById('v').srcObject=stream;msg('Cámara activa.');}catch(e){msg('No se pudo activar la cámara: '+e,false);}} function stopCam(){if(stream){stream.getTracks().forEach(t=>t.stop());stream=null;msg('Cámara parada.');}} async function takePhoto(){try{const v=document.getElementById('v'); if(!stream){await startCam(); await new Promise(r=>setTimeout(r,800));} const c=document.getElementById('c'); c.width=v.videoWidth||640; c.height=v.videoHeight||480; c.getContext('2d').drawImage(v,0,0,c.width,c.height); const data=c.toDataURL('image/png'); document.getElementById('preview').src=data; const r=await fetch('/camera/upload',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image:data})}); const j=await r.json(); msg(j.ok?'Foto guardada: '+j.path:'Error guardando: '+JSON.stringify(j),j.ok);}catch(e){msg('Error haciendo foto: '+e,false);}}</script></body></html>'''

    _AH43_PANEL_JS = r'''
<script id="ahootsa-5-0-43-panel">
(function(){
  if(window.__AHOOTSA_5_0_43_PANEL__) return; window.__AHOOTSA_5_0_43_PANEL__=true;
  try{ if('speechSynthesis' in window){ window.speechSynthesis.cancel(); window.speechSynthesis.speak=function(){}; window.speechSynthesis.resume=function(){}; } window.SpeechSynthesisUtterance=function(){return {};}; }catch(e){}
  function add(){
    if(document.getElementById('ahootsa43box')) return;
    const box=document.createElement('div'); box.id='ahootsa43box';
    box.style.cssText='position:fixed;right:12px;bottom:12px;z-index:999999;background:white;border:2px solid #df2b8c;border-radius:14px;padding:10px;box-shadow:0 4px 18px #0003;font-family:Arial;max-width:350px;font-size:13px';
    box.innerHTML='<b style="color:#df2b8c">Ahootsa 5.0.43</b><br><button id="a43cam">Cámara PC</button> <button id="a43oll">Estado IA local</button><br><input id="a43q" placeholder="Preguntar a IA local" style="width:220px;margin-top:6px"><button id="a43ask">Preguntar</button><div id="a43out" style="margin-top:6px;max-height:130px;overflow:auto;white-space:pre-wrap"></div>';
    document.body.appendChild(box);
    document.getElementById('a43cam').onclick=function(){ window.open('/camera/page','_blank'); };
    document.getElementById('a43oll').onclick=async function(){let o=document.getElementById('a43out'); o.textContent='Comprobando...'; try{let r=await fetch('/ollama/status'); o.textContent=JSON.stringify(await r.json(),null,2);}catch(e){o.textContent='Error: '+e;}};
    document.getElementById('a43ask').onclick=async function(){let q=document.getElementById('a43q').value||'Di hola brevemente';let o=document.getElementById('a43out'); o.textContent='Preguntando...'; try{let r=await fetch('/ollama/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:q})}); let j=await r.json(); o.textContent=j.answer||j.response||j.text||JSON.stringify(j,null,2);}catch(e){o.textContent='Error: '+e;}};
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',add); else add();
})();
</script>
'''

    def _ah43_patch_app(app):
        try:
            if getattr(app, '_ahootsa_5_0_43_patched', False):
                return app
            setattr(app, '_ahootsa_5_0_43_patched', True)
            _ah43_disable_windows_audio()
            routes = [
                ('/status', _ah43_status, ['GET']),
                ('/mic', _ah43_mic, ['GET']),
                ('/voices/current', _ah43_voices_current, ['GET']),
                ('/voices', _ah43_voices, ['GET']),
                ('/ollama/status', _ah43_ollama_status, ['GET']),
                ('/ollama/models', _ah43_ollama_models, ['GET']),
                ('/ollama/ask', _ah43_ask, ['GET','POST']),
                ('/ask_ollama', _ah43_ask, ['GET','POST']),
                ('/ask-ollama', _ah43_ask, ['GET','POST']),
                ('/api/ollama/ask', _ah43_ask, ['GET','POST']),
                ('/api/ask_ollama', _ah43_ask, ['GET','POST']),
                ('/api/local-ai/ask', _ah43_ask, ['GET','POST']),
                ('/local-ai/ask', _ah43_ask, ['GET','POST']),
                ('/llm/ask', _ah43_ask, ['GET','POST']),
                ('/ask', _ah43_ask, ['GET','POST']),
                ('/chat', _ah43_ask, ['GET','POST']),
                ('/camera/health', _ah43_camera_health, ['GET']),
                ('/camera/page', _ah43_camera_page, ['GET']),
                ('/camera/upload', _ah43_camera_upload, ['POST']),
                ('/camera/latest', _ah43_camera_latest, ['GET']),
            ]
            existing = set()
            try: existing = {getattr(r, 'path', '') for r in getattr(app, 'routes', [])}
            except Exception: pass
            for path, func, methods in routes:
                if path not in existing and hasattr(app, 'add_api_route'):
                    app.add_api_route(path, func, methods=methods)
            if hasattr(app, 'middleware') and not getattr(app, '_ahootsa_5_0_43_middleware', False):
                setattr(app, '_ahootsa_5_0_43_middleware', True)
                @app.middleware('http')
                async def _ah43_inject_panel(request, call_next):
                    response = await call_next(request)
                    try:
                        ctype = response.headers.get('content-type','')
                        if 'text/html' in ctype.lower():
                            body = b''
                            async for chunk in response.body_iterator: body += chunk
                            text = body.decode('utf-8', errors='replace')
                            if 'ahootsa-5-0-43-panel' not in text:
                                text = text.replace('</body>', _AH43_PANEL_JS + '</body>') if '</body>' in text else text + _AH43_PANEL_JS
                            try:
                                from starlette.responses import HTMLResponse
                            except Exception:
                                from fastapi.responses import HTMLResponse
                            return HTMLResponse(text, status_code=response.status_code, headers=dict(response.headers))
                    except Exception as e:
                        _ah43_log('middleware inject error: ' + repr(e))
                    return response
            _ah43_log('app patched ok')
        except Exception as e:
            _ah43_log('app patch error: ' + repr(e))
        return app

    try:
        import fastapi as _fastapi
        _orig_fastapi_init = _fastapi.FastAPI.__init__
        def _new_fastapi_init(self,*a,**k):
            _orig_fastapi_init(self,*a,**k); _ah43_patch_app(self)
        if not getattr(_fastapi.FastAPI.__init__, '_ahootsa_5_0_43_wrapped', False):
            _new_fastapi_init._ahootsa_5_0_43_wrapped=True; _fastapi.FastAPI.__init__=_new_fastapi_init
    except Exception as e: _ah43_log('fastapi wrap error: '+repr(e))
    try:
        import starlette.applications as _sapp
        _orig_starlette_init = _sapp.Starlette.__init__
        def _new_starlette_init(self,*a,**k):
            _orig_starlette_init(self,*a,**k); _ah43_patch_app(self)
        if not getattr(_sapp.Starlette.__init__, '_ahootsa_5_0_43_wrapped', False):
            _new_starlette_init._ahootsa_5_0_43_wrapped=True; _sapp.Starlette.__init__=_new_starlette_init
    except Exception as e: _ah43_log('starlette wrap error: '+repr(e))
    _ah43_disable_windows_audio(); _ah43_log('bootstrap loaded')
except Exception as _e:
    try: print('AHOOTSA_5_0_43_BOOTSTRAP_ERROR', repr(_e))
    except Exception: pass
# <<< AHOOTSA_5_0_43_AUTONOMA_END
"""

def main() -> int:
    try:
        import ahootsa_realtime_ollama_desktop_app as pkg
    except Exception as e:
        print('[ERROR] No se pudo importar ahootsa_realtime_ollama_desktop_app:', repr(e))
        return 2
    init_path = pathlib.Path(pkg.__file__).resolve()
    print('PACKAGE_INIT=' + str(init_path))
    text = init_path.read_text(encoding='utf-8', errors='ignore')
    # Limpia parches autónomos anteriores para evitar duplicados/conflictos.
    for begin, end in [
        ('# >>> AHOOTSA_5_0_41_AUTONOMA_BEGIN', '# <<< AHOOTSA_5_0_41_AUTONOMA_END'),
        ('# >>> AHOOTSA_5_0_42_AUTONOMA_BEGIN', '# <<< AHOOTSA_5_0_42_AUTONOMA_END'),
        (MARKER_BEGIN, MARKER_END),
    ]:
        if begin in text and end in text:
            text = text.split(begin)[0].rstrip() + '\n' + text.split(end,1)[1].lstrip('\n')
    backup = init_path.with_suffix(init_path.suffix + '.bak_5_0_43_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    shutil.copy2(init_path, backup)
    print('BACKUP=' + str(backup))
    new = BOOTSTRAP.strip() + '\n\n' + text
    init_path.write_text(new, encoding='utf-8')
    print('PATCH_OK=5.0.43')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
