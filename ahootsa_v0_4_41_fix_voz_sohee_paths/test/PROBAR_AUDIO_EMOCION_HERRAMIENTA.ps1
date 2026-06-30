# PROBAR_AUDIO_EMOCION_HERRAMIENTA.ps1
# Prueba el audio de emociones usando la herramienta local play_emotion.py.
# No necesita robot físico. Debe sonar un OGG por los altavoces de Windows.

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Fail($Text) { Write-Host "[ERROR] $Text" -ForegroundColor Red; exit 1 }

Header "Probar audio de herramienta de emoción"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Python = Join-Path $DesktopDir "apps_venv\Scripts\python.exe"
$Profile = Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es"
$ToolPy = Join-Path $Profile "play_emotion.py"

if (-not (Test-Path $Python)) { Fail "No existe Python apps_venv: $Python" }
if (-not (Test-Path $ToolPy)) { Fail "No existe play_emotion.py instalado: $ToolPy" }

$tmp = Join-Path $env:TEMP "test_ahootsa_emotion_audio_tool.py"

@'
import importlib.util, sys, time, json, os
from pathlib import Path

tool_py = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("ahootsa_test_play_emotion_audio", tool_py)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

print("tool_py=", tool_py)
print("backend_env=", os.getenv("AHOOTSA_EMOTION_AUDIO_BACKEND"))
print("drivers_env=", os.getenv("AHOOTSA_PYGAME_AUDIO_DRIVERS"))

dataset = mod.get_dataset_dir()
print("dataset_dir=", dataset)
if not dataset:
    print("ERROR: no se encuentra la librería de emociones.")
    sys.exit(2)

move = mod.resolve_emotion_name("greeting") or "welcoming2"
ogg = Path(dataset) / f"{move}.ogg"
print("move=", move)
print("ogg=", ogg, "exists=", ogg.exists())
if not ogg.exists():
    sys.exit(3)

result = mod._play_ogg_with_pygame(ogg)
print("audio_result=", json.dumps(result, ensure_ascii=False, indent=2))
if not result.get("ok"):
    sys.exit(4)

print("Reproduciendo 4 segundos...")
time.sleep(4)
print("FIN")
'@ | Set-Content -Encoding UTF8 $tmp

& $Python $tmp $ToolPy
$code = $LASTEXITCODE
Remove-Item $tmp -Force -ErrorAction SilentlyContinue

Header "Resultado"
if ($code -eq 0) {
    Write-Host "OK. Si has oído sonido, el audio pygame funciona."
} else {
    Write-Host "La prueba ha fallado. Código: $code" -ForegroundColor Red
    Write-Host "Revisa el log: $DesktopDir\ahootsa_logs\play_emotion_audio.log"
}
exit $code
