# DIAGNOSTICAR_EMOCIONES_AUDIO.ps1
# Ubicación actual: subcarpeta test.
# Ejecutar desde la raíz con: powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_EMOCIONES_AUDIO.ps1

# Diagnóstico de emociones con movimiento + audio OGG oficial.
#
# Uso:
#   powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_EMOCIONES_AUDIO.ps1

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Info($Text) { Write-Host "[INFO] $Text" }
function Warn($Text) { Write-Host "[AVISO] $Text" -ForegroundColor Yellow }

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Python = Join-Path $DesktopDir "apps_venv\Scripts\python.exe"

Header "Diagnóstico emociones audio + movimiento"

if (-not (Test-Path $Python)) {
    Write-Host "[ERROR] No existe apps_venv Python: $Python" -ForegroundColor Red
    exit 1
}

$tmp = Join-Path $env:TEMP "diag_emociones_audio_ahootsa.py"

@'
from pathlib import Path
import os, sys, json

print("python=", sys.executable)
try:
    import pygame
    print("pygame=", pygame.version.ver)
except Exception as e:
    print("pygame_error=", repr(e))

profile_dirs = [
    Path(os.environ.get("LOCALAPPDATA", "")) / "Reachy Mini Control" / "user_personalities" / "ahootsa_realtime_es",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Reachy Mini Control" / "profiles" / "ahootsa_realtime_es",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Reachy Mini Control" / "apps_venv" / "Lib" / "site-packages" / "reachy_mini_conversation_app" / "profiles" / "ahootsa_realtime_es",
]
for p in profile_dirs:
    print("profile=", p, "exists=", p.exists(), "play_emotion_py=", (p/"play_emotion.py").exists(), "play_emotion_with_audio_py=", (p/"play_emotion_with_audio.py").exists(), "tools=", (p/"tools.txt").exists())
    if (p/"tools.txt").exists():
        print((p/"tools.txt").read_text(encoding="utf-8"))

# Import the profile-local tool from the installed profile.
profile = profile_dirs[-1]
if not (profile / "play_emotion.py").exists():
    print("ERROR: no está instalado play_emotion.py en el perfil de apps_venv")
    sys.exit(2)

import importlib.util
spec = importlib.util.spec_from_file_location("diag_play_emotion", profile / "play_emotion.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

print("dataset_dir=", mod.get_dataset_dir())
moves = mod.list_moves()
print("moves_count=", len(moves))
print("sample_moves=", moves[:20])
for name in ["success1", "welcoming1", "welcoming2", "laughing2", "dance1"]:
    d = mod.get_dataset_dir()
    print(name, "json=", bool(d and (d/f"{name}.json").exists()), "ogg=", bool(d and (d/f"{name}.ogg").exists()))

# Verifica que se resuelve una emoción.
for intent in ["success", "greeting", "happy", "thinking", "calming"]:
    print("resolve", intent, "=>", mod.resolve_emotion_name(intent))
'@ | Set-Content -Encoding UTF8 $tmp

& $Python $tmp

Remove-Item $tmp -Force -ErrorAction SilentlyContinue

Header "Log play_emotion_audio"
$log = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\ahootsa_logs\play_emotion_audio.log"
if (Test-Path $log) {
    Get-Content $log -Encoding UTF8 -Tail 40
} else {
    Warn "Todavía no existe log. Se creará cuando la app llame a play_emotion."
}

Header "Prueba por voz"
Write-Host "Arranca Ahootsa y prueba:"
Write-Host '  saluda con sonido'
Write-Host '  celebra con una emoción'
Write-Host '  haz una emoción con sonido'
