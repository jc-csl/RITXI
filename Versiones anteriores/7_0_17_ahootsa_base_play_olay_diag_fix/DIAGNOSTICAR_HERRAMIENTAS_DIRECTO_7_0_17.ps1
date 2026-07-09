param(
    [string]$AppVenv = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv"
)
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$Logs = "D:\RITXI\logs"
New-Item -ItemType Directory -Force -Path $Logs | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Out = Join-Path $Logs "AHOOTSA_DIAGNOSTICO_DIRECTO_7_0_17_$Stamp.log"
$Py = Join-Path $AppVenv "Scripts\python.exe"
"Ahootsa diagnóstico directo 7.0.17" | Tee-Object -FilePath $Out
"Python: $Py" | Tee-Object -FilePath $Out -Append
if (-not (Test-Path -LiteralPath $Py)) {
    "ERROR: No encuentro python.exe en $Py" | Tee-Object -FilePath $Out -Append
    exit 1
}
$Tmp = Join-Path $env:TEMP "ahootsa_diag_direct_7_0_17.py"
@'
from __future__ import annotations
import asyncio, importlib, importlib.util, inspect, json, os, sys, sysconfig, traceback
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

print("=== PYTHON / PACKAGE ===")
print("python", sys.version)
print("purelib", sysconfig.get_paths().get("purelib"))
try:
    import ahootsa_realtime_ollama_desktop_app as pkg
    print("package_file", pkg.__file__)
    print("package_version", getattr(pkg, "__version__", "?"))
    root = Path(pkg.__file__).resolve().parent
except Exception as exc:
    print("PACKAGE_IMPORT_ERROR", type(exc).__name__, exc)
    traceback.print_exc()
    raise SystemExit(2)

print("\n=== ARCHIVOS CLAVE ===")
checks = [
    "tools/play_panel_dance_activity.py",
    "tools/list_panel_dances_activities.py",
    "tools/choose_memory_cards.py",
    "tools/start_memory_pairs_game.py",
    "tools/memory_pairs_game_server.py",
    "tools/play_emotion.py",
    "profiles/ahootsa7_realtime_es/play_emotion.py",
    "profiles/ahootsa7_realtime_es/tools.txt",
    "profiles/ahootsa7_realtime_es/instructions.txt",
]
for rel in checks:
    p = root / rel
    print(f"{rel}: exists={p.exists()} path={p}")

print("\n=== COMPROBACIÓN DE CÓDIGO PATCH 7.0.17 ===")
choose = (root / "tools" / "choose_memory_cards.py").read_text(encoding="utf-8", errors="ignore")
panel = (root / "tools" / "play_panel_dance_activity.py").read_text(encoding="utf-8", errors="ignore")
print("choose_has_profile_loader", "_load_profile_play_emotion" in choose)
print("choose_uses_missing_tools_play_emotion", '_load_sibling_module("play_emotion_for_memory", "play_emotion.py")' in choose)
print("panel_loads_profiles", "profiles" in panel and "play_emotion.py" in panel)
print("tools_play_emotion_should_not_exist", (root / "tools" / "play_emotion.py").exists())

print("\n=== TOOLS.TXT PERFIL ===")
try:
    tools = (root / "profiles" / "ahootsa7_realtime_es" / "tools.txt").read_text(encoding="utf-8", errors="ignore").splitlines()
    tools = [t.strip() for t in tools if t.strip() and not t.strip().startswith("#")]
    print("tools_count", len(tools))
    print(json.dumps(tools, ensure_ascii=False, indent=2))
except Exception as exc:
    print("TOOLS_TXT_ERROR", type(exc).__name__, exc)

print("\n=== PLAY_EMOTION PROFILE RESOLVE ===")
try:
    path = root / "profiles" / "ahootsa7_realtime_es" / "play_emotion.py"
    spec = importlib.util.spec_from_file_location("ahootsa_diag_profile_play_emotion", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    for text in ["baile uno", "baile dos", "baile tres", "baile numero dos", "baile número dos", "play", "olay", "play dos", "olay dos", "play tres", "olay tres", "saludo", "saludo ahootsa", "sludo", "sluod", "celebracion", "celebración", "calma", "electrico", "eléctrico"]:
        try:
            print("RESOLVE", repr(text), "=>", mod.resolve_emotion_name(text))
        except Exception as exc:
            print("RESOLVE_ERROR", repr(text), type(exc).__name__, exc)
    try:
        moves = list(mod.list_moves())
        print("moves_count", len(moves))
        print("contains dance1 dance2 dance3", "dance1" in moves, "dance2" in moves, "dance3" in moves)
        print("first_moves", moves[:30])
    except Exception as exc:
        print("LIST_MOVES_ERROR", type(exc).__name__, exc)
except Exception as exc:
    print("PROFILE_PLAY_EMOTION_LOAD_ERROR", type(exc).__name__, exc)
    traceback.print_exc()

print("\n=== LIBRERIA LOCAL EMOCIONES ===")
ds = Path(os.environ.get("AHOOTSA_EMOTIONS_LIBRARY_DIR", r"D:\RITXI\reachy-mini-emotions-library"))
print("dataset_dir", ds, "exists", ds.exists())
for stem in ["dance1", "dance2", "dance3", "welcoming2", "success1", "calming1", "electric1"]:
    print("RESOURCE", stem, "json", (ds / f"{stem}.json").exists(), "ogg", (ds / f"{stem}.ogg").exists())

print("\n=== IMPORT TOOLS DIRECTO ===")
for name in ["list_panel_dances_activities", "play_panel_dance_activity", "start_memory_pairs_game", "choose_memory_cards", "memory_pairs_game_status"]:
    try:
        path = root / "tools" / f"{name}.py"
        spec = importlib.util.spec_from_file_location(f"ahootsa_diag_{name}", path)
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        classes = [v for v in mod.__dict__.values() if isinstance(v, type) and getattr(v, "name", None)]
        print("TOOL_IMPORT_OK", name, "classes", [(c.__name__, getattr(c, "name", None)) for c in classes])
    except Exception as exc:
        print("TOOL_IMPORT_ERROR", name, type(exc).__name__, exc)
        traceback.print_exc()

print("\n=== ENDPOINTS APP 7860 ===")
def get(url):
    try:
        with urlopen(url, timeout=3) as r:
            data = r.read(500).decode("utf-8", "ignore")
            print("HTTP_OK", url, "status", r.status, "body_start", data[:120].replace("\n", " "))
    except HTTPError as exc:
        print("HTTP_ERROR", url, exc.code, exc.reason)
    except Exception as exc:
        print("HTTP_FAIL", url, type(exc).__name__, exc)
for url in [
    "http://127.0.0.1:7860/ahootsa/status",
    "http://127.0.0.1:7860/ahootsa",
    "http://127.0.0.1:7860/memory/state",
    "http://127.0.0.1:7860/memory/page?game_id=animales&reset=0",
]:
    get(url)
'@ | Set-Content -Encoding UTF8 -LiteralPath $Tmp
$RunOut = Join-Path $env:TEMP "ahootsa_diag_direct_7_0_17_output.txt"
& $Py $Tmp *> $RunOut
Get-Content -LiteralPath $RunOut -Encoding UTF8 | Tee-Object -FilePath $Out -Append
"`nLOG: $Out" | Tee-Object -FilePath $Out -Append
Write-Host "Diagnóstico guardado en $Out"
