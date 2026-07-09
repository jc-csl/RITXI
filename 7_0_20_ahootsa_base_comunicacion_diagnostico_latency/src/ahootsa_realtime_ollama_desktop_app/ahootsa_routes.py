
"""Ahootsa 7.0.20 panel/API routes.

Estas rutas no sustituyen el motor conversacional oficial de Hugging Face
Realtime. Añaden un panel HTML lateral para estado, cámara PC, consulta directa
Ollama y edición controlada de configuración Ahootsa.
"""
from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse

VERSION = "7.0.20"

TEXT_EXTENSIONS = {".txt", ".json", ".md", ".html", ".toml", ".yaml", ".yml", ".ini", ".cfg", ".env"}
VIEW_ONLY_EXTENSIONS = {".py"}
EXCLUDE_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules", ".mypy_cache", ".pytest_cache"}


def _package_root() -> Path:
    return Path(__file__).resolve().parent


def _photos_dir() -> Path:
    d = Path(os.getenv("AHOOTSA_PHOTOS_DIR", r"D:\RITXI\fotos"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _config_backup_dir() -> Path:
    d = Path(os.getenv("AHOOTSA_CONFIG_BACKUP_DIR", r"D:\RITXI\logs\config_backups"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _ollama_base() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")


def _ollama_model() -> str:
    return os.getenv("OLLAMA_MODEL", "llama3.2:3b").strip() or "llama3.2:3b"


def _vision_model() -> str:
    return os.getenv("OLLAMA_VISION_MODEL", "llava:latest").strip() or "llava:latest"



def _load_tool_module(module_name: str):
    """Carga un módulo de tools Ahootsa sin depender de paquetes oficiales."""
    path = _package_root() / "tools" / f"{module_name}.py"
    if not path.exists():
        raise FileNotFoundError(str(path))
    import sys as _sys
    mod_name = f"ahootsa_shared_tool_{module_name}"
    if mod_name in _sys.modules:
        return _sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"No se puede cargar {path}")
    mod = importlib.util.module_from_spec(spec)
    _sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _capture_pc_with_opencv(camera_index: int = 0, warmup_frames: int = 2) -> dict[str, Any]:
    """Captura foto desde la webcam del PC mediante OpenCV; no usa cámara MuJoCo."""
    try:
        mod = _load_tool_module("camera_pc")
        result = mod._capture_with_cv2(int(camera_index), int(warmup_frames))
        if result.get("ok") and result.get("image_path"):
            p = Path(str(result["image_path"]))
            # Normalizar nombres de foto para que el panel detecte todas.
            result["source"] = "pc_webcam_opencv"
            result["photos_dir"] = str(_photos_dir())
            result["message_for_user"] = "Foto realizada con la cámara del PC y guardada en D:\\RITXI\\fotos."
        return result
    except Exception as exc:
        return {
            "ok": False,
            "source": "pc_webcam_opencv",
            "error": f"{type(exc).__name__}: {exc}",
            "message_for_user": "No he podido abrir la cámara del PC. Revisa permisos de cámara de Windows y que no esté usada por otra aplicación.",
        }


def _memory_mod():
    return _load_tool_module("memory_pairs_game_server")


def _memory_status_payload() -> dict[str, Any]:
    try:
        mod = _memory_mod()
        st = mod.status()
        if not st.get("state", {}).get("cards"):
            mod.reset_game("animales")
            st = mod.status()
        return st
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "message_for_user": "No he podido cargar el juego de parejas integrado."}


def _memory_page_html(game_id: str = "animales", reset: bool = False) -> str:
    safe_game = (game_id or "animales").replace("<", "").replace(">", "")
    reset_js = "true" if reset else "false"
    return f"""<!doctype html>
<html lang='es'><head><meta charset='utf-8'/><meta name='viewport' content='width=device-width,initial-scale=1'/>
<title>Ahootsa - juego de parejas</title>
<style>
body{{margin:0;background:#eef2f7;font-family:Arial,sans-serif;color:#17213a}}
.header{{padding:8px 12px;background:#17213a;color:white;display:flex;gap:8px;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:5}}
.header b{{color:#ff2fa6}} select,button{{border:0;border-radius:10px;padding:8px 10px;margin:2px}}
button{{background:#ff2fa6;color:white;cursor:pointer}} select{{background:white;color:#17213a}}
.board{{padding:12px;display:grid;grid-template-columns:repeat(2,1fr);gap:12px;max-width:720px;margin:0 auto}}
.card{{height:132px;border:0;border-radius:18px;background:linear-gradient(180deg,#1763c8,#0f4d9f);color:white;font-size:60px;font-weight:900;box-shadow:0 10px 22px #0002;cursor:pointer}}
.card.open,.card.matched{{background:linear-gradient(180deg,#ffe8a9,#ffd47a);color:#17213a;font-size:21px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:7px;padding:8px;text-align:center}}
.card{{position:relative}}
.card.selected{{outline:6px solid #ff2fa6;outline-offset:-6px;box-shadow:0 0 0 5px rgba(255,47,166,.22),0 12px 26px #0003;transform:translateY(-2px)}}
.card.selected::after{{content:'seleccionada';position:absolute;left:8px;right:8px;bottom:8px;background:white;color:#ff2fa6;border-radius:999px;font-size:13px;padding:3px;font-weight:900;text-transform:uppercase}}
.card .ico{{font-size:50px;line-height:1}} .kind{{font-size:11px;text-transform:uppercase;color:#5b6475;font-weight:800;letter-spacing:.08em}}
.msg{{text-align:center;font-size:20px;font-weight:800;padding:8px}} .small{{font-size:12px;color:#d7dbea}}
@media(min-width:900px){{.board{{grid-template-columns:repeat(4,1fr);max-width:980px}}.card{{height:150px}}}}
@media(max-width:520px){{.board{{gap:9px;padding:9px}}.card{{height:112px;font-size:50px}}.card .ico{{font-size:42px}}}}
</style></head><body>
<div class='header'><div><b>Ahootsa</b> · Juego de parejas integrado</div><div><select id='game'></select><button onclick='resetGame()'>Reiniciar</button><button onclick='refresh()'>Actualizar</button></div></div>
<div id='msg' class='msg'>Cargando...</div><main id='board' class='board'></main>
<script>
let selected=[];
async function j(path, opts){{const r=await fetch(path, opts||{{cache:'no-store'}}); if(!r.ok) throw new Error(await r.text()); return await r.json();}}
async function loadGames(){{const data=await j('/memory/games'); const sel=document.getElementById('game'); sel.innerHTML=''; (data.games||[]).forEach(g=>{{const o=document.createElement('option');o.value=g.id;o.textContent=g.title||g.id; sel.appendChild(o);}}); sel.value='{safe_game}';}}
function cardHtml(c){{const isSel=selected.includes(c.number); const open=c.visible||c.matched||isSel; const cls=(open?'card open'+(c.matched?' matched':'')+(isSel?' selected':''):'card'); const icon=open?(c.icon||c.peek_icon||''):''; const label=open?(c.label||c.peek_label||''):''; const kind=open?(c.kind_label||c.peek_kind_label||''):''; return `<button class="${{cls}}" onclick="pick(${{c.number}})" ${{c.matched?'disabled':''}}>${{open?`<div class="ico">${{icon}}</div><div>${{label}}</div><div class="kind">${{kind}}</div>`:c.number}}</button>`;}}
let refreshMs=900;
async function refresh(){{try{{const data=await j('/memory/state'); const st=data.state||data; refreshMs=st.refresh_interval_ms||900; document.getElementById('msg').textContent=st.message||'Elige dos números.'; document.getElementById('board').innerHTML=(st.cards||[]).map(cardHtml).join('');}}catch(e){{document.getElementById('msg').textContent='No se pudo cargar el juego: '+e;}}}}
async function resetGame(){{selected=[]; const gid=document.getElementById('game').value||'{safe_game}'; await j('/memory/reset?game_id='+encodeURIComponent(gid)); await refresh();}}
async function pick(n){{if(selected.includes(n)){{selected=selected.filter(x=>x!==n);document.getElementById('msg').textContent='Has quitado la carta '+n+'. Elige dos números.';await refresh();return;}} selected.push(n); if(selected.length<2){{document.getElementById('msg').textContent='Has elegido la carta '+n+'. Elige otra carta.';await refresh();return;}} const a=selected[0],b=selected[1]; selected=[]; const res=await j('/memory/choose?first='+a+'&second='+b); const st=res.state||res; document.getElementById('msg').textContent=res.message_for_user||st.message||'Resultado actualizado.'; await refresh();}}
(async()=>{{await loadGames(); if({reset_js}) await resetGame(); else await refresh(); setInterval(()=>refresh(), Math.max(500, refreshMs||900));}})();
</script></body></html>"""

def _http_json(url: str, payload: dict[str, Any] | None = None, timeout: float = 20.0) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8")
    return json.loads(raw) if raw else {}


def _ollama_tags() -> dict[str, Any]:
    try:
        data = _http_json(f"{_ollama_base()}/api/tags", timeout=4)
        names = [m.get("name") for m in data.get("models", []) if isinstance(m, dict)]
        return {"ok": True, "models": names, "base_url": _ollama_base(), "model": _ollama_model(), "vision_model": _vision_model()}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "base_url": _ollama_base(), "model": _ollama_model(), "vision_model": _vision_model()}


def _latest_photo() -> Path | None:
    files = list(_photos_dir().glob("ahootsa_pc_*.jpg")) + list(_photos_dir().glob("camera_pc_*.jpg"))
    files = sorted([p for p in files if p.is_file()], key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def _file_id(path: Path) -> str:
    return hashlib.sha1(str(path.resolve()).lower().encode("utf-8", errors="ignore")).hexdigest()[:16]


def _safe_read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except Exception:
        return path.name


def _iter_text_files(root: Path, category: str, editable: bool, origin: str, include_py: bool = False) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if not root.exists():
        return items
    for f in sorted(root.rglob("*")):
        if not f.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in f.parts):
            continue
        suffix = f.suffix.lower()
        if suffix not in TEXT_EXTENSIONS and not (include_py and suffix in VIEW_ONLY_EXTENSIONS):
            continue
        can_save = editable and suffix in TEXT_EXTENSIONS
        rid = _file_id(f)
        label = f"{category} / {_rel(f, root)}"
        items.append({
            "id": rid,
            "label": label,
            "category": category,
            "origin": origin,
            "path": str(f),
            "relative_path": _rel(f, root),
            "extension": suffix,
            "can_save": can_save,
            "can_open_notepad": True,
            "requires_restart": _requires_restart(f),
            "size_bytes": f.stat().st_size if f.exists() else 0,
            "mtime": datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec="seconds") if f.exists() else None,
        })
    return items


def _requires_restart(path: Path) -> bool:
    name = path.name.lower()
    parts = {p.lower() for p in path.parts}
    if name in {"instructions.txt", "tools.txt", "voice.txt", "greeting.txt"}:
        return True
    if "profiles" in parts:
        return True
    if path.suffix.lower() == ".py":
        return True
    return False


def _official_roots() -> list[tuple[str, Path]]:
    roots: list[tuple[str, Path]] = []
    for mod_name in ("reachy_mini_conversation_app", "reachy_talk_data"):
        try:
            mod = __import__(mod_name)
            root = Path(mod.__file__).resolve().parent
            for candidate in (root / "profiles", root / "external_content", root / "external_tools"):
                if candidate.exists():
                    roots.append((f"Oficial {mod_name} / {candidate.name}", candidate))
        except Exception:
            continue
    return roots


def _config_inventory() -> list[dict[str, Any]]:
    root = _package_root()
    items: list[dict[str, Any]] = []

    # Ahootsa editable: configuración externa propia. No toca el núcleo oficial.
    items += _iter_text_files(root / "profiles", "Ahootsa perfiles", True, "ahootsa")
    items += _iter_text_files(root / "tools", "Ahootsa tools y actividades", True, "ahootsa", include_py=True)

    # Archivos puntuales de paquete que sí afectan al comportamiento del panel/logs.
    for f in [root / "logging_config.json"]:
        if f.exists():
            items += _iter_text_files(f.parent, "Ahootsa configuración interna", True, "ahootsa")
            break

    # Oficial: lectura y apertura en Bloc de notas, pero no guardado desde panel para respetar que el núcleo es intocable.
    for label, path in _official_roots():
        items += _iter_text_files(path, label, False, "oficial", include_py=False)

    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in items:
        if item["id"] in seen:
            continue
        seen.add(item["id"])
        unique.append(item)
    unique.sort(key=lambda x: (x["origin"], x["category"], x["relative_path"]))
    return unique


def _get_config_item(file_id: str) -> dict[str, Any] | None:
    for item in _config_inventory():
        if item["id"] == file_id:
            return item
    return None


def _backup_file(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re_safe_filename(str(path).replace(":", ""))
    backup = _config_backup_dir() / f"{safe_name}.{stamp}.bak"
    backup.write_text(_safe_read_text(path), encoding="utf-8")
    return backup


def re_safe_filename(value: str) -> str:
    return "".join(c if c.isalnum() or c in {".", "_", "-"} else "_" for c in value)[-180:]


def _config_note_for(item: dict[str, Any]) -> str:
    if item.get("origin") == "oficial":
        return "Archivo de la app oficial. Se muestra para consulta y apertura manual, pero el panel no lo guarda para no modificar el núcleo oficial."
    if item.get("requires_restart"):
        return "Este archivo afecta al perfil/sesión. Guarda y reinicia Ahootsa para que la sesión Hugging Face cargue el cambio."
    return "Este archivo suele aplicarse en la siguiente llamada de la herramienta. Algunos cambios pueden requerir reiniciar la actividad."


def _html() -> str:
    photos_dir = str(_photos_dir()).replace("\\", "\\\\")
    return f"""<!doctype html>
<html lang='es'><head><meta charset='utf-8'/><meta name='viewport' content='width=device-width, initial-scale=1'/>
<title>Ahootsa 7.0.20</title>
<style>
:root{{--navy:#17213a;--pink:#ff2fa6;--line:#d7dbea;--bg:#f6f7fb;--ok:#118a42;--bad:#b3261e}}
body{{margin:0;font-family:Arial,sans-serif;background:var(--bg);color:var(--navy)}}
.header{{display:flex;align-items:center;gap:16px;padding:12px 16px;background:var(--navy);color:white}}
.header b{{color:var(--pink)}}
.layout{{display:grid;grid-template-columns:minmax(0,1fr) 460px;height:calc(100vh - 56px)}}
iframe{{width:100%;height:100%;border:0;background:white}}
.panel{{border-left:1px solid var(--line);background:white;padding:14px;overflow:auto}}
.card{{border:1px solid var(--line);border-radius:14px;padding:12px;margin-bottom:12px;background:#fff;box-shadow:0 1px 6px rgba(0,0,0,.05)}}
h3{{margin:0 0 8px 0;color:var(--pink);letter-spacing:.02em}}
button{{border:0;border-radius:10px;padding:9px 11px;background:var(--navy);color:white;cursor:pointer;margin:4px 4px 4px 0}}
button.secondary{{background:var(--pink)}} button.light{{background:#eef1f8;color:var(--navy)}}
textarea{{width:100%;box-sizing:border-box;min-height:92px;border:1px solid #c9ccda;border-radius:10px;padding:10px}}
#configText{{min-height:280px;font-family:Consolas,monospace;font-size:12px}}
select,input{{width:100%;box-sizing:border-box;border:1px solid #c9ccda;border-radius:10px;padding:9px;margin:4px 0}}
pre{{white-space:pre-wrap;background:#f1f3f8;padding:10px;border-radius:10px;max-height:260px;overflow:auto}}
.small{{font-size:12px;color:#5d667c}}.pill{{display:inline-block;border-radius:999px;padding:3px 8px;margin:2px;background:#eef1f8;font-size:12px}}
.ok{{color:var(--ok)}}.bad{{color:var(--bad)}} code{{font-size:12px}} a{{color:var(--pink)}}
video{{width:100%;border-radius:12px;background:#111}} canvas{{display:none}}
.warn{{background:#fff6e0;border:1px solid #ffd37a;border-radius:10px;padding:8px;margin:6px 0}}
</style></head><body>
<div class='header'><strong>Ahootsa <b>7.0.20</b></strong><span>Conversación principal: Hugging Face Realtime oficial · Ollama auxiliar: {_ollama_model()}</span></div>
<div class='layout'><iframe src='/' title='Conversación principal Reachy/Ahootsa'></iframe><aside class='panel'>
<div class='card'><h3>ESTADO GENERAL</h3>
<div><span class='pill'>Micro voz principal: <b>habilitado</b></span></div>
<div><span class='pill'>Salida audio HF: <b id='voice'>Sohee</b></span></div>
<div><span class='pill'>Audio emociones: <b id='emo'>pygame activo</b></span></div>
<div><span class='pill'>HF modo: <b id='hf'>comprobando...</b></span></div>
<div><span class='pill'>Ollama: <b id='ol'>comprobando...</b></span></div>
<div class='small'>Fotos PC: <code>{photos_dir}</code></div>
<button onclick='status()'>Actualizar estado</button>
<a href='/ahootsa/status' target='_blank'>JSON</a>
</div>
<div class='card'><h3>CONFIGURACIÓN DEL SISTEMA</h3><p class='small'>Acceso rápido a perfiles, tools.txt, instrucciones, actividades, juegos y catálogos. La app oficial se muestra como consulta protegida; Ahootsa es la capa editable.</p>
<input id='configFilter' placeholder='Filtrar: perfil, memory_timing, tools, animales...' oninput='fillConfigSelect()'/>
<select id='configSelect' onchange='loadConfigFile()'></select>
<div id='configMeta' class='small'></div>
<div id='configWarn' class='warn small'></div>
<textarea id='configText' spellcheck='false' placeholder='Selecciona un archivo de configuración...'></textarea>
<button class='secondary' onclick='saveConfigFile()'>Guardar</button><button onclick='openConfigNotepad()'>Abrir en Bloc de notas</button><button class='light' onclick='applyConfig()'>Aplicar / recordar cambios</button>
<pre id='configOut'></pre></div>
<div class='card'><h3>CHAT TEXTO OLLAMA</h3><p class='small'>Consulta directa a Ollama. No interfiere con el control por voz ni sustituye Hugging Face.</p>
<textarea id='prompt' placeholder='Escribe una pregunta para la IA local...'></textarea>
<button class='secondary' onclick='ask()'>Preguntar a Ollama</button><pre id='answer'></pre></div>
<div class='card'><h3>CÁMARA PC</h3><p class='small'>Usa la webcam del ordenador. No activa el micrófono. La cámara oficial del robot/MuJoCo sigue siendo la herramienta camera.</p>
<video id='video' autoplay playsinline muted></video><canvas id='canvas'></canvas><br/>
<button onclick='startCam()'>Activar cámara PC en navegador</button><button class='secondary' onclick='takePhoto()'>Hacer foto navegador</button><button onclick='capturePcServer()'>Foto PC directa OpenCV</button><button onclick='analyzeLatest()'>Analizar última foto PC</button>
<pre id='camout'></pre></div>
<div class='card'><h3>JUEGO DE PAREJAS</h3><p class='small'>Versión integrada en el mismo puerto 7860. Las cartas se muestran en este iframe; al elegir dos números se ve directamente la imagen y la respuesta oral solo indica acierto o fallo.</p>
<select id='memoryGame'><option value='animales'>Animales</option><option value='ciudades'>Ciudades</option><option value='alimentos'>Alimentos</option></select>
<button class='secondary' onclick='openMemory(true)'>Abrir / reiniciar juego</button><button onclick='reloadMemory()'>Actualizar juego</button>
<iframe id='memoryFrame' src='/memory/page?game_id=animales' style='width:100%;height:700px;border:1px solid #d7dbea;border-radius:12px;background:#eef2f7'></iframe><div class='small'>El juego queda cargado aquí. Si se ve pequeño, usa pantalla grande; el iframe mantiene el mismo estado.</div><div class='small'><a id='memoryBigLink' href='/memory/page?game_id=animales' target='_blank'>Abrir juego en pantalla grande</a></div>
</div>
<div class='card'><h3>COMUNICACIÓN · DIAGNÓSTICO DE LATENCIA</h3><p class='small'>Estas pruebas lanzan actividades locales sin pasar por Ollama. Sirven para saber si la espera viene del ciclo de voz/Hugging Face o de la herramienta local.</p>
<select id='commLevel'><option value='facil'>Fácil</option><option value='normal'>Intermedia</option><option value='avanzada'>Avanzada</option></select>
<input id='commActivity' value='1' placeholder='Número o nombre de actividad'/>
<button onclick='commLevels()'>Niveles</button><button onclick='commList()'>Listar actividades</button><button class='secondary' onclick='commStart()'>Iniciar actividad</button><button class='light' onclick='commDiagnose()'>Diagnóstico completo</button>
<pre id='commOut'></pre><div class='small'>Si aquí responde en menos de 1 segundo pero por voz tarda mucho, el cuello de botella está antes de la herramienta: escucha, transcripción, decisión HF o respuesta hablada.</div></div>
<div class='card'><h3>ACTIVIDADES</h3><p class='small'>Comunicación, juego de parejas, emociones con audio, bailes y reproducción de librería de emociones.</p><p class='small'>Diagnóstico rápido de alias: comprueba si Ahootsa entiende el nombre antes de pedirlo por voz.</p><input id='activityAlias' value='baile dos'/><button onclick='resolveActivity()'>Comprobar alias</button><button class='secondary' onclick='playActivity()'>Probar desde panel</button><button onclick='listActivities()'>Listar recursos</button><br/><button class='light' onclick="quickActivity('baile uno')">Baile 1</button><button class='light' onclick="quickActivity('baile dos')">Baile 2</button><button class='light' onclick="quickActivity('baile tres')">Baile 3</button><button class='light' onclick="quickActivity('saludo')">Saludo</button><pre id='activityOut'></pre></div>
</aside></div>
<script>
let CONFIG_ITEMS=[];
async function status(){{try{{const r=await fetch('/ahootsa/status');const j=await r.json();
document.getElementById('hf').textContent=j.hf.mode+(j.hf.ws_url?' local':' deployed');
document.getElementById('ol').textContent=j.ollama.ok?'OK':'NO';document.getElementById('ol').className=j.ollama.ok?'ok':'bad';
document.getElementById('voice').textContent=j.audio.voice;document.getElementById('emo').textContent=j.audio.emotion_audio_enabled?'pygame activo':'desactivado';
}}catch(e){{document.getElementById('ol').textContent='error';}}}}
async function ask(){{const el=document.getElementById('answer');el.textContent='Consultando Ollama local...';try{{const r=await fetch('/ollama/ask',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{prompt:document.getElementById('prompt').value}})}});const j=await r.json();el.textContent=j.reply||j.message_for_user||JSON.stringify(j,null,2);}}catch(e){{el.textContent='Error: '+e;}}}}
async function startCam(){{const out=document.getElementById('camout');try{{const stream=await navigator.mediaDevices.getUserMedia({{video:{{width:960,height:540}},audio:false}});document.getElementById('video').srcObject=stream;out.textContent='Cámara PC activa. El micrófono no se ha solicitado.';}}catch(e){{out.textContent='No se ha podido activar la cámara: '+e;}}}}
async function takePhoto(){{const v=document.getElementById('video'), c=document.getElementById('canvas'), out=document.getElementById('camout'); if(!v.srcObject){{out.textContent='Activa primero la cámara.';return;}} c.width=v.videoWidth||960;c.height=v.videoHeight||540; c.getContext('2d').drawImage(v,0,0,c.width,c.height); const img=c.toDataURL('image/jpeg',0.9); out.textContent='Guardando foto...'; try{{const r=await fetch('/camera_pc/upload',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{image:img}})}}); const j=await r.json(); out.textContent=JSON.stringify(j,null,2);}}catch(e){{out.textContent='Error guardando foto: '+e;}}}}
async function capturePcServer(){{const out=document.getElementById('camout');out.textContent='Intentando foto directa con OpenCV...';try{{const r=await fetch('/camera_pc/capture',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{camera_index:0,warmup_frames:2}})}});const j=await r.json();out.textContent=JSON.stringify(j,null,2);}}catch(e){{out.textContent='Error captura OpenCV: '+e;}}}}
async function analyzeLatest(){{const out=document.getElementById('camout');out.textContent='Analizando última foto...';try{{const r=await fetch('/camera_pc/analyze_latest',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{question:'Describe la imagen en castellano sencillo.'}})}}); const j=await r.json(); out.textContent=j.reply||j.message_for_user||JSON.stringify(j,null,2);}}catch(e){{out.textContent='Error al analizar: '+e;}}}}
function currentMemoryUrl(reset){{const gid=document.getElementById('memoryGame').value||'animales';return '/memory/page?game_id='+encodeURIComponent(gid)+(reset?'&reset=1':'');}}
function syncMemoryLinks(){{const url=currentMemoryUrl(false);const big=document.getElementById('memoryBigLink');if(big)big.href=url;}}
function openMemory(reset){{syncMemoryLinks();document.getElementById('memoryFrame').src=currentMemoryUrl(!!reset);}}
function reloadMemory(){{openMemory(false);}}
async function loadConfigList(){{try{{const r=await fetch('/config/list');const j=await r.json();CONFIG_ITEMS=j.files||[];fillConfigSelect();}}catch(e){{document.getElementById('configOut').textContent='Error cargando lista: '+e;}}}}
function fillConfigSelect(){{const sel=document.getElementById('configSelect');const filter=(document.getElementById('configFilter').value||'').toLowerCase();sel.innerHTML='';CONFIG_ITEMS.filter(x=>(x.label+' '+x.path+' '+x.category).toLowerCase().includes(filter)).forEach(x=>{{const o=document.createElement('option');o.value=x.id;o.textContent=(x.can_save?'✎ ':'🔒 ')+x.label;sel.appendChild(o);}}); if(sel.options.length && !document.getElementById('configText').value) loadConfigFile();}}
async function loadConfigFile(){{const id=document.getElementById('configSelect').value;if(!id)return;const r=await fetch('/config/file?id='+encodeURIComponent(id));const j=await r.json();document.getElementById('configText').value=j.content||'';document.getElementById('configMeta').innerHTML='<b>'+j.label+'</b><br/><code>'+j.path+'</code><br/>editable: '+j.can_save+' · requiere reinicio: '+j.requires_restart;document.getElementById('configWarn').textContent=j.note||'';document.getElementById('configOut').textContent='';}}
async function saveConfigFile(){{const id=document.getElementById('configSelect').value;if(!id)return;const r=await fetch('/config/file',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{id:id,content:document.getElementById('configText').value}})}});const j=await r.json();document.getElementById('configOut').textContent=JSON.stringify(j,null,2);if(j.ok) await loadConfigList();}}
async function openConfigNotepad(){{const id=document.getElementById('configSelect').value;if(!id)return;const r=await fetch('/config/open',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{id:id}})}});const j=await r.json();document.getElementById('configOut').textContent=JSON.stringify(j,null,2);}}
async function applyConfig(){{const r=await fetch('/config/apply',{{method:'POST'}});const j=await r.json();document.getElementById('configOut').textContent=JSON.stringify(j,null,2);}}

async function commLevels(){{const out=document.getElementById('commOut');out.textContent='Consultando niveles locales...';try{{const t0=performance.now();const r=await fetch('/communication/levels');const j=await r.json();j.panel_elapsed_ms=Math.round(performance.now()-t0);out.textContent=JSON.stringify(j,null,2);}}catch(e){{out.textContent='Error: '+e;}}}}
async function commList(){{const out=document.getElementById('commOut');const level=document.getElementById('commLevel').value||'facil';out.textContent='Listando actividades locales...';try{{const t0=performance.now();const r=await fetch('/communication/activities?level='+encodeURIComponent(level)+'&limit=6');const j=await r.json();j.panel_elapsed_ms=Math.round(performance.now()-t0);out.textContent=JSON.stringify(j,null,2);}}catch(e){{out.textContent='Error: '+e;}}}}
async function commStart(){{const out=document.getElementById('commOut');const level=document.getElementById('commLevel').value||'facil';const activity=document.getElementById('commActivity').value||'1';out.textContent='Iniciando actividad local...';try{{const t0=performance.now();const r=await fetch('/communication/start?level='+encodeURIComponent(level)+'&activity='+encodeURIComponent(activity));const j=await r.json();j.panel_elapsed_ms=Math.round(performance.now()-t0);out.textContent=JSON.stringify(j,null,2);}}catch(e){{out.textContent='Error: '+e;}}}}
async function commDiagnose(){{const out=document.getElementById('commOut');const level=document.getElementById('commLevel').value||'facil';const activity=document.getElementById('commActivity').value||'1';out.textContent='Ejecutando diagnóstico de comunicación...';try{{const t0=performance.now();const r=await fetch('/communication/diagnose?level='+encodeURIComponent(level)+'&activity='+encodeURIComponent(activity));const j=await r.json();j.panel_elapsed_ms=Math.round(performance.now()-t0);out.textContent=JSON.stringify(j,null,2);}}catch(e){{out.textContent='Error: '+e;}}}}

async function resolveActivity(){{const out=document.getElementById('activityOut');const v=document.getElementById('activityAlias').value||'baile dos';out.textContent='Comprobando...';try{{const r=await fetch('/ahootsa/resolve_activity?activity='+encodeURIComponent(v));const j=await r.json();out.textContent=JSON.stringify(j,null,2);}}catch(e){{out.textContent='Error: '+e;}}}}
function quickActivity(v){{document.getElementById('activityAlias').value=v;resolveActivity();}}
async function playActivity(){{const out=document.getElementById('activityOut');const v=document.getElementById('activityAlias').value||'baile dos';out.textContent='Probando reproducción desde panel...';try{{const r=await fetch('/ahootsa/play_activity?activity='+encodeURIComponent(v)+'&sound=true',{{method:'POST'}});const j=await r.json();out.textContent=JSON.stringify(j,null,2);}}catch(e){{out.textContent='Error: '+e;}}}}
async function listActivities(){{const out=document.getElementById('activityOut');out.textContent='Listando recursos...';try{{const r=await fetch('/ahootsa/list_activities');const j=await r.json();out.textContent=JSON.stringify(j,null,2);}}catch(e){{out.textContent='Error: '+e;}}}}
status();loadConfigList();syncMemoryLinks();
</script></body></html>"""



def _load_profile_play_emotion_module():
    """Load profile-local play_emotion.py to resolve Spanish aliases without creating tools/play_emotion.py collisions."""
    root = _package_root()
    profile = (os.getenv("AHOOTSA_PROFILE") or os.getenv("REACHY_MINI_PROFILE") or "ahootsa7_realtime_es").strip() or "ahootsa7_realtime_es"
    candidates = [
        root / "profiles" / profile / "play_emotion.py",
        root / "profiles" / "ahootsa7_realtime_es" / "play_emotion.py",
        root / "profiles" / "ahootsa7_actividades" / "play_emotion.py",
    ]
    for path in candidates:
        if path.exists():
            mod_name = f"ahootsa_route_play_emotion_{profile}_{int(path.stat().st_mtime_ns)}"
            if mod_name in sys.modules:
                return sys.modules[mod_name]
            spec = importlib.util.spec_from_file_location(mod_name, path)
            if not spec or not spec.loader:
                continue
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod
    raise FileNotFoundError("No se encuentra play_emotion.py en los perfiles Ahootsa")


def _resolve_activity_payload(activity: str) -> dict[str, Any]:
    try:
        mod = _load_profile_play_emotion_module()
        resolved = mod.resolve_emotion_name(activity) if hasattr(mod, "resolve_emotion_name") else None
        display = mod.display_name_for_move(resolved) if resolved and hasattr(mod, "display_name_for_move") else resolved
        examples = mod.available_examples_es() if hasattr(mod, "available_examples_es") else []
        moves = mod.list_moves() if hasattr(mod, "list_moves") else []
        return {
            "ok": bool(resolved),
            "requested": activity,
            "resolved": resolved,
            "display_name_es": display,
            "available": bool(resolved and resolved in set(moves)),
            "examples": examples,
            "main_moves_available": {"dance1": "dance1" in moves, "dance2": "dance2" in moves, "dance3": "dance3" in moves, "welcoming2": "welcoming2" in moves, "electric1": "electric1" in moves},
            "message_for_user": (f"{activity} se reconoce como {display} ({resolved})." if resolved else "No he reconocido ese baile o emoción."),
        }
    except Exception as exc:
        return {"ok": False, "requested": activity, "error": f"{type(exc).__name__}: {exc}", "message_for_user": "No he podido comprobar ese alias."}



def _communication_tool_module(name: str):
    return _load_tool_module(name)


async def _call_communication_tool(module_name: str, class_name: str, **kwargs: Any) -> dict[str, Any]:
    start = datetime.now()
    mod = _communication_tool_module(module_name)
    cls = getattr(mod, class_name)
    tool = cls()
    result = await tool(None, **kwargs)  # communication tools do not use ToolDependencies
    if not isinstance(result, dict):
        result = {"ok": True, "raw": result}
    elapsed = int((datetime.now() - start).total_seconds() * 1000)
    result.setdefault("route_duration_ms", elapsed)
    result.setdefault("called_from", "ahootsa_panel_endpoint")
    result.setdefault("uses_ollama", False)
    result.setdefault("hf_voice_pipeline", False)
    return result


def _camera_html() -> str:
    return """<!doctype html><html lang='es'><head><meta charset='utf-8'/><meta name='viewport' content='width=device-width, initial-scale=1'/><title>Cámara PC Ahootsa</title><style>body{font-family:Arial;margin:20px;background:#f6f7fb;color:#17213a}button{border:0;border-radius:10px;padding:10px 12px;background:#17213a;color:white;margin:4px}button.p{background:#ff2fa6}video{max-width:900px;width:100%;border-radius:14px;background:#111}pre{background:white;padding:12px;border-radius:10px;white-space:pre-wrap}</style></head><body><h1>Cámara PC Ahootsa</h1><p>No se solicita audio. Las fotos se guardan en D:\\RITXI\\fotos.</p><video id='video' autoplay playsinline muted></video><canvas id='canvas' style='display:none'></canvas><br/><button onclick='startCam()'>Activar cámara navegador</button><button class='p' onclick='takePhoto()'>Hacer foto navegador</button><button onclick='captureDirect()'>Foto PC directa OpenCV</button><button onclick='analyzeLatest()'>Analizar última foto PC</button><pre id='out'></pre><script>async function startCam(){try{video.srcObject=await navigator.mediaDevices.getUserMedia({video:{width:960,height:540},audio:false});out.textContent='Cámara activa.';}catch(e){out.textContent='Error cámara: '+e;}}async function takePhoto(){if(!video.srcObject){out.textContent='Activa primero la cámara.';return;}canvas.width=video.videoWidth||960;canvas.height=video.videoHeight||540;canvas.getContext('2d').drawImage(video,0,0,canvas.width,canvas.height);const img=canvas.toDataURL('image/jpeg',0.9);const r=await fetch('/camera_pc/upload',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image:img})});out.textContent=JSON.stringify(await r.json(),null,2);}async function capturePcServer(){{const out=document.getElementById('camout');out.textContent='Intentando foto directa con OpenCV...';try{{const r=await fetch('/camera_pc/capture',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{camera_index:0,warmup_frames:2}})}});const j=await r.json();out.textContent=JSON.stringify(j,null,2);}}catch(e){{out.textContent='Error captura OpenCV: '+e;}}}}
async function captureDirect(){out.textContent='Intentando foto directa con OpenCV...';const r=await fetch('/camera_pc/capture',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({camera_index:0,warmup_frames:2})});out.textContent=JSON.stringify(await r.json(),null,2);}async function analyzeLatest(){out.textContent='Analizando...';const r=await fetch('/camera_pc/analyze_latest',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:'Describe la imagen en castellano sencillo.'})});const j=await r.json();out.textContent=j.reply||j.message_for_user||JSON.stringify(j,null,2);}</script></body></html>"""


def mount_ahootsa_routes(app: Any, reachy_mini: Any | None = None) -> None:
    if getattr(app, "_ahootsa_7_routes_mounted", False):
        return
    setattr(app, "_ahootsa_7_routes_mounted", True)
    direct_robot = reachy_mini

    @app.get("/ahootsa")
    def _panel() -> HTMLResponse:
        return HTMLResponse(_html())

    @app.get("/ahootsa/status")
    def _status() -> JSONResponse:
        latest = _latest_photo()
        return JSONResponse({
            "ok": True,
            "version": VERSION,
            "app": "ahootsa_realtime_ollama_app",
            "hf": {"mode": os.getenv("HF_REALTIME_CONNECTION_MODE", "deployed"), "ws_url": os.getenv("HF_REALTIME_WS_URL", "")},
            "ollama": _ollama_tags(),
            "audio": {
                "voice": os.getenv("VOICE", "Sohee"),
                "realtime_voice": os.getenv("REALTIME_VOICE", "Sohee"),
                "emotion_audio_enabled": os.getenv("AHOOTSA_DISABLE_EMOTION_AUDIO", "0").lower() not in {"1", "true", "yes", "on"},
                "emotion_backend": os.getenv("AHOOTSA_EMOTION_AUDIO_BACKEND", "pygame"),
                "winsound_enabled": os.getenv("AHOOTSA_MEMORY_WINSOUND_ENABLED", "0") in {"1", "true", "yes", "on"},
            },
            "micro": {"voice_control_expected": True, "muted_by_ahootsa_panel": False},
            "camera_pc": {"photos_dir": str(_photos_dir()), "latest": str(latest) if latest else None},
            "profiles_dir": os.getenv("REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY", ""),
            "tools_dir": os.getenv("REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY", ""),
            "config_files": len(_config_inventory()),
        })

    @app.get("/ahootsa/resolve_activity")
    def _resolve_activity(activity: str = "baile uno") -> JSONResponse:
        payload = _resolve_activity_payload(activity)
        return JSONResponse(payload, status_code=200 if payload.get("ok") else 404)

    @app.get("/ahootsa/list_activities")
    def _list_activities() -> JSONResponse:
        try:
            mod = _load_profile_play_emotion_module()
            moves = mod.list_moves() if hasattr(mod, "list_moves") else []
            display = mod.display_name_for_move if hasattr(mod, "display_name_for_move") else (lambda x: x)
            preferred = ["dance1", "dance2", "dance3", "welcoming2", "success1", "calming1", "electric1", "thoughtful1", "amazed1", "laughing2", "yes1", "no1"]
            items = [{"technical_id": mid, "nombre_es": display(mid), "available": mid in moves, "example": f"haz {display(mid)}"} for mid in preferred]
            return JSONResponse({"ok": True, "count": len(moves), "items": items, "message_for_user": "Bailes principales: baile uno, baile dos, baile tres. También: saludo, celebración, calma y eléctrico."})
        except Exception as exc:
            return JSONResponse({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, status_code=500)

    @app.post("/ahootsa/play_activity")
    @app.get("/ahootsa/play_activity")
    async def _play_activity(activity: str = "baile uno", sound: bool = True) -> JSONResponse:
        """Diagnostic panel play endpoint.

        It is intentionally separated from the voice engine. The preferred path is still
        the official HF tool call. This route helps verify resources from the panel.
        """
        resolved_payload = _resolve_activity_payload(activity)
        if not resolved_payload.get("ok"):
            return JSONResponse(resolved_payload, status_code=404)
        if direct_robot is None:
            payload = dict(resolved_payload)
            payload.update({"ok": False, "error": "direct_robot_not_available", "message_for_user": "El alias se reconoce, pero el panel no tiene acceso directo al robot para reproducirlo. Prueba por voz o reinicia Ahootsa."})
            return JSONResponse(payload, status_code=503)
        try:
            from reachy_mini_conversation_app.moves import MovementManager
            from reachy_mini_conversation_app.tools.core_tools import ToolDependencies
            mod = _load_tool_module("play_panel_dance_activity")
            mm = MovementManager(current_robot=direct_robot)
            mm.start()
            deps = ToolDependencies(reachy_mini=direct_robot, movement_manager=mm, instance_path=os.getenv("AHOOTSA_INSTANCE_PATH"), camera_enabled=False)
            tool = mod.PlayPanelDanceActivity()
            result = await tool(deps, activity=activity, sound=sound, delay_before_play_seconds=0, post_play_wait_seconds=3.0)
            try:
                mm.stop(reset_to_neutral=False)
            except Exception:
                pass
            if isinstance(result, dict):
                result.setdefault("direct_panel_test", True)
                result.setdefault("message_for_user", "Prueba de panel enviada.")
            return JSONResponse(result, status_code=200 if isinstance(result, dict) and result.get("ok") else 500)
        except Exception as exc:
            return JSONResponse({"ok": False, "requested": activity, "resolved": resolved_payload.get("resolved"), "error": f"{type(exc).__name__}: {exc}", "message_for_user": "No he podido reproducir desde el panel. Si por voz sí funciona, este endpoint de diagnóstico no es necesario."}, status_code=500)

    @app.get("/status")
    def _compat_status() -> JSONResponse:
        return JSONResponse({"ok": True, "status": "running", "app": "Ahootsa", "version": VERSION})

    @app.get("/config/list")
    def _config_list() -> JSONResponse:
        return JSONResponse({
            "ok": True,
            "version": VERSION,
            "files": _config_inventory(),
            "policy": "Ahootsa editable. App oficial visible como consulta protegida para no tocar el núcleo oficial.",
        })

    @app.get("/config/file")
    def _config_file(id: str) -> JSONResponse:
        item = _get_config_item(id)
        if not item:
            return JSONResponse({"ok": False, "error": "config_id_not_found"}, status_code=404)
        path = Path(item["path"])
        if not path.exists():
            return JSONResponse({"ok": False, "error": "file_not_found", "path": str(path)}, status_code=404)
        content = _safe_read_text(path)
        payload = dict(item)
        payload.update({"ok": True, "content": content, "note": _config_note_for(item)})
        return JSONResponse(payload)

    @app.post("/config/file")
    async def _config_save(request: Request) -> JSONResponse:
        body = await request.json()
        item = _get_config_item(str(body.get("id", "")))
        if not item:
            return JSONResponse({"ok": False, "error": "config_id_not_found"}, status_code=404)
        if not item.get("can_save"):
            return JSONResponse({"ok": False, "error": "file_is_protected", "message_for_user": "Este archivo no se guarda desde el panel porque pertenece a la app oficial o es código. Abre una copia si necesitas revisarlo."}, status_code=403)
        path = Path(item["path"])
        content = str(body.get("content", ""))
        try:
            backup = _backup_file(path) if path.exists() else None
            path.write_text(content, encoding="utf-8")
            return JSONResponse({
                "ok": True,
                "path": str(path),
                "backup": str(backup) if backup else None,
                "requires_restart": item.get("requires_restart", False),
                "message_for_user": "Archivo guardado. Reinicia Ahootsa si has cambiado perfiles, instructions.txt o tools.txt.",
            })
        except Exception as exc:
            return JSONResponse({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, status_code=500)

    @app.post("/config/open")
    async def _config_open(request: Request) -> JSONResponse:
        body = await request.json()
        item = _get_config_item(str(body.get("id", "")))
        if not item:
            return JSONResponse({"ok": False, "error": "config_id_not_found"}, status_code=404)
        path = Path(item["path"])
        if not path.exists():
            return JSONResponse({"ok": False, "error": "file_not_found", "path": str(path)}, status_code=404)
        try:
            if os.name == "nt":
                subprocess.Popen(["notepad.exe", str(path)], close_fds=True)
                return JSONResponse({"ok": True, "opened": str(path), "editor": "notepad.exe", "can_save_from_panel": item.get("can_save", False)})
            return JSONResponse({"ok": False, "error": "not_windows", "message_for_user": "Abrir Bloc de notas solo está disponible en Windows."}, status_code=501)
        except Exception as exc:
            return JSONResponse({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, status_code=500)

    @app.post("/config/apply")
    def _config_apply() -> JSONResponse:
        refreshed = False
        error = None
        try:
            from reachy_mini_conversation_app.config import refresh_runtime_config_from_env
            refresh_runtime_config_from_env()
            refreshed = True
        except Exception as exc:
            error = repr(exc)
        return JSONResponse({
            "ok": True,
            "runtime_config_refreshed": refreshed,
            "refresh_error": error,
            "restart_recommended": True,
            "message_for_user": "Configuración registrada. Los JSON de actividades suelen aplicarse en la siguiente llamada. Cambios en profiles/tools/instructions requieren reiniciar Ahootsa para crear una sesión Hugging Face nueva.",
        })


    @app.get("/communication/levels")
    async def _communication_levels() -> JSONResponse:
        try:
            result = await _call_communication_tool("list_communication_activity_levels", "ListCommunicationActivityLevels")
            return JSONResponse(result, status_code=200 if result.get("ok") else 500)
        except Exception as exc:
            return JSONResponse({"ok": False, "error": f"{type(exc).__name__}: {exc}", "uses_ollama": False}, status_code=500)

    @app.get("/communication/activities")
    async def _communication_activities(level: str = "facil", limit: int = 6) -> JSONResponse:
        try:
            result = await _call_communication_tool("list_communication_activities", "ListCommunicationActivities", level=level, limit=limit)
            return JSONResponse(result, status_code=200 if result.get("ok") else 400)
        except Exception as exc:
            return JSONResponse({"ok": False, "error": f"{type(exc).__name__}: {exc}", "uses_ollama": False}, status_code=500)

    @app.get("/communication/start")
    async def _communication_start(level: str = "facil", activity: str = "1") -> JSONResponse:
        try:
            result = await _call_communication_tool("start_communication_activity", "StartCommunicationActivity", level=level, activity=activity)
            return JSONResponse(result, status_code=200 if result.get("ok") else 400)
        except Exception as exc:
            return JSONResponse({"ok": False, "error": f"{type(exc).__name__}: {exc}", "uses_ollama": False}, status_code=500)

    @app.get("/communication/diagnose")
    async def _communication_diagnose(level: str = "facil", activity: str = "1") -> JSONResponse:
        t0 = datetime.now()
        results: dict[str, Any] = {"ok": True, "version": VERSION, "uses_ollama": False, "note": "Diagnóstico local. Si esto es rápido y por voz tarda, el retraso está en la cadena voz/HF antes o después de la herramienta."}
        try:
            results["levels"] = await _call_communication_tool("list_communication_activity_levels", "ListCommunicationActivityLevels")
            results["activities"] = await _call_communication_tool("list_communication_activities", "ListCommunicationActivities", level=level, limit=6)
            results["start"] = await _call_communication_tool("start_communication_activity", "StartCommunicationActivity", level=level, activity=activity)
            results["total_route_duration_ms"] = int((datetime.now() - t0).total_seconds() * 1000)
            return JSONResponse(results)
        except Exception as exc:
            results.update({"ok": False, "error": f"{type(exc).__name__}: {exc}", "total_route_duration_ms": int((datetime.now() - t0).total_seconds() * 1000)})
            return JSONResponse(results, status_code=500)

    @app.get("/ollama/status")
    def _ollama_status() -> JSONResponse:
        return JSONResponse(_ollama_tags())

    @app.get("/ollama/models")
    def _ollama_models() -> JSONResponse:
        return JSONResponse(_ollama_tags())

    async def _ask_request(request: Request) -> JSONResponse:
        body = await request.json()
        prompt = (body.get("prompt") or body.get("question") or body.get("message") or body.get("text") or "").strip()
        if not prompt:
            return JSONResponse({"ok": False, "error": "prompt vacío", "message_for_user": "Escribe una pregunta para Ollama."}, status_code=400)
        model = (body.get("model") or _ollama_model()).strip() or _ollama_model()
        system = (body.get("system_prompt") or "Eres Ahootsa. Responde en castellano claro, breve y natural.").strip()
        payload = {"model": model, "stream": False, "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}], "options": {"temperature": 0.35, "num_predict": 180, "num_ctx": 2048}}
        try:
            data = _http_json(f"{_ollama_base()}/api/chat", payload=payload, timeout=float(os.getenv("AHOOTSA_OLLAMA_TIMEOUT_SECONDS", "20")))
            msg = data.get("message", {}) if isinstance(data, dict) else {}
            reply = (msg.get("content") if isinstance(msg, dict) else "") or data.get("response", "")
            return JSONResponse({"ok": True, "reply": str(reply).strip(), "message_for_user": str(reply).strip(), "model": data.get("model", model), "raw": data})
        except Exception as exc:
            return JSONResponse({"ok": False, "error": f"{type(exc).__name__}: {exc}", "message_for_user": "Ollama local no ha respondido. Comprueba que Ollama está abierto y que existe el modelo llama3.2:3b."}, status_code=503)

    for path in ["/ollama/ask", "/ask_ollama", "/api/ask_ollama", "/api/ollama/ask", "/local-ai/ask", "/llm/ask", "/ask", "/chat"]:
        app.post(path)(_ask_request)

    @app.get("/camera_pc/page")
    def _camera_page() -> HTMLResponse:
        return HTMLResponse(_camera_html())

    @app.post("/camera_pc/upload")
    async def _camera_upload(request: Request) -> JSONResponse:
        try:
            body = await request.json()
            img = body.get("image", "")
            if "," in img:
                img = img.split(",", 1)[1]
            data = base64.b64decode(img)
            path = _photos_dir() / f"ahootsa_pc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            path.write_bytes(data)
            return JSONResponse({"ok": True, "path": str(path), "bytes": len(data), "message_for_user": "Foto guardada."})
        except Exception as exc:
            return JSONResponse({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, status_code=400)

    @app.get("/memory/page")
    def _memory_page(game_id: str = "animales", reset: int = 0) -> HTMLResponse:
        try:
            if reset:
                _memory_mod().reset_game(game_id)
            return HTMLResponse(_memory_page_html(game_id=game_id, reset=bool(reset)))
        except Exception as exc:
            return HTMLResponse(f"<h1>Error cargando Memory</h1><pre>{type(exc).__name__}: {exc}</pre>", status_code=500)

    @app.get("/memory/games")
    def _memory_games() -> JSONResponse:
        try:
            return JSONResponse({"ok": True, "games": _memory_mod().available_games()})
        except Exception as exc:
            return JSONResponse({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, status_code=500)

    @app.get("/memory/state")
    def _memory_state() -> JSONResponse:
        return JSONResponse(_memory_status_payload())

    @app.get("/memory/reset")
    def _memory_reset(game_id: str = "animales") -> JSONResponse:
        try:
            return JSONResponse(_memory_mod().reset_game(game_id))
        except Exception as exc:
            return JSONResponse({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, status_code=500)

    @app.get("/memory/choose")
    def _memory_choose(first: int, second: int) -> JSONResponse:
        try:
            return JSONResponse(_memory_mod().choose_cards(first, second))
        except Exception as exc:
            return JSONResponse({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, status_code=500)

    @app.post("/camera_pc/capture")
    async def _camera_capture(request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except Exception:
            body = {}
        result = _capture_pc_with_opencv(int(body.get("camera_index", 0)), int(body.get("warmup_frames", 2)))
        return JSONResponse(result, status_code=200 if result.get("ok") else 503)

    @app.get("/camera_pc/latest")
    def _camera_latest() -> JSONResponse:
        p = _latest_photo()
        return JSONResponse({"ok": bool(p), "latest": str(p) if p else None, "photos_dir": str(_photos_dir())})

    @app.post("/camera_pc/analyze_latest")
    async def _camera_analyze_latest(request: Request) -> JSONResponse:
        p = _latest_photo()
        if not p:
            return JSONResponse({"ok": False, "error": "no_photo", "message_for_user": "Todavía no hay foto guardada en la cámara PC."}, status_code=404)
        try:
            body = await request.json()
        except Exception:
            body = {}
        question = (body.get("question") or "Describe la imagen en castellano claro y sencillo.").strip()
        try:
            image_b64 = base64.b64encode(p.read_bytes()).decode("ascii")
            payload = {"model": _vision_model(), "prompt": question, "stream": False, "images": [image_b64], "options": {"temperature": 0.2, "num_predict": 160}}
            data = _http_json(f"{_ollama_base()}/api/generate", payload=payload, timeout=float(os.getenv("AHOOTSA_IMAGE_TIMEOUT_SECONDS", "60")))
            reply = str(data.get("response", "")).strip()
            return JSONResponse({"ok": True, "reply": reply, "message_for_user": reply, "image_path": str(p), "model": data.get("model", _vision_model()), "raw": data})
        except urllib.error.HTTPError as exc:
            return JSONResponse({"ok": False, "error": f"HTTPError {exc.code}: {exc.reason}", "message_for_user": "Para analizar fotos necesitas un modelo de visión en Ollama, por ejemplo: ollama pull llava:latest."}, status_code=503)
        except Exception as exc:
            return JSONResponse({"ok": False, "error": f"{type(exc).__name__}: {exc}", "message_for_user": "No he podido analizar la foto. Comprueba Ollama y el modelo de visión."}, status_code=503)

    @app.get("/voices/current")
    def _voice_current() -> JSONResponse:
        return JSONResponse({"ok": True, "voice": {"id": os.getenv("VOICE", "Sohee"), "name": os.getenv("VOICE", "Sohee"), "language": "es-ES", "engine": "hf_realtime"}})

    @app.get("/voices")
    def _voices() -> JSONResponse:
        return JSONResponse({"ok": True, "current": os.getenv("VOICE", "Sohee"), "voices": ["Sohee", "Aiden", "Serena", "Vivian"]})

    @app.get("/mic")
    def _mic() -> JSONResponse:
        return JSONResponse({"ok": True, "muted": False, "voice_control_expected": True})

    @app.get("/audio/status")
    def _audio_status() -> JSONResponse:
        return JSONResponse({"ok": True, "voice": os.getenv("VOICE", "Sohee"), "emotion_audio_backend": os.getenv("AHOOTSA_EMOTION_AUDIO_BACKEND", "pygame"), "emotion_audio_enabled": os.getenv("AHOOTSA_DISABLE_EMOTION_AUDIO", "0") not in {"1", "true", "yes", "on"}})
