r"""
Ahootsa 5.0.30 - guardia de audio único Ahootsa.

Objetivo:
- Evitar que las actividades usen simultáneamente la voz del navegador/Windows
  y la voz propia de Ahootsa.
- Bloquear de forma global la API Web Speech del navegador (`window.speechSynthesis.speak`).
- Mantener el audio propio de Ahootsa, normalmente reproducido por backend/TTS propio
  o por elementos <audio> generados por la app.

Por qué no se elimina <audio>:
- La voz Ahootsa puede llegar al navegador como audio normal.
- El problema detectado es la síntesis nativa Windows/navegador, no todos los sonidos.

La corrección se aplica dentro del paquete instalado:
    %LOCALAPPDATA%\Reachy Mini Control\apps_venv\Lib\site-packages\ahootsa_realtime_ollama_desktop_app

y opcionalmente en una carpeta de proyecto indicada con --project-root.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib
import pathlib
import re
import shutil
import sys
from typing import Iterable

PACKAGE_NAME = "ahootsa_realtime_ollama_desktop_app"
MARKER = "Ahootsa 5.0.30 - audio unico Ahootsa"

AUDIO_GUARD_JS = r'''
/* ============================================================
 * Ahootsa 5.0.30 - audio unico Ahootsa
 *
 * Regla global:
 *   - El robot/app Ahootsa es la unica voz de actividades y juegos.
 *   - Se desactiva la voz del navegador/Windows mediante Web Speech API.
 *
 * Corrige casos como el juego de parejas, donde sonaba a la vez:
 *   1) audio/voz Ahootsa
 *   2) voz Windows/navegador (`speechSynthesis`)
 *
 * No bloquea etiquetas <audio>, porque pueden ser la salida real de Ahootsa.
 * ============================================================ */
(function () {
  try {
    if (typeof window === "undefined") return;

    var PATCH_MARKER = "__AHOOTSA_5029_AUDIO_UNICO_AHOOTSA__";
    if (window[PATCH_MARKER]) return;
    window[PATCH_MARKER] = true;

    window.AHOOTSA_AUDIO_POLICY = window.AHOOTSA_AUDIO_POLICY || {};
    window.AHOOTSA_AUDIO_POLICY.onlyAhootsaVoice = true;
    window.AHOOTSA_AUDIO_POLICY.blockWindowsSpeechSynthesis = true;
    window.AHOOTSA_AUDIO_POLICY.version = "5.0.30";

    function logBlocked(detail) {
      try {
        if (window.AHOOTSA_DEBUG_AUDIO === true) {
          console.info("[Ahootsa 5.0.30] Voz Windows/navegador bloqueada:", detail || "speechSynthesis.speak");
        }
      } catch (e) {}
    }

    function cancelWindowsSpeech() {
      try {
        if (window.speechSynthesis && typeof window.speechSynthesis.cancel === "function") {
          window.speechSynthesis.cancel();
        }
      } catch (e) {}
    }

    function patchSpeechSynthesis() {
      try {
        if (!window.speechSynthesis) return;
        var synth = window.speechSynthesis;

        if (!window.__AHOOTSA_ORIGINAL_SPEECH_SYNTHESIS_SPEAK__) {
          try { window.__AHOOTSA_ORIGINAL_SPEECH_SYNTHESIS_SPEAK__ = synth.speak ? synth.speak.bind(synth) : null; } catch (e) {}
        }
        if (!window.__AHOOTSA_ORIGINAL_SPEECH_SYNTHESIS_CANCEL__) {
          try { window.__AHOOTSA_ORIGINAL_SPEECH_SYNTHESIS_CANCEL__ = synth.cancel ? synth.cancel.bind(synth) : null; } catch (e) {}
        }

        var blockedSpeak = function (utterance) {
          logBlocked(utterance && (utterance.text || utterance.lang || utterance.voice && utterance.voice.name));
          cancelWindowsSpeech();
          return undefined;
        };
        blockedSpeak.__ahootsaBlockedSpeak5029 = true;

        try {
          synth.speak = blockedSpeak;
        } catch (e1) {
          try {
            Object.defineProperty(synth, "speak", {
              value: blockedSpeak,
              configurable: true,
              writable: true
            });
          } catch (e2) {}
        }

        cancelWindowsSpeech();
      } catch (e) {}
    }

    patchSpeechSynthesis();

    // Algunas librerias reescriben speechSynthesis.speak tras cargar la pantalla.
    // Reaplicamos durante los primeros segundos y al volver a foco/actividad.
    var tries = 0;
    var timer = window.setInterval(function () {
      tries += 1;
      patchSpeechSynthesis();
      if (tries >= 40) window.clearInterval(timer);
    }, 250);

    try { window.addEventListener("focus", patchSpeechSynthesis, true); } catch (e) {}
    try { document.addEventListener("visibilitychange", patchSpeechSynthesis, true); } catch (e) {}
    try { document.addEventListener("DOMContentLoaded", patchSpeechSynthesis, true); } catch (e) {}

    // API explicita por si alguna actividad quiere comprobar la politica.
    window.ahootsaAudio = window.ahootsaAudio || {};
    window.ahootsaAudio.isWindowsSpeechBlocked = function () { return true; };
    window.ahootsaAudio.cancelWindowsSpeech = cancelWindowsSpeech;
  } catch (e) {}
})();
/* ============================================================
 * Fin Ahootsa 5.0.30 - audio unico Ahootsa
 * ============================================================ */
'''.strip() + "\n"

INLINE_SCRIPT = "<script>\n" + AUDIO_GUARD_JS + "</script>\n"

TEXT_SUFFIXES = {
    ".html", ".htm", ".js", ".mjs", ".jsx", ".ts", ".tsx", ".vue", ".svelte"
}
HTML_SUFFIXES = {".html", ".htm"}
JS_LIKE_SUFFIXES = {".js", ".mjs", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}

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
    path.write_text(text, encoding="utf-8", newline="")


def backup_file(path: pathlib.Path) -> pathlib.Path:
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_name(path.name + f".bak_5_0_30_{stamp}")
    shutil.copy2(path, backup)
    return backup


def iter_candidate_files(root: pathlib.Path) -> Iterable[pathlib.Path]:
    if not root.exists():
        return []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        # Evitar ficheros gigantes generados. El guardia debe estar en fuentes/frontend.
        try:
            if path.stat().st_size > 4_000_000:
                continue
        except Exception:
            continue
        yield path


def looks_relevant_js(text: str) -> bool:
    needles = (
        "speechSynthesis",
        "SpeechSynthesisUtterance",
        "responsiveVoice",
        "speak(",
        "voz",
        "voice",
        "audio",
        "actividad",
        "juego",
        "parejas",
    )
    lower = text.lower()
    return any(n.lower() in lower for n in needles)


def inject_into_html(path: pathlib.Path, text: str) -> tuple[str, str]:
    if MARKER in text or "__AHOOTSA_5029_AUDIO_UNICO_AHOOTSA__" in text:
        return text, "already"

    if re.search(r"</head\s*>", text, flags=re.I):
        new = re.sub(r"</head\s*>", INLINE_SCRIPT + "</head>", text, count=1, flags=re.I)
        return new, "html_head"
    if re.search(r"</body\s*>", text, flags=re.I):
        new = re.sub(r"</body\s*>", INLINE_SCRIPT + "</body>", text, count=1, flags=re.I)
        return new, "html_body"
    return INLINE_SCRIPT + text, "html_prepend"


def inject_into_js(path: pathlib.Path, text: str) -> tuple[str, str]:
    if MARKER in text or "__AHOOTSA_5029_AUDIO_UNICO_AHOOTSA__" in text:
        return text, "already"
    if not looks_relevant_js(text):
        return text, "skip_not_relevant"
    return AUDIO_GUARD_JS + "\n" + text, "js_prepend"


def patch_root(root: pathlib.Path, label: str) -> dict:
    result = {
        "label": label,
        "root": str(root),
        "exists": root.exists(),
        "checked": 0,
        "modified": 0,
        "already": 0,
        "skipped": 0,
        "backups": [],
        "files": [],
    }
    if not root.exists():
        return result

    # Guard JS independiente para poder inspeccionarlo facilmente.
    try:
        guard_path = root / "ahootsa_audio_guard_5_0_30.js"
        if not guard_path.exists() or "__AHOOTSA_5029_AUDIO_UNICO_AHOOTSA__" not in (read_text(guard_path) or ""):
            if guard_path.exists():
                result["backups"].append(str(backup_file(guard_path)))
            write_text(guard_path, AUDIO_GUARD_JS)
            result["modified"] += 1
            result["files"].append(str(guard_path))
    except Exception as exc:
        print(f"[WARN] No he podido crear guard JS en {root}: {exc}")

    for path in iter_candidate_files(root):
        result["checked"] += 1
        text = read_text(path)
        if text is None:
            result["skipped"] += 1
            continue

        suffix = path.suffix.lower()
        if suffix in HTML_SUFFIXES:
            new, mode = inject_into_html(path, text)
        elif suffix in JS_LIKE_SUFFIXES:
            new, mode = inject_into_js(path, text)
        else:
            result["skipped"] += 1
            continue

        if mode == "already":
            result["already"] += 1
            continue
        if mode.startswith("skip"):
            result["skipped"] += 1
            continue
        if new != text:
            try:
                result["backups"].append(str(backup_file(path)))
                write_text(path, new)
                result["modified"] += 1
                result["files"].append(str(path))
                print(f"[OK] {label}: {mode}: {path}")
            except Exception as exc:
                print(f"[WARN] No he podido modificar {path}: {exc}")
                result["skipped"] += 1

    return result


def locate_package_root() -> pathlib.Path:
    pkg = importlib.import_module(PACKAGE_NAME)
    return pathlib.Path(pkg.__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=None, help="Carpeta de proyecto Ahootsa 5_0_25 a parchear tambien, si existe.")
    parser.add_argument("--package-only", action="store_true", help="Solo parchea el paquete instalado en apps_venv.")
    args = parser.parse_args()

    try:
        package_root = locate_package_root()
    except Exception as exc:
        print(f"[ERROR] No he podido importar/localizar {PACKAGE_NAME}: {exc}")
        return 2

    roots: list[tuple[pathlib.Path, str]] = [(package_root, "paquete_instalado")]

    if not args.package_only:
        if args.project_root:
            pr = pathlib.Path(args.project_root).resolve()
            if pr.exists():
                roots.append((pr, "project_root"))
            else:
                print(f"[WARN] --project-root no existe: {pr}")
        else:
            # Heuristica para el caso habitual del usuario.
            for candidate in (
                pathlib.Path(r"D:\RITXI\5_0_25_ahootsa_logs_simples_actividades_recuperadas"),
                pathlib.Path.cwd(),
            ):
                if candidate.exists() and candidate not in [r[0] for r in roots]:
                    roots.append((candidate.resolve(), "project_root_auto"))

    print(f"[INFO] Paquete Ahootsa: {package_root}")
    summaries = []
    for root, label in roots:
        summaries.append(patch_root(root, label))

    total_modified = sum(s["modified"] for s in summaries)
    print("\n[RESUMEN]")
    for s in summaries:
        print(f"- {s['label']}: root={s['root']}")
        print(f"  existe={s['exists']} revisados={s['checked']} modificados={s['modified']} ya_parcheados={s['already']} omitidos={s['skipped']}")
        if s["files"]:
            print("  archivos modificados:")
            for f in s["files"][:20]:
                print(f"    - {f}")
            if len(s["files"]) > 20:
                print(f"    ... y {len(s['files']) - 20} mas")

    if total_modified <= 0 and not any(s["already"] for s in summaries):
        print("[ERROR] No se ha modificado nada. No he encontrado HTML/JS relevante donde insertar el guardia de audio.")
        return 3

    print("\n[OK] Guardia de audio unico Ahootsa aplicado.")
    print("[OK] La voz Windows/navegador speechSynthesis queda bloqueada globalmente.")
    print("[OK] El audio propio de Ahootsa por <audio>/backend no se bloquea.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
