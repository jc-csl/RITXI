# PROBAR_AUDIO_EMOCION_PYGAME.ps1
# Ubicación actual: subcarpeta test.
# Ejecutar desde la raíz con: powershell -ExecutionPolicy Bypass -File .\test\PROBAR_AUDIO_EMOCION_PYGAME.ps1

# Reproduce un OGG oficial con pygame/SDL, evitando GStreamer.
# Debe sonar por los altavoces de Windows.

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Info($Text) { Write-Host "[INFO] $Text" }
function Fail($Text) { Write-Host "[ERROR] $Text" -ForegroundColor Red; exit 1 }

Header "Prueba audio emoción con pygame"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Python = Join-Path $DesktopDir "apps_venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Fail "No existe apps_venv Python: $Python"
}

$Ogg = "D:\RITXI\reachy-mini-emotions-library\welcoming2.ogg"
if (-not (Test-Path $Ogg)) {
    $Ogg = "D:\RITXI\reachy-mini-emotions-library\success1.ogg"
}
if (-not (Test-Path $Ogg)) {
    Fail "No encuentro OGG oficial en D:\RITXI\reachy-mini-emotions-library"
}

$tmp = Join-Path $env:TEMP "probar_audio_emocion_pygame.py"

@'
import sys, time, os
ogg = sys.argv[1]
print("python=", sys.executable)
print("ogg=", ogg)

try:
    import pygame
except Exception as e:
    print("ERROR pygame import:", repr(e))
    sys.exit(2)

try:
    pygame.mixer.init(frequency=48000, size=-16, channels=2, buffer=1024)
    print("mixer=", pygame.mixer.get_init())
    snd = pygame.mixer.Sound(ogg)
    ch = snd.play()
    if ch is None:
        print("ERROR: no free channel")
        sys.exit(3)
    print("OK: reproduciendo durante 4 segundos")
    t0 = time.time()
    while time.time() - t0 < 3.0 and ch.get_busy():
        time.sleep(0.1)
    pygame.mixer.quit()
    print("FIN")
except Exception as e:
    print("ERROR audio:", type(e).__name__, str(e))
    sys.exit(4)
'@ | Set-Content -Encoding UTF8 $tmp

& $Python $tmp $Ogg

Remove-Item $tmp -Force -ErrorAction SilentlyContinue

Header "Final"
Write-Host "Si has oído un sonido, pygame/SDL funciona y v0.4.39 puede evitar GStreamer para emociones."
