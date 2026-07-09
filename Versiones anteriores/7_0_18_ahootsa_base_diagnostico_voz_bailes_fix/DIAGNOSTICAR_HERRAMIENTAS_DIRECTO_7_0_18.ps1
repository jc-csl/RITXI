param()
$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONLEGACYWINDOWSSTDIO = "0"
$LogDir = "D:\RITXI\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Out = Join-Path $LogDir "AHOOTSA_DIAGNOSTICO_DIRECTO_7_0_18_$Stamp.log"
$Py = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\apps_venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { $Py = "python" }
Write-Host "Ahootsa diagnostico directo 7.0.18"
Write-Host "Python: $Py"
"Ahootsa diagnostico directo 7.0.18`nPython: $Py`n" | Out-File -Encoding UTF8 -FilePath $Out
$Tmp = Join-Path $env:TEMP "ahootsa_diag_direct_7_0_18.py"
@'
from __future__ import annotations
import sys, os, json, pathlib, importlib.util, urllib.request, traceback
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def p(*args):
    print(*args, flush=True)

def http(url):
    try:
        with urllib.request.urlopen(url, timeout=4) as r:
            raw = r.read().decode("utf-8", "replace")
        p("HTTP_OK", url, "status", getattr(r, "status", "?"), "body_start", raw[:140].replace("\n"," "))
    except Exception as exc:
        p("HTTP_ERR", url, type(exc).__name__, str(exc))

p("=== PYTHON / PACKAGE ===")
p("python", sys.version)
try:
    import site
    p("purelib", site.getsitepackages()[0] if site.getsitepackages() else "?")
except Exception as exc:
    p("site_error", repr(exc))
try:
    import ahootsa_realtime_ollama_desktop_app as pkg
    root = pathlib.Path(pkg.__file__).resolve().parent
    p("package_file", pkg.__file__)
    p("package_version", getattr(pkg, "__version__", "?"))
except Exception as exc:
    p("PACKAGE_IMPORT_ERR", type(exc).__name__, exc)
    raise
files = [
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
p("\n=== ARCHIVOS CLAVE ===")
for rel in files:
    path = root / rel
    p(f"{rel}: exists={path.exists()} path={path}")

p("\n=== COMPROBACION CODIGO PATCH 7.0.18 ===")
choose = (root/"tools/choose_memory_cards.py").read_text(encoding="utf-8", errors="replace")
panel = (root/"tools/play_panel_dance_activity.py").read_text(encoding="utf-8", errors="replace")
pe_txt = (root/"profiles/ahootsa7_realtime_es/play_emotion.py").read_text(encoding="utf-8", errors="replace")
p("choose_has_profile_loader", "profiles" in choose and "play_emotion.py" in choose)
p("choose_uses_missing_tools_play_emotion", "with_name(\"play_emotion.py\")" in choose)
p("panel_loads_profiles", "profiles" in panel and "_load_local_play_emotion" in panel)
p("has_repair_mojibake", "_repair_mojibake" in pe_txt)
p("tools_play_emotion_should_not_exist", (root/"tools/play_emotion.py").exists())

p("\n=== TOOLS.TXT PERFIL ===")
tools = [line.strip() for line in (root/"profiles/ahootsa7_realtime_es/tools.txt").read_text(encoding="utf-8", errors="replace").splitlines() if line.strip() and not line.strip().startswith("#")]
p("tools_count", len(tools))
p(json.dumps(tools, ensure_ascii=False, indent=2))

p("\n=== PLAY_EMOTION PROFILE RESOLVE ===")
pe_path = root/"profiles/ahootsa7_realtime_es/play_emotion.py"
spec = importlib.util.spec_from_file_location("diag_play_emotion_7018", pe_path)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)  # type: ignore
for text in ["baile uno","baile dos","baile tres","baile numero dos","baile número dos","baile nÃºmero dos","play","olay","play dos","olay dos","play tres","olay tres","saludo","saludo ahootsa","sludo","sluod","celebracion","celebración","celebraciÃ³n","calma","electrico","eléctrico","elÃ©ctrico"]:
    try:
        p(f"RESOLVE {text!r} => {mod.resolve_emotion_name(text)}")
    except Exception as exc:
        p(f"RESOLVE_ERR {text!r} {type(exc).__name__}: {exc}")
try:
    moves = mod.list_moves()
    p("moves_count", len(moves))
    p("contains dance1 dance2 dance3", "dance1" in moves, "dance2" in moves, "dance3" in moves)
    p("first_moves", moves[:30])
except Exception as exc:
    p("moves_error", type(exc).__name__, exc)

p("\n=== LIBRERIA LOCAL EMOCIONES ===")
dataset = pathlib.Path(os.getenv("AHOOTSA_EMOTIONS_LIBRARY_DIR", r"D:\RITXI\reachy-mini-emotions-library"))
p("dataset_dir", dataset, "exists", dataset.exists())
for mid in ["dance1","dance2","dance3","welcoming2","success1","calming1","electric1"]:
    p("RESOURCE", mid, "json", (dataset/f"{mid}.json").exists(), "ogg", (dataset/f"{mid}.ogg").exists())

p("\n=== IMPORT TOOLS DIRECTO ===")
for name in ["list_panel_dances_activities","play_panel_dance_activity","start_memory_pairs_game","choose_memory_cards","memory_pairs_game_status"]:
    try:
        path = root/"tools"/f"{name}.py"
        spec = importlib.util.spec_from_file_location(f"diag_{name}", path)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)  # type: ignore
        classes = [(k, getattr(v,"name",None)) for k,v in m.__dict__.items() if isinstance(v,type)]
        p("TOOL_IMPORT_OK", name, "classes", classes)
    except Exception as exc:
        p("TOOL_IMPORT_ERR", name, type(exc).__name__, exc)
        traceback.print_exc()

p("\n=== ENDPOINTS APP 7860 ===")
for url in [
    "http://127.0.0.1:7860/ahootsa/status",
    "http://127.0.0.1:7860/ahootsa",
    "http://127.0.0.1:7860/ahootsa/resolve_activity?activity=baile%20dos",
    "http://127.0.0.1:7860/ahootsa/resolve_activity?activity=olay%20tres",
    "http://127.0.0.1:7860/memory/state",
    "http://127.0.0.1:7860/memory/page?game_id=animales&reset=0",
]:
    http(url)
'@ | Set-Content -Encoding UTF8 -Path $Tmp
# Execute Python without letting stderr lines become PowerShell NativeCommandError.
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $Py
$psi.Arguments = '"' + $Tmp + '"'
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8
$psi.StandardErrorEncoding = [System.Text.Encoding]::UTF8
$p = New-Object System.Diagnostics.Process
$p.StartInfo = $psi
[void]$p.Start()
$stdout = $p.StandardOutput.ReadToEnd()
$stderr = $p.StandardError.ReadToEnd()
$p.WaitForExit()
$combined = $stdout
if ($stderr -and ($stderr.Trim().Length -gt 0)) {
    $combined += "`r`n--- STDERR ---`r`n" + $stderr
}
$combined | Tee-Object -FilePath $Out -Append
if ($p.ExitCode -ne 0) {
    Write-Host "[WARN] Python diagnostico termino con codigo $($p.ExitCode). Revisa el log." -ForegroundColor Yellow
}
Write-Host "LOG: $Out"
Write-Host "Diagnostico guardado en $Out"
