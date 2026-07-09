# -*- coding: utf-8 -*-
"""
Ahootsa 5.0.38 - proveedor LLM dual

Objetivo:
- Recuperar la posibilidad de usar un modelo Hugging Face descargado en local.
- Mantener Ollama como alternativa rápida/fallback.
- Evitar que la interfaz se quede en "preguntando..." sin respuesta.

Variables:
  AHOOTSA_LLM_PROVIDER=auto|hf_local|ollama
  AHOOTSA_HF_MODEL_PATH=D:\RITXI\models\mi_modelo_hf  (o carpeta cache HF local)
  AHOOTSA_OLLAMA_MODEL=llama3.2:3b
  AHOOTSA_OLLAMA_URL=http://127.0.0.1:11434
"""
from __future__ import annotations
import argparse, os, pathlib, json, urllib.request, urllib.error, datetime, re, base64


def log(x): print(x, flush=True)


def package_root(name: str) -> pathlib.Path | None:
    try:
        mod = __import__(name)
        return pathlib.Path(mod.__file__).resolve().parent
    except Exception:
        return None


def replace_in_tree(root: pathlib.Path, pairs: list[tuple[str,str]]) -> list[str]:
    changed=[]
    exts={'.py','.js','.html','.txt','.md','.json','.env','.example'}
    for p in root.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in exts:
            continue
        try:
            txt=p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        new=txt
        for a,b in pairs:
            new=new.replace(a,b)
        if new!=txt:
            try:
                bak=p.with_suffix(p.suffix+'.bak_5_0_38')
                if not bak.exists(): bak.write_text(txt,encoding='utf-8')
            except Exception:
                pass
            try:
                p.write_text(new,encoding='utf-8')
                changed.append(str(p))
            except Exception:
                pass
    return changed

BOOT = r'''
# AHOOTSA_LLM_DUAL_HF_OLLAMA_5_0_38_BEGIN
try:
    import os as _a38_os, pathlib as _a38_pathlib, json as _a38_json, urllib.request as _a38_ureq, urllib.error as _a38_uerr, datetime as _a38_dt, base64 as _a38_b64, re as _a38_re
    _a38_os.environ.setdefault('AHOOTSA_LLM_PROVIDER', 'auto')
    _a38_os.environ.setdefault('AHOOTSA_OLLAMA_URL', 'http://127.0.0.1:11434')
    _a38_os.environ.setdefault('AHOOTSA_OLLAMA_MODEL', 'llama3.2:3b')
    _a38_os.environ.setdefault('OLLAMA_MODEL', _a38_os.environ.get('AHOOTSA_OLLAMA_MODEL','llama3.2:3b'))
    _a38_os.environ.setdefault('AHOOTSA_OLLAMA_TIMEOUT', '18')
    _a38_os.environ.setdefault('AHOOTSA_HF_TIMEOUT', '30')
    _a38_os.environ.setdefault('AHOOTSA_HF_MAX_NEW_TOKENS', '120')
    _a38_os.environ.setdefault('AHOOTSA_HF_TEMPERATURE', '0.5')
    _a38_os.environ.setdefault('AHOOTSA_CAMERA_DIR', r'D:\RITXI\logs\camera')
    _a38_os.environ.setdefault('AHOOTSA_DISABLE_WINDOWS_BEEP', '1')
    _a38_os.environ.setdefault('PYTTSX3_DISABLE', '1')

    try:
        import winsound as _a38_winsound
        _a38_winsound.Beep=lambda *a,**k: None
        _a38_winsound.PlaySound=lambda *a,**k: None
    except Exception: pass
    try:
        import pyttsx3 as _a38_pyttsx3
        class _A38SilentEngine:
            def say(self,*a,**k): return None
            def runAndWait(self,*a,**k): return None
            def stop(self,*a,**k): return None
            def setProperty(self,*a,**k): return None
            def getProperty(self,*a,**k): return None
        _a38_pyttsx3.init=lambda *a,**k: _A38SilentEngine()
    except Exception: pass

    _a38_hf_pipe = None
    _a38_hf_error = None

    def _a38_ollama_json(path, payload=None, timeout=8):
        base=_a38_os.environ.get('AHOOTSA_OLLAMA_URL','http://127.0.0.1:11434').rstrip('/')
        data=None; method='GET'; headers={'Content-Type':'application/json'}
        if payload is not None:
            data=_a38_json.dumps(payload,ensure_ascii=False).encode('utf-8'); method='POST'
        req=_a38_ureq.Request(base+path,data=data,headers=headers,method=method)
        with _a38_ureq.urlopen(req,timeout=timeout) as r:
            raw=r.read().decode('utf-8','replace')
            return _a38_json.loads(raw) if raw else {}

    def _a38_hf_available():
        p=(_a38_os.environ.get('AHOOTSA_HF_MODEL_PATH') or '').strip().strip('"')
        return bool(p) and _a38_pathlib.Path(p).exists()

    def _a38_load_hf():
        global _a38_hf_pipe, _a38_hf_error
        if _a38_hf_pipe is not None: return _a38_hf_pipe
        model_path=(_a38_os.environ.get('AHOOTSA_HF_MODEL_PATH') or '').strip().strip('"')
        if not model_path:
            raise RuntimeError('AHOOTSA_HF_MODEL_PATH no está configurado')
        if not _a38_pathlib.Path(model_path).exists():
            raise RuntimeError('No existe AHOOTSA_HF_MODEL_PATH: '+model_path)
        try:
            from transformers import pipeline
            # local_files_only evita descargas inesperadas. trust_remote_code se permite para modelos HF locales que lo necesiten.
            _a38_hf_pipe = pipeline('text-generation', model=model_path, tokenizer=model_path, local_files_only=True, trust_remote_code=True)
            _a38_hf_error = None
            return _a38_hf_pipe
        except Exception as e:
            _a38_hf_error = repr(e)
            raise

    def _a38_generate_hf(prompt):
        pipe=_a38_load_hf()
        system='Eres Ahootsa, un asistente educativo amable. Responde en castellano claro, natural y breve. Usa frases cortas.'
        full=system+'\nUsuario: '+prompt.strip()+'\nAhootsa:'
        max_new=int(float(_a38_os.environ.get('AHOOTSA_HF_MAX_NEW_TOKENS','120')))
        temp=float(_a38_os.environ.get('AHOOTSA_HF_TEMPERATURE','0.5'))
        out=pipe(full, max_new_tokens=max_new, do_sample=(temp>0), temperature=temp, return_full_text=False)
        txt=''
        if isinstance(out,list) and out:
            txt=out[0].get('generated_text','') if isinstance(out[0],dict) else str(out[0])
        else:
            txt=str(out)
        return txt.strip()

    def _a38_generate_ollama(prompt, model=None):
        m=(model or _a38_os.environ.get('AHOOTSA_OLLAMA_MODEL','llama3.2:3b')).strip()
        body={'model':m,'prompt':'Eres Ahootsa. Responde en castellano claro, breve y natural.\nUsuario: '+prompt.strip()+'\nAhootsa:', 'stream':False, 'options':{'temperature':0.5,'num_predict':140}}
        ans=_a38_ollama_json('/api/generate', body, timeout=float(_a38_os.environ.get('AHOOTSA_OLLAMA_TIMEOUT','18')))
        return (ans.get('response') or '').strip(), m

    def _a38_choose_provider():
        pref=(_a38_os.environ.get('AHOOTSA_LLM_PROVIDER','auto') or 'auto').lower().strip()
        if pref=='hf_local': return 'hf_local'
        if pref=='ollama': return 'ollama'
        if _a38_hf_available(): return 'hf_local'
        return 'ollama'

    async def _a38_llm_status():
        provider=_a38_choose_provider()
        hf_path=(_a38_os.environ.get('AHOOTSA_HF_MODEL_PATH') or '').strip()
        data={'ok':True,'version':'5.0.38','provider':provider,'provider_pref':_a38_os.environ.get('AHOOTSA_LLM_PROVIDER','auto'), 'hf_model_path':hf_path, 'hf_model_exists': bool(hf_path and _a38_pathlib.Path(hf_path).exists()), 'hf_loaded': _a38_hf_pipe is not None, 'hf_error': _a38_hf_error, 'ollama_url': _a38_os.environ.get('AHOOTSA_OLLAMA_URL'), 'ollama_model': _a38_os.environ.get('AHOOTSA_OLLAMA_MODEL')}
        try:
            tags=_a38_ollama_json('/api/tags',timeout=4)
            data['ollama_connected']=True
            data['ollama_models']=[m.get('name') for m in tags.get('models',[]) if isinstance(m,dict)]
        except Exception as e:
            data['ollama_connected']=False; data['ollama_error']=str(e)
        return data

    async def _a38_llm_ask(request):
        try: payload=await request.json()
        except Exception: payload={}
        prompt=(payload.get('prompt') or payload.get('question') or payload.get('text') or '').strip()
        if not prompt: return {'ok':False,'error':'Falta prompt'}
        requested=(payload.get('provider') or _a38_os.environ.get('AHOOTSA_LLM_PROVIDER','auto') or 'auto').lower().strip()
        provider = _a38_choose_provider() if requested=='auto' else requested
        # Primero HF local si se pide o si auto lo detecta. Si falla y está en auto, cae a Ollama.
        if provider=='hf_local':
            try:
                return {'ok':True,'provider':'hf_local','model_path':_a38_os.environ.get('AHOOTSA_HF_MODEL_PATH'), 'response':_a38_generate_hf(prompt)}
            except Exception as e:
                if requested!='auto':
                    return {'ok':False,'provider':'hf_local','error':repr(e),'hint':'Instala transformers/torch en apps_venv o revisa AHOOTSA_HF_MODEL_PATH.'}
                # fallback auto
        try:
            txt,m=_a38_generate_ollama(prompt, payload.get('model'))
            return {'ok':True,'provider':'ollama','model':m,'response':txt}
        except Exception as e:
            return {'ok':False,'provider':'ollama','error':repr(e),'hint':'Si quieres HF local configura -Provider hf_local -HFModelPath "ruta". Si quieres Ollama usa llama3.2:3b.'}

    # Cámara PC: página aislada para evitar cachés del frontend principal.
    async def _a38_camera_health():
        return {'ok':True,'version':'5.0.38','camera_dir':_a38_os.environ.get('AHOOTSA_CAMERA_DIR'), 'note':'La webcam del PC se activa desde navegador con getUserMedia. No usa micrófono.'}
    async def _a38_camera_page():
        from fastapi.responses import HTMLResponse
        return HTMLResponse("""<!doctype html><html><head><meta charset='utf-8'><title>Ahootsa Cámara PC</title><style>body{font-family:system-ui;margin:24px;background:#fafafa}main{max-width:850px;margin:auto;background:white;padding:20px;border-radius:14px;border:1px solid #ddd}button{padding:12px 16px;margin:6px;border-radius:10px;border:1px solid #aaa;background:#fff;cursor:pointer}video,img{max-width:800px;width:100%;background:#eee;border-radius:12px;border:1px solid #ccc}.ok{color:#166534}.err{color:#991b1b}</style></head><body><main><h1>Cámara PC Ahootsa</h1><p>Esta prueba usa la webcam del portátil/PC desde el navegador. No activa el micrófono.</p><video id='v' autoplay playsinline muted></video><canvas id='c' style='display:none'></canvas><img id='img' style='display:none'><p><button id='start'>Activar cámara</button><button id='shot'>Hacer foto</button><button id='stop'>Parar cámara</button></p><pre id='s'>Lista. Pulsa Activar cámara y acepta el permiso.</pre></main><script>let st=null,v=document.getElementById('v'),c=document.getElementById('c'),img=document.getElementById('img'),s=document.getElementById('s');function msg(t,ok=true){s.className=ok?'ok':'err';s.textContent=t;}document.getElementById('start').onclick=async()=>{try{if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){msg('ERROR: getUserMedia no disponible. Prueba Chrome/Edge y http://127.0.0.1:7860/camera/page',false);return}st=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:1280},height:{ideal:720}},audio:false});v.srcObject=st;msg('Cámara activa. Ahora pulsa Hacer foto.');}catch(e){msg('ERROR cámara: '+e.name+' - '+e.message+'\\nRevisa permisos de cámara en Windows y navegador/Desktop Control.',false)}};document.getElementById('shot').onclick=async()=>{try{if(!v.videoWidth){msg('Primero activa la cámara.',false);return}c.width=v.videoWidth;c.height=v.videoHeight;c.getContext('2d').drawImage(v,0,0);let d=c.toDataURL('image/png');img.src=d;img.style.display='block';let r=await fetch('/camera/upload',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image_data:d})});msg(await r.text());}catch(e){msg('ERROR foto/subida: '+e.name+' - '+e.message,false)}};document.getElementById('stop').onclick=()=>{if(st){st.getTracks().forEach(t=>t.stop());st=null;v.srcObject=null;msg('Cámara parada.')}}</script></body></html>""")
    async def _a38_camera_upload(request):
        try: payload=await request.json()
        except Exception: payload={}
        data=payload.get('image_data') or payload.get('image') or ''
        m=_a38_re.match(r'^data:image/(png|jpeg|jpg);base64,(.+)$',data,_a38_re.I|_a38_re.S)
        if not m: return {'ok':False,'error':'Falta image_data dataURL'}
        raw=_a38_b64.b64decode(m.group(2)); ext='jpg' if m.group(1).lower() in ('jpg','jpeg') else 'png'
        d=_a38_pathlib.Path(_a38_os.environ.get('AHOOTSA_CAMERA_DIR',r'D:\RITXI\logs\camera')); d.mkdir(parents=True,exist_ok=True)
        p=d/('ahootsa_camera_'+_a38_dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'.'+ext); p.write_bytes(raw)
        return {'ok':True,'path':str(p),'bytes':len(raw)}

    def _a38_add_routes(app):
        try:
            existing={getattr(r,'path',None) for r in getattr(app,'routes',[])}
            if '/llm/status' not in existing: app.get('/llm/status')(_a38_llm_status)
            if '/llm/ask' not in existing: app.post('/llm/ask')(_a38_llm_ask)
            # compatibilidad con los botones Ollama anteriores
            if '/ollama/status' not in existing: app.get('/ollama/status')(_a38_llm_status)
            if '/ollama/models' not in existing: app.get('/ollama/models')(_a38_llm_status)
            if '/ollama/ask' not in existing: app.post('/ollama/ask')(_a38_llm_ask)
            if '/camera/health' not in existing: app.get('/camera/health')(_a38_camera_health)
            if '/camera/page' not in existing: app.get('/camera/page')(_a38_camera_page)
            if '/camera/upload' not in existing: app.post('/camera/upload')(_a38_camera_upload)
        except Exception: pass

    try:
        import fastapi.applications as _a38_fa
        _old_init=_a38_fa.FastAPI.__init__
        if not getattr(_a38_fa.FastAPI,'_ahootsa_5_0_38_patched',False):
            def _new_init(self,*a,**k):
                _old_init(self,*a,**k); _a38_add_routes(self)
            _a38_fa.FastAPI.__init__=_new_init; _a38_fa.FastAPI._ahootsa_5_0_38_patched=True
    except Exception: pass
except Exception:
    pass
# AHOOTSA_LLM_DUAL_HF_OLLAMA_5_0_38_END
'''


def patch_init(root: pathlib.Path) -> bool:
    init=root/'__init__.py'
    if not init.exists(): init.write_text('', encoding='utf-8')
    txt=init.read_text(encoding='utf-8', errors='ignore')
    if 'AHOOTSA_LLM_DUAL_HF_OLLAMA_5_0_38_BEGIN' in txt:
        return False
    init.write_text(BOOT+'\n'+txt,encoding='utf-8')
    return True


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--ollama-model', default=os.environ.get('AHOOTSA_OLLAMA_MODEL','llama3.2:3b'))
    ap.add_argument('--provider', default=os.environ.get('AHOOTSA_LLM_PROVIDER','auto'))
    ap.add_argument('--hf-model-path', default=os.environ.get('AHOOTSA_HF_MODEL_PATH',''))
    args=ap.parse_args()
    os.environ['AHOOTSA_LLM_PROVIDER']=args.provider
    os.environ['AHOOTSA_OLLAMA_MODEL']=args.ollama_model
    os.environ['OLLAMA_MODEL']=args.ollama_model
    if args.hf_model_path:
        os.environ['AHOOTSA_HF_MODEL_PATH']=args.hf_model_path
    roots=[]
    for name in ['ahootsa_realtime_ollama_desktop_app','reachy_mini_conversation_app','reachy_talk_data']:
        r=package_root(name)
        if r: roots.append((name,r))
    if not roots:
        log('[ERROR] No encuentro paquetes Ahootsa/Reachy en apps_venv')
        return 2
    pairs=[('ahootsa-local:latest', args.ollama_model), ('ahootsa-local', args.ollama_model)]
    for name,r in roots:
        log('[INFO] paquete %s: %s' % (name,r))
        if name=='ahootsa_realtime_ollama_desktop_app':
            changed=patch_init(r)
            log('[OK] bootstrap 5.0.38 %s' % ('insertado' if changed else 'ya existia'))
        modified=replace_in_tree(r,pairs)
        log('[OK] ficheros modificados en %s: %s' % (name,len(modified)))
    diag=pathlib.Path(os.environ.get('AHOOTSA_LOG_ROOT',r'D:\RITXI\logs'))/'ahootsa_5_0_38_llm_config.json'
    diag.parent.mkdir(parents=True,exist_ok=True)
    diag.write_text(json.dumps({'provider':args.provider,'hf_model_path':args.hf_model_path,'ollama_model':args.ollama_model,'ts':datetime.datetime.now().isoformat()},ensure_ascii=False,indent=2),encoding='utf-8')
    log('[OK] config escrita: %s' % diag)
    return 0

if __name__=='__main__':
    raise SystemExit(main())
