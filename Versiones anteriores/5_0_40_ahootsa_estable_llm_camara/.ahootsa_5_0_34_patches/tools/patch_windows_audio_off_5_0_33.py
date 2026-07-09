"""
Ahootsa 5.0.33 - eliminar audio Windows/navegador dejando solo audio Ahootsa.

Esta correccion es mas fuerte que el guardia 5.0.29:
1) Bloquea Web Speech API en navegador: speechSynthesis, SpeechSynthesisUtterance.
2) Inyecta el bloqueo en HTML/JS de ahootsa, reachy_mini_conversation_app y reachy_talk_data.
3) Instala/actualiza sitecustomize.py en apps_venv para anular TTS Windows desde Python:
   - pyttsx3.init().say/runAndWait/stop no hacen nada.
   - win32com.client.Dispatch("SAPI.SpVoice").Speak no hace nada.
   - comtypes.client.CreateObject("SAPI.SpVoice").Speak no hace nada.

No bloquea la salida de audio propia de Ahootsa/OpenAI/Realtime ni etiquetas <audio> normales.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib
import pathlib
import re
import shutil
import sys
import sysconfig
from typing import Iterable

MARKER = "Ahootsa 5.0.33 - sin audio Windows"
PACKAGE_NAMES = [
    "ahootsa_realtime_ollama_desktop_app",
    "reachy_mini_conversation_app",
    "reachy_talk_data",
]

JS_GUARD = r'''
/* ============================================================
 * Ahootsa 5.0.33 - SIN AUDIO WINDOWS / NAVEGADOR
 *
 * Politica global:
 *   - Solo debe hablar Ahootsa.
 *   - Se bloquea la TTS del navegador/Windows: Web Speech API.
 *   - No se bloquean etiquetas <audio>, porque Ahootsa/Realtime puede usarlas.
 * ============================================================ */
(function installAhootsaNoWindowsAudioGuard(rootWindow) {
  function apply(win) {
    try {
      if (!win || win.__AHOOTSA_5033_NO_WINDOWS_AUDIO__) return;
      win.__AHOOTSA_5033_NO_WINDOWS_AUDIO__ = true;

      win.AHOOTSA_AUDIO_POLICY = win.AHOOTSA_AUDIO_POLICY || {};
      win.AHOOTSA_AUDIO_POLICY.onlyAhootsaVoice = true;
      win.AHOOTSA_AUDIO_POLICY.blockWindowsSpeechSynthesis = true;
      win.AHOOTSA_AUDIO_POLICY.blockedBy = "Ahootsa 5.0.33";

      function quietLog(msg) {
        try {
          if (win.AHOOTSA_DEBUG_AUDIO === true && win.console) {
            win.console.info("[Ahootsa 5.0.33] Audio Windows bloqueado", msg || "");
          }
        } catch (e) {}
      }

      function cancelNativeSpeech() {
        try {
          if (win.speechSynthesis && typeof win.speechSynthesis.cancel === "function") {
            win.speechSynthesis.cancel();
          }
        } catch (e) {}
      }

      function installSpeechBlock() {
        try {
          cancelNativeSpeech();

          if (win.speechSynthesis) {
            var synth = win.speechSynthesis;

            var blockedSpeak = function(utterance) {
              try {
                quietLog(utterance && (utterance.text || utterance.lang || (utterance.voice && utterance.voice.name)));
              } catch (e) {}
              cancelNativeSpeech();
              return undefined;
            };
            blockedSpeak.__ahootsa5033Blocked = true;

            var blockedGetVoices = function() { return []; };

            try { synth.speak = blockedSpeak; } catch (e1) {
              try { Object.defineProperty(synth, "speak", { value: blockedSpeak, configurable: true, writable: true }); } catch (e2) {}
            }
            try { synth.getVoices = blockedGetVoices; } catch (e3) {
              try { Object.defineProperty(synth, "getVoices", { value: blockedGetVoices, configurable: true, writable: true }); } catch (e4) {}
            }
            try { synth.resume = cancelNativeSpeech; } catch (e5) {}
          }

          // Neutraliza tambien la construccion de utterances usada por algunas actividades.
          try {
            var OriginalUtterance = win.SpeechSynthesisUtterance;
            if (OriginalUtterance && !win.__AHOOTSA_ORIGINAL_UTTERANCE_5033__) {
              win.__AHOOTSA_ORIGINAL_UTTERANCE_5033__ = OriginalUtterance;
            }
            var BlockedUtterance = function(text) {
              this.text = "";
              this.lang = "es-ES";
              this.volume = 0;
              this.rate = 1;
              this.pitch = 1;
              this.voice = null;
              this.__ahootsaBlockedUtterance = true;
              quietLog(text || "SpeechSynthesisUtterance");
            };
            BlockedUtterance.prototype = OriginalUtterance && OriginalUtterance.prototype ? OriginalUtterance.prototype : {};
            try { win.SpeechSynthesisUtterance = BlockedUtterance; } catch (e6) {
              try { Object.defineProperty(win, "SpeechSynthesisUtterance", { value: BlockedUtterance, configurable: true, writable: true }); } catch (e7) {}
            }
          } catch (e8) {}
        } catch (e) {}
      }

      installSpeechBlock();

      // Algunas librerias restauran speechSynthesis despues de cargar. Reaplicar mas tiempo.
      var n = 0;
      var timer = win.setInterval(function() {
        n += 1;
        installSpeechBlock();
        if (n >= 240) { try { win.clearInterval(timer); } catch (e) {} }
      }, 250);

      try { win.addEventListener("focus", installSpeechBlock, true); } catch (e) {}
      try { win.addEventListener("pageshow", installSpeechBlock, true); } catch (e) {}
      try { win.document && win.document.addEventListener("visibilitychange", installSpeechBlock, true); } catch (e) {}
      try { win.document && win.document.addEventListener("DOMContentLoaded", installSpeechBlock, true); } catch (e) {}

      // Aplicar tambien a iframes same-origin si los hubiera.
      function patchFrames() {
        try {
          var frames = win.document ? win.document.querySelectorAll("iframe") : [];
          for (var i = 0; i < frames.length; i++) {
            try { apply(frames[i].contentWindow); } catch (e) {}
          }
        } catch (e) {}
      }
      patchFrames();
      try {
        if (win.MutationObserver && win.document && win.document.documentElement) {
          var mo = new win.MutationObserver(function() { patchFrames(); installSpeechBlock(); });
          mo.observe(win.document.documentElement, { childList: true, subtree: true });
        }
      } catch (e) {}

      win.ahootsaAudio = win.ahootsaAudio || {};
      win.ahootsaAudio.isWindowsSpeechBlocked = function() { return true; };
      win.ahootsaAudio.cancelWindowsSpeech = cancelNativeSpeech;
      win.ahootsaAudio.blockWindowsSpeechNow = installSpeechBlock;
    } catch (e) {}
  }
  apply(rootWindow || window);
})(typeof window !== "undefined" ? window : null);
/* Fin Ahootsa 5.0.33 - SIN AUDIO WINDOWS / NAVEGADOR */
'''.strip() + "\n"

SITE_CUSTOMIZE_BLOCK = r'''

# ============================================================
# Ahootsa 5.0.33 - SIN AUDIO WINDOWS DESDE PYTHON
# Este bloque se carga automaticamente en apps_venv al iniciar Python.
# Solo actua si AHOOTSA_DISABLE_WINDOWS_TTS=1 y no se ha definido
# AHOOTSA_ALLOW_WINDOWS_TTS=1.
# ============================================================
def _ahootsa_5033_disable_windows_tts():
    import os
    import sys
    import types
    import importlib

    if os.environ.get("AHOOTSA_ALLOW_WINDOWS_TTS", "").lower() in ("1", "true", "yes", "si", "sí"):
        return
    if os.environ.get("AHOOTSA_DISABLE_WINDOWS_TTS", "").lower() not in ("1", "true", "yes", "si", "sí"):
        return

    class _AhootsaSilentEngine:
        def say(self, *args, **kwargs): return None
        def runAndWait(self, *args, **kwargs): return None
        def stop(self, *args, **kwargs): return None
        def setProperty(self, *args, **kwargs): return None
        def getProperty(self, name=None, *args, **kwargs):
            if name == "voices": return []
            if name == "voice": return "ahootsa-only"
            if name == "rate": return 0
            if name == "volume": return 0
            return None
        def connect(self, *args, **kwargs): return None
        def disconnect(self, *args, **kwargs): return None
        def isBusy(self, *args, **kwargs): return False

    def _silent_init(*args, **kwargs):
        return _AhootsaSilentEngine()

    # pyttsx3: libreria tipica que dispara voz Windows/SAPI.
    try:
        pyttsx3 = importlib.import_module("pyttsx3")
        pyttsx3.init = _silent_init
        pyttsx3.__ahootsa_5033_disabled__ = True
    except Exception:
        mod = types.ModuleType("pyttsx3")
        mod.init = _silent_init
        mod.__ahootsa_5033_disabled__ = True
        sys.modules.setdefault("pyttsx3", mod)

    class _SilentSapiVoice:
        Volume = 0
        Rate = 0
        Voice = None
        def Speak(self, *args, **kwargs): return 0
        def Pause(self, *args, **kwargs): return None
        def Resume(self, *args, **kwargs): return None
        def Skip(self, *args, **kwargs): return 0
        def WaitUntilDone(self, *args, **kwargs): return True

    def _is_sapi_name(name):
        try:
            return "sapi.spvoice" in str(name).lower()
        except Exception:
            return False

    # win32com.client.Dispatch("SAPI.SpVoice").Speak(...)
    try:
        import win32com.client as _w32c
        _orig_dispatch = getattr(_w32c, "Dispatch", None)
        _orig_dispatchex = getattr(_w32c, "DispatchEx", None)
        def _dispatch(name, *args, **kwargs):
            if _is_sapi_name(name): return _SilentSapiVoice()
            if _orig_dispatch: return _orig_dispatch(name, *args, **kwargs)
            return _SilentSapiVoice()
        def _dispatchex(name, *args, **kwargs):
            if _is_sapi_name(name): return _SilentSapiVoice()
            if _orig_dispatchex: return _orig_dispatchex(name, *args, **kwargs)
            return _SilentSapiVoice()
        _w32c.Dispatch = _dispatch
        _w32c.DispatchEx = _dispatchex
        _w32c.__ahootsa_5033_disabled__ = True
    except Exception:
        pass

    # comtypes.client.CreateObject("SAPI.SpVoice")
    try:
        import comtypes.client as _ctc
        _orig_create_object = getattr(_ctc, "CreateObject", None)
        def _create_object(name, *args, **kwargs):
            if _is_sapi_name(name): return _SilentSapiVoice()
            if _orig_create_object: return _orig_create_object(name, *args, **kwargs)
            return _SilentSapiVoice()
        _ctc.CreateObject = _create_object
        _ctc.__ahootsa_5033_disabled__ = True
    except Exception:
        pass

try:
    _ahootsa_5033_disable_windows_tts()
except Exception:
    pass
# ============================================================
# Fin Ahootsa 5.0.33 - SIN AUDIO WINDOWS DESDE PYTHON
# ============================================================
'''

TEXT_SUFFIXES = {".html", ".htm", ".js", ".mjs", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}
HTML_SUFFIXES = {".html", ".htm"}
JS_SUFFIXES = {".js", ".mjs", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}
SKIP_PARTS = {"__pycache__", ".git", "node_modules", "dist-info", "site-packages_backup"}


def read_text(path: pathlib.Path) -> str | None:
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
        except Exception:
            return None
    return None


def write_text(path: pathlib.Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def backup_file(path: pathlib.Path) -> pathlib.Path:
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_name(path.name + f".bak_5_0_33_{stamp}")
    shutil.copy2(path, backup)
    return backup


def iter_files(root: pathlib.Path) -> Iterable[pathlib.Path]:
    if not root.exists():
        return []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        try:
            if path.stat().st_size > 6_000_000:
                continue
        except Exception:
            continue
        yield path


def inject_html(text: str) -> tuple[str, str]:
    if "__AHOOTSA_5033_NO_WINDOWS_AUDIO__" in text or MARKER in text:
        return text, "already"
    script = "<script>\n" + JS_GUARD + "</script>\n"
    if re.search(r"</head\s*>", text, flags=re.I):
        return re.sub(r"</head\s*>", script + "</head>", text, count=1, flags=re.I), "html_head"
    if re.search(r"</body\s*>", text, flags=re.I):
        return re.sub(r"</body\s*>", script + "</body>", text, count=1, flags=re.I), "html_body"
    return script + text, "html_prepend"


def inject_js(text: str) -> tuple[str, str]:
    if "__AHOOTSA_5033_NO_WINDOWS_AUDIO__" in text or MARKER in text:
        return text, "already"
    # En 5.0.33 se inyecta en todo JS/TS del paquete, no solo donde aparezca speechSynthesis.
    return JS_GUARD + "\n" + text, "js_prepend"


def patch_root(root: pathlib.Path, label: str) -> dict:
    res = {"label": label, "root": str(root), "exists": root.exists(), "checked": 0, "modified": 0, "already": 0, "skipped": 0, "files": []}
    if not root.exists():
        return res
    try:
        guard_path = root / "ahootsa_no_windows_audio_guard_5_0_33.js"
        old = read_text(guard_path) if guard_path.exists() else None
        if not old or "__AHOOTSA_5033_NO_WINDOWS_AUDIO__" not in old:
            if guard_path.exists(): backup_file(guard_path)
            write_text(guard_path, JS_GUARD)
            res["modified"] += 1
            res["files"].append(str(guard_path))
    except Exception as exc:
        print(f"[WARN] No he podido crear guard JS en {root}: {exc}")

    for path in iter_files(root):
        res["checked"] += 1
        txt = read_text(path)
        if txt is None:
            res["skipped"] += 1
            continue
        suffix = path.suffix.lower()
        if suffix in HTML_SUFFIXES:
            new, mode = inject_html(txt)
        elif suffix in JS_SUFFIXES:
            new, mode = inject_js(txt)
        else:
            res["skipped"] += 1
            continue
        if mode == "already":
            res["already"] += 1
            continue
        if new != txt:
            try:
                backup_file(path)
                write_text(path, new)
                res["modified"] += 1
                res["files"].append(str(path))
                print(f"[OK] {label}: {mode}: {path}")
            except Exception as exc:
                print(f"[WARN] No he podido modificar {path}: {exc}")
                res["skipped"] += 1
    return res


def locate_package(name: str) -> pathlib.Path | None:
    try:
        pkg = importlib.import_module(name)
        return pathlib.Path(pkg.__file__).resolve().parent
    except Exception as exc:
        print(f"[WARN] No se pudo localizar paquete {name}: {exc}")
        return None


def locate_site_packages() -> pathlib.Path:
    p = sysconfig.get_paths().get("purelib") or sysconfig.get_paths().get("platlib")
    if p:
        return pathlib.Path(p).resolve()
    root = locate_package("ahootsa_realtime_ollama_desktop_app")
    if root:
        return root.parent
    return pathlib.Path(sys.prefix) / "Lib" / "site-packages"


def install_sitecustomize(site_packages: pathlib.Path) -> dict:
    site_packages.mkdir(parents=True, exist_ok=True)
    sc = site_packages / "sitecustomize.py"
    res = {"path": str(sc), "modified": False, "already": False}
    old = read_text(sc) if sc.exists() else ""
    if old and "Ahootsa 5.0.33 - SIN AUDIO WINDOWS DESDE PYTHON" in old:
        res["already"] = True
        return res
    if sc.exists(): backup_file(sc)
    new = (old or "")
    if new and not new.endswith("\n"):
        new += "\n"
    new += SITE_CUSTOMIZE_BLOCK
    write_text(sc, new)
    res["modified"] = True
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=None)
    ap.add_argument("--package-only", action="store_true")
    args = ap.parse_args()

    roots: list[tuple[pathlib.Path, str]] = []
    for name in PACKAGE_NAMES:
        r = locate_package(name)
        if r and r.exists():
            roots.append((r, name))

    site_packages = locate_site_packages()
    if site_packages.exists():
        for child in site_packages.iterdir():
            if child.is_dir() and ("ahootsa" in child.name.lower() or child.name.lower().startswith("reachy")):
                if child not in [r[0] for r in roots]:
                    roots.append((child, f"sitepkg:{child.name}"))

    if not args.package_only:
        candidates = []
        if args.project_root:
            candidates.append(pathlib.Path(args.project_root).resolve())
        candidates += [
            pathlib.Path(r"D:\RITXI\5_0_34_ahootsa_completa_consolidada_b"),
            pathlib.Path.cwd(),
        ]
        for c in candidates:
            if c.exists() and c not in [r[0] for r in roots]:
                roots.append((c, "project_root"))

    print(f"[INFO] site-packages: {site_packages}")
    sc_res = install_sitecustomize(site_packages)
    if sc_res["modified"]:
        print(f"[OK] sitecustomize.py actualizado para bloquear pyttsx3/SAPI: {sc_res['path']}")
    elif sc_res["already"]:
        print(f"[OK] sitecustomize.py ya tenia bloqueo pyttsx3/SAPI: {sc_res['path']}")
    else:
        print(f"[WARN] sitecustomize.py sin cambios: {sc_res['path']}")

    summaries = []
    for root, label in roots:
        summaries.append(patch_root(root, label))

    total_modified = sum(s["modified"] for s in summaries) + (1 if sc_res["modified"] else 0)
    total_already = sum(s["already"] for s in summaries) + (1 if sc_res["already"] else 0)
    print("\n[RESUMEN AUDIO 5.0.33]")
    for s in summaries:
        print(f"- {s['label']}: root={s['root']}")
        print(f"  existe={s['exists']} revisados={s['checked']} modificados={s['modified']} ya_parcheados={s['already']} omitidos={s['skipped']}")
        for f in s["files"][:25]:
            print(f"    - {f}")
        if len(s["files"]) > 25:
            print(f"    ... y {len(s['files']) - 25} mas")

    if total_modified <= 0 and total_already <= 0:
        print("[ERROR] No se ha podido aplicar ningun bloqueo de audio Windows.")
        return 3

    print("\n[OK] Audio Windows/navegador bloqueado de forma reforzada.")
    print("[OK] Para que sitecustomize actue, el lanzador 5.0.33 define AHOOTSA_DISABLE_WINDOWS_TTS=1.")
    print("[OK] Cierra y vuelve a abrir la ventana/app para evitar cache del navegador.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
