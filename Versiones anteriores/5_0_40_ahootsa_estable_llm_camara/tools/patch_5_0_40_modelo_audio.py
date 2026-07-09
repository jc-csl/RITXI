
import argparse
import os
import pathlib
import sys
from datetime import datetime

DEFAULT_MODEL = "llama3.2:3b"
OLD_MODELS = ["ahootsa-local:latest", "ahootsa-local"]


def log(msg):
    print(f"[5.0.40] {msg}")


def replace_in_file(path: pathlib.Path, model: str):
    try:
        txt = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    new = txt
    for old in OLD_MODELS:
        new = new.replace(old, model)
    # Defaults commonly used by previous scripts
    new = new.replace('os.environ.get("AHOOTSA_OLLAMA_MODEL", "ahootsa-local:latest")', f'os.environ.get("AHOOTSA_OLLAMA_MODEL", "{model}")')
    new = new.replace("os.environ.get('AHOOTSA_OLLAMA_MODEL', 'ahootsa-local:latest')", f"os.environ.get('AHOOTSA_OLLAMA_MODEL', '{model}')")
    if new != txt:
        bak = path.with_suffix(path.suffix + f".bak_5_0_40_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        try:
            bak.write_text(txt, encoding="utf-8", errors="ignore")
        except Exception:
            pass
        path.write_text(new, encoding="utf-8")
        return True
    return False


def find_site_packages():
    roots = []
    try:
        import site
        roots += [pathlib.Path(p) for p in site.getsitepackages()]
    except Exception:
        pass
    try:
        roots.append(pathlib.Path(sys.prefix) / "Lib" / "site-packages")
    except Exception:
        pass
    return [p for p in roots if p.exists()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ollama-model", default=DEFAULT_MODEL)
    ap.add_argument("--provider", default="ollama", choices=["ollama", "hf_local", "auto"])
    ap.add_argument("--hf-model-path", default="")
    args = ap.parse_args()

    os.environ.setdefault("AHOOTSA_LLM_PROVIDER", args.provider)
    os.environ.setdefault("AHOOTSA_OLLAMA_MODEL", args.ollama_model)
    os.environ.setdefault("OLLAMA_MODEL", args.ollama_model)
    os.environ.setdefault("AHOOTSA_OLLAMA_URL", "http://127.0.0.1:11434")
    os.environ.setdefault("AHOOTSA_OLLAMA_TIMEOUT", "18")
    os.environ.setdefault("AHOOTSA_DISABLE_WINDOWS_TTS", "1")
    os.environ.setdefault("AHOOTSA_DISABLE_WINDOWS_BEEP", "1")
    os.environ.setdefault("PYTTSX3_DISABLE", "1")
    os.environ.setdefault("AHOOTSA_AUDIO_UNICO", "1")
    if args.hf_model_path:
        os.environ.setdefault("AHOOTSA_HF_MODEL_PATH", args.hf_model_path)

    changed = []
    for sp in find_site_packages():
        for pkg in ["ahootsa_realtime_ollama_desktop_app", "reachy_mini_conversation_app", "reachy_talk_data"]:
            base = sp / pkg
            if base.exists():
                log(f"Revisando paquete: {base}")
                for ext in ("*.py", "*.js", "*.html", "*.json", "*.txt"):
                    for f in base.rglob(ext):
                        if replace_in_file(f, args.ollama_model):
                            changed.append(str(f))
    log(f"Archivos modificados: {len(changed)}")
    for f in changed[:80]:
        log("  " + f)

    # Create a small sitecustomize safety net so new Python processes inherit sensible defaults.
    for sp in find_site_packages():
        sc = sp / "sitecustomize.py"
        block = f