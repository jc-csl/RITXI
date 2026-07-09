# -*- coding: utf-8 -*-
"""
Ahootsa 5.0.35 - soporte cámara PC
Aplica dos correcciones:
1) Backend: endpoints /camera/upload y /camera/latest mediante bootstrap FastAPI/Starlette.
2) Frontend: panel flotante de cámara basado en navigator.mediaDevices.getUserMedia.

Pensado para ejecutarse con el python.exe del apps_venv de Reachy Mini Control.
"""
from __future__ import annotations

import base64
import datetime as _dt
import os
import pathlib
import re
import sys
from typing import Iterable

MARK_BACKEND = "# AHOOTSA_CAMERA_PC_5_0_35_BEGIN"
MARK_BACKEND_END = "# AHOOTSA_CAMERA_PC_5_0_35_END"
MARK_HTML = "<!-- AHOOTSA_CAMERA_PC_5_0_35 -->"
JS_NAME = "ahootsa_camera_pc_5_0_35.js"

BACKEND_PATCH = r'''
# AHOOTSA_CAMERA_PC_5_0_35_BEGIN
# Soporte de cámara PC: endpoints para guardar la última foto tomada desde el navegador.
# Se añade como bootstrap para no depender del nombre exacto de la variable FastAPI.
try:
    import base64 as _ahootsa_b64
    import datetime as _ahootsa_dt
    import json as _ahootsa_json
    import os as _ahootsa_os
    import pathlib as _ahootsa_pathlib
    import re as _ahootsa_re

    _AHOOTSA_CAMERA_DIR = _ahootsa_pathlib.Path(
        _ahootsa_os.environ.get("AHOOTSA_CAMERA_DIR", r"D:\RITXI\logs\camera")
    )
    _AHOOTSA_CAMERA_DIR.mkdir(parents=True, exist_ok=True)
    _AHOOTSA_CAMERA_LATEST = {"ok": False, "message": "No hay foto capturada todavía."}

    def _ahootsa_camera_add_routes(app):
        try:
            routes = getattr(app, "routes", [])
            existing = {getattr(r, "path", None) for r in routes}
            if "/camera/upload" in existing and "/camera/latest" in existing:
                return app

            async def _camera_upload(request):
                nonlocal_app = app
                try:
                    payload = await request.json()
                except Exception:
                    return {"ok": False, "error": "JSON inválido."}

                data_url = payload.get("image_data") or payload.get("dataUrl") or payload.get("image")
                if not data_url or not isinstance(data_url, str):
                    return {"ok": False, "error": "Falta image_data en formato data URL."}

                m = _ahootsa_re.match(r"^data:image/(png|jpeg|jpg);base64,(.+)$", data_url, _ahootsa_re.I | _ahootsa_re.S)
                if not m:
                    return {"ok": False, "error": "Formato de imagen no válido. Se espera data:image/png;base64,..."}

                ext = "jpg" if m.group(1).lower() in ("jpg", "jpeg") else "png"
                raw = _ahootsa_b64.b64decode(m.group(2))
                ts = _ahootsa_dt.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ahootsa_camera_{ts}.{ext}"
                path = _AHOOTSA_CAMERA_DIR / filename
                path.write_bytes(raw)

                info = {
                    "ok": True,
                    "filename": filename,
                    "path": str(path),
                    "bytes": len(raw),
                    "created_at": _ahootsa_dt.datetime.now().isoformat(),
                    "source": "browser_camera_getUserMedia",
                }
                globals()["_AHOOTSA_CAMERA_LATEST"] = info
                try:
                    (_AHOOTSA_CAMERA_DIR / "latest.json").write_text(_ahootsa_json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
                except Exception:
                    pass
                return info

            async def _camera_latest():
                try:
                    latest_file = _AHOOTSA_CAMERA_DIR / "latest.json"
                    if latest_file.exists():
                        return _ahootsa_json.loads(latest_file.read_text(encoding="utf-8"))
                except Exception:
                    pass
                return globals().get("_AHOOTSA_CAMERA_LATEST", {"ok": False, "message": "No hay foto capturada todavía."})

            # FastAPI acepta decoradores get/post. Starlette apps también suelen exponer route/add_route,
            # pero aquí priorizamos FastAPI porque es lo que usa Ahootsa.
            if hasattr(app, "post"):
                app.post("/camera/upload")(_camera_upload)
            if hasattr(app, "get"):
                app.get("/camera/latest")(_camera_latest)
        except Exception:
            pass
        return app

    try:
        from fastapi import FastAPI as _AhootsaFastAPI
        _orig_fastapi_init_camera = getattr(_AhootsaFastAPI, "_ahootsa_camera_orig_init_5_0_35", None)
        if _orig_fastapi_init_camera is None:
            _orig_fastapi_init_camera = _AhootsaFastAPI.__init__
            setattr(_AhootsaFastAPI, "_ahootsa_camera_orig_init_5_0_35", _orig_fastapi_init_camera)

            def _ahootsa_fastapi_init_camera(self, *args, **kwargs):
                _orig_fastapi_init_camera(self, *args, **kwargs)
                _ahootsa_camera_add_routes(self)

            _AhootsaFastAPI.__init__ = _ahootsa_fastapi_init_camera
    except Exception:
        pass
except Exception:
    pass
# AHOOTSA_CAMERA_PC_5_0_35_END
'''

JS_PATCH = r'''// AHOOTSA_CAMERA_PC_5_0_35
(function () {
  if (window.__AHOOTSA_CAMERA_PC_5_0_35__) return;
  window.__AHOOTSA_CAMERA_PC_5_0_35__ = true;

  const css = `
  #ahootsa-camera-panel-5035 { position: fixed; right: 16px; bottom: 16px; z-index: 2147483000; font-family: system-ui, sans-serif; }
  #ahootsa-camera-panel-5035 .box { width: 280px; background: white; border: 2px solid #d3d3d3; border-radius: 14px; box-shadow: 0 6px 20px rgba(0,0,0,.18); overflow: hidden; }
  #ahootsa-camera-panel-5035 .head { display: flex; align-items: center; justify-content: space-between; padding: 8px 10px; background: #f7f7f7; font-weight: 700; color: #cc167a; }
  #ahootsa-camera-panel-5035 .body { padding: 10px; display: none; }
  #ahootsa-camera-panel-5035.open .body { display: block; }
  #ahootsa-camera-panel-5035 video, #ahootsa-camera-panel-5035 img { width: 100%; border-radius: 10px; background: #eee; display: block; }
  #ahootsa-camera-panel-5035 .row { display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; }
  #ahootsa-camera-panel-5035 button { border: 1px solid #d3d3d3; background: #fff; border-radius: 10px; padding: 7px 9px; cursor: pointer; font-weight: 600; }
  #ahootsa-camera-panel-5035 button.primary { background: #cc167a; color: white; border-color: #cc167a; }
  #ahootsa-camera-panel-5035 .status { margin-top: 7px; font-size: 12px; color: #555; line-height: 1.25; }
  `;

  function addStyle() {
    if (document.getElementById('ahootsa-camera-style-5035')) return;
    const st = document.createElement('style');
    st.id = 'ahootsa-camera-style-5035';
    st.textContent = css;
    document.head.appendChild(st);
  }

  function dataUrlToDownload(dataUrl, filename) {
    const a = document.createElement('a');
    a.href = dataUrl;
    a.download = filename || 'ahootsa_foto.png';
    document.body.appendChild(a);
    a.click();
    a.remove();
  }

  function buildPanel() {
    if (document.getElementById('ahootsa-camera-panel-5035')) return;
    addStyle();
    const panel = document.createElement('div');
    panel.id = 'ahootsa-camera-panel-5035';
    panel.innerHTML = `
      <div class="box">
        <div class="head">
          <span>📷 Cámara PC</span>
          <button type="button" data-act="toggle">Abrir</button>
        </div>
        <div class="body">
          <video autoplay playsinline muted></video>
          <canvas style="display:none"></canvas>
          <img alt="Última foto" style="display:none" />
          <div class="row">
            <button type="button" class="primary" data-act="start">Activar</button>
            <button type="button" class="primary" data-act="shot">Hacer foto</button>
            <button type="button" data-act="download">Guardar</button>
            <button type="button" data-act="stop">Cerrar cámara</button>
          </div>
          <div class="status">Lista. Pulsa Activar y acepta el permiso de cámara.</div>
        </div>
      </div>`;
    document.body.appendChild(panel);

    const video = panel.querySelector('video');
    const canvas = panel.querySelector('canvas');
    const img = panel.querySelector('img');
    const status = panel.querySelector('.status');
    let stream = null;
    let lastDataUrl = null;

    function setStatus(txt) { status.textContent = txt; }

    async function start() {
      try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          setStatus('El navegador no expone getUserMedia. Prueba desde localhost o revisa permisos.');
          return;
        }
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false });
        video.srcObject = stream;
        video.style.display = 'block';
        setStatus('Cámara activa. Puedes hacer foto.');
      } catch (err) {
        setStatus('No se pudo activar la cámara: ' + (err && err.message ? err.message : err));
      }
    }

    function stop() {
      if (stream) stream.getTracks().forEach(t => t.stop());
      stream = null;
      video.srcObject = null;
      setStatus('Cámara cerrada.');
    }

    async function shot() {
      if (!video.videoWidth || !video.videoHeight) {
        setStatus('Primero activa la cámara y espera a ver la imagen.');
        return;
      }
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      lastDataUrl = canvas.toDataURL('image/png');
      window.AHOOTSA_LAST_CAMERA_PHOTO = lastDataUrl;
      try { localStorage.setItem('AHOOTSA_LAST_CAMERA_PHOTO', lastDataUrl); } catch (_) {}
      img.src = lastDataUrl;
      img.style.display = 'block';
      window.dispatchEvent(new CustomEvent('ahootsa:camera-photo', { detail: { image_data: lastDataUrl } }));
      setStatus('Foto tomada. Guardando en backend...');
      try {
        const res = await fetch('/camera/upload', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image_data: lastDataUrl, created_at: new Date().toISOString() })
        });
        const json = await res.json();
        if (json && json.ok) setStatus('Foto guardada: ' + (json.path || json.filename));
        else setStatus('Foto tomada, pero no guardada en backend: ' + JSON.stringify(json));
      } catch (err) {
        setStatus('Foto tomada. No se pudo enviar al backend; usa Guardar.');
      }
    }

    function download() {
      if (!lastDataUrl) { setStatus('Todavía no hay foto.'); return; }
      dataUrlToDownload(lastDataUrl, 'ahootsa_foto_' + new Date().toISOString().replace(/[:.]/g, '-') + '.png');
    }

    panel.addEventListener('click', (ev) => {
      const b = ev.target.closest('button[data-act]');
      if (!b) return;
      const act = b.getAttribute('data-act');
      if (act === 'toggle') {
        panel.classList.toggle('open');
        b.textContent = panel.classList.contains('open') ? 'Ocultar' : 'Abrir';
      } else if (act === 'start') start();
      else if (act === 'shot') shot();
      else if (act === 'stop') stop();
      else if (act === 'download') download();
    });

    window.AHOOTSA_CAMERA = { start, stop, shot, download, getLastPhoto: () => lastDataUrl };
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', buildPanel);
  else buildPanel();
})();
'''


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_text(path: pathlib.Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def find_package_root() -> pathlib.Path:
    import ahootsa_realtime_ollama_desktop_app as pkg  # type: ignore
    return pathlib.Path(pkg.__file__).resolve().parent


def patch_backend(pkg_root: pathlib.Path) -> None:
    init_py = pkg_root / "__init__.py"
    txt = read_text(init_py) if init_py.exists() else ""
    if MARK_BACKEND in txt:
        print(f"[OK] Backend ya tenia parche camara: {init_py}")
        return
    backup = init_py.with_suffix(init_py.suffix + ".bak_5_0_35")
    if init_py.exists() and not backup.exists():
        backup.write_text(txt, encoding="utf-8")
    write_text(init_py, txt.rstrip() + "\n\n" + BACKEND_PATCH.strip() + "\n")
    print(f"[OK] Backend parcheado: {init_py}")


def html_candidates(roots: Iterable[pathlib.Path]) -> list[pathlib.Path]:
    out: list[pathlib.Path] = []
    for root in roots:
        if root.exists():
            out.extend([p for p in root.rglob("*.html") if p.is_file()])
    return out


def patch_frontend(pkg_root: pathlib.Path, extra_root: pathlib.Path | None = None) -> None:
    js_path = pkg_root / JS_NAME
    write_text(js_path, JS_PATCH)
    print(f"[OK] JS camara escrito: {js_path}")

    roots = [pkg_root]
    if extra_root:
        roots.append(extra_root)
    htmls = html_candidates(roots)
    injected = 0
    tag = f'{MARK_HTML}\n<script src="/{JS_NAME}"></script>'

    # Si los HTML se sirven como ficheros estáticos, se inyecta el script.
    for html in htmls:
        txt = read_text(html)
        if MARK_HTML in txt:
            continue
        rel_tag = f'{MARK_HTML}\n<script src="{JS_NAME}"></script>'
        # Si el HTML está en el mismo paquete, usamos ruta relativa para maximizar compatibilidad.
        script_tag = rel_tag
        if "</body>" in txt.lower():
            txt2 = re.sub(r"</body>", script_tag + "\n</body>", txt, count=1, flags=re.I)
        else:
            txt2 = txt.rstrip() + "\n" + script_tag + "\n"
        backup = html.with_suffix(html.suffix + ".bak_5_0_35")
        if not backup.exists():
            backup.write_text(txt, encoding="utf-8")
        write_text(html, txt2)
        injected += 1
        print(f"[OK] HTML parcheado: {html}")

    # Plan B: parchea JS grandes añadiendo carga dinámica desde el propio bundle si no hay HTML.
    if injected == 0:
        js_files = [p for p in pkg_root.rglob("*.js") if p.name != JS_NAME and p.is_file() and p.stat().st_size < 2_000_000]
        marker = "// AHOOTSA_CAMERA_PC_5_0_35_LOADER"
        loader = f"\n{marker}\n(function(){{try{{if(!window.__AHOOTSA_CAMERA_LOADER_5035__){{window.__AHOOTSA_CAMERA_LOADER_5035__=true;var s=document.createElement('script');s.src='/{JS_NAME}';s.defer=true;document.head.appendChild(s);}}}}catch(e){{}}}})();\n"
        for js in js_files[:20]:
            txt = read_text(js)
            if marker in txt or "AHOOTSA_CAMERA_PC_5_0_35" in txt:
                continue
            backup = js.with_suffix(js.suffix + ".bak_5_0_35")
            if not backup.exists():
                backup.write_text(txt, encoding="utf-8")
            write_text(js, txt.rstrip() + loader)
            injected += 1
            print(f"[OK] Loader camara añadido a JS: {js}")

    if injected == 0:
        print("[WARN] No se encontro HTML/JS para inyectar panel. El backend de camara si queda disponible.")


def main() -> int:
    extra = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 and sys.argv[1] else None
    try:
        pkg_root = find_package_root()
    except Exception as e:
        print(f"[ERROR] No puedo importar ahootsa_realtime_ollama_desktop_app: {e}")
        return 2
    print(f"[INFO] Paquete Ahootsa: {pkg_root}")
    patch_backend(pkg_root)
    patch_frontend(pkg_root, extra)
    print("[OK] Correccion camara PC 5.0.35 aplicada")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
