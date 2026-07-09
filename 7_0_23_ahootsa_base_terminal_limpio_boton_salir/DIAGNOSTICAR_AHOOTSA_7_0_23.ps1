param(
    [switch]$Deep
)
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogRoot = "D:\RITXI\logs"
New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Out = Join-Path $LogRoot "AHOOTSA_DIAGNOSTICO_GENERAL_7_0_23_$Stamp.log"
$Py = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv\Scripts\python.exe"
"Ahootsa diagnóstico general 7.0.23" | Set-Content -Encoding UTF8 $Out
"Root: $Root" | Add-Content -Encoding UTF8 $Out
"Python: $Py" | Add-Content -Encoding UTF8 $Out

$Code = @'
from pathlib import Path
import importlib, json, sys, os, urllib.request
print("=== PACKAGE ===")
import ahootsa_realtime_ollama_desktop_app as pkg
root = Path(pkg.__file__).resolve().parent
print("version", getattr(pkg, "__version__", "?"))
print("root", root)
print("tools_py", len(list((root/"tools").glob("*.py"))))
for rel in ["data/memory/games", "data/communication", "data/dances", "config/memory", "config/dances", "routes", "services", "templates/memory", "legacy"]:
    p = root / rel
    print(rel, "exists", p.exists(), "files", len([x for x in p.rglob("*") if x.is_file()]) if p.exists() else 0)
print("tools_play_emotion_exists", (root/"tools"/"play_emotion.py").exists())
print("profile_play_emotion_exists", (root/"profiles"/"ahootsa7_realtime_es"/"play_emotion.py").exists())
print("memory_catalogs", sorted(p.name for p in (root/"data"/"memory"/"games").glob("*.json")))
print("communication_catalog_exists", (root/"data"/"communication"/"communication_activities_catalog.json").exists())
print("dance_catalogs", sorted(p.name for p in (root/"data"/"dances").glob("*.json")))
print("=== ENDPOINTS ===")
for url in ["http://127.0.0.1:7860/ahootsa/status", "http://127.0.0.1:7860/memory/state", "http://127.0.0.1:7860/communication/levels", "http://127.0.0.1:7860/ahootsa/resolve_activity?activity=baile%20dos"]:
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            body = r.read(160).decode("utf-8", "replace").replace("\n", " ")
        print("HTTP_OK", url, r.status, body)
    except Exception as exc:
        print("HTTP_ERR", url, type(exc).__name__, exc)
'@
$Tmp = Join-Path $env:TEMP "ahootsa_diag_general_7_0_23.py"
Set-Content -Encoding UTF8 -Path $Tmp -Value $Code
& $Py $Tmp 2>&1 | ForEach-Object { $_.ToString() } | Add-Content -Encoding UTF8 $Out
"LOG: $Out"
