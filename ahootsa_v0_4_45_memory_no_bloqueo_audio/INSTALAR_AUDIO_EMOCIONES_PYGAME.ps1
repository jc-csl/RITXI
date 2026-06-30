# INSTALAR_AUDIO_EMOCIONES_PYGAME.ps1
# Instala pygame en el Python de Reachy Mini Desktop para reproducir OGG sin GStreamer.
# No modifica Reachy Mini ni la app oficial.

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Info($Text) { Write-Host "[INFO] $Text" }
function Warn($Text) { Write-Host "[AVISO] $Text" -ForegroundColor Yellow }
function Fail($Text) { Write-Host "[ERROR] $Text" -ForegroundColor Red; exit 1 }

Header "Instalar audio de emociones por pygame/SDL"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$pythons = @(
    (Join-Path $DesktopDir "apps_venv\Scripts\python.exe"),
    (Join-Path $DesktopDir ".venv\Scripts\python.exe"),
    (Join-Path $DesktopDir "cpython-3.12-windows-x86_64-none\python.exe")
) | Where-Object { Test-Path $_ } | Select-Object -Unique

if ($pythons.Count -eq 0) {
    Fail "No se encontraron Python internos de Reachy Mini Desktop."
}

foreach ($py in $pythons) {
    Info "Comprobando pygame en: $py"
    & $py -c "import pygame; print('pygame=', pygame.version.ver)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Info "pygame ya está instalado."
        continue
    }

    Info "Instalando pygame en: $py"
    & $py -m pip install pygame
    if ($LASTEXITCODE -ne 0) {
        Warn "Instalación normal falló. Reintentando con --break-system-packages..."
        & $py -m pip install --break-system-packages pygame
    }

    & $py -c "import pygame; print('pygame=', pygame.version.ver)"
    if ($LASTEXITCODE -ne 0) {
        Warn "No se pudo verificar pygame en $py"
    }
}

Header "Final"
Write-Host "pygame instalado/verificado."
Write-Host "Prueba ahora:"
Write-Host "powershell -ExecutionPolicy Bypass -File .\test\PROBAR_AUDIO_EMOCION_PYGAME.ps1"


Header "Configurar backend Ahootsa"
[Environment]::SetEnvironmentVariable("AHOOTSA_EMOTION_AUDIO_BACKEND", "pygame", "User")
[Environment]::SetEnvironmentVariable("AHOOTSA_PYGAME_AUDIO_DRIVERS", "directsound,wasapi,winmm,default", "User")
[Environment]::SetEnvironmentVariable("AHOOTSA_EMOTION_AUDIO_VOLUME", "1.0", "User")
Info "AHOOTSA_EMOTION_AUDIO_BACKEND=pygame"
Info "AHOOTSA_PYGAME_AUDIO_DRIVERS=directsound,wasapi,winmm,default"
Info "AHOOTSA_EMOTION_AUDIO_VOLUME=1.0"
