# REPARAR_MEMORY_REACCION_UNICA.ps1
# v0.4.45: repara el juego Memory para evitar doble movimiento/doble sonido en fallo.
# Ejecutar con Reachy Mini Desktop cerrado.

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Info($Text) { Write-Host "[INFO] $Text" }
function Warn($Text) { Write-Host "[AVISO] $Text" -ForegroundColor Yellow }

Header "Reparar Memory reacción única"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$ProfileName = "ahootsa_realtime_es"
$SourceProfile = Join-Path $Root "src\ahootsa_realtime_ollama_desktop_app\profiles\$ProfileName"

Header "Cerrar puerto 7870 si está ocupado"
try {
    Get-NetTCPConnection -LocalPort 7870 -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique |
        ForEach-Object {
            Warn "Cerrando proceso en puerto 7870: $_"
            Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
        }
} catch {}

$Targets = @(
    (Join-Path $DesktopDir "user_personalities\$ProfileName"),
    (Join-Path $DesktopDir "profiles\$ProfileName"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\$ProfileName"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles\$ProfileName"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\default"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles\default")
)

$Files = @(
    "choose_memory_cards.py",
    "start_memory_pairs_game.py",
    "memory_pairs_game_server.py",
    "memory_pairs_generic.html",
    "memory_pairs_animales.html",
    "tools.txt",
    "instructions.txt",
    "animales.json",
    "ciudades.json",
    "alimentos.json"
)

foreach ($t in $Targets) {
    if (-not (Test-Path $t)) { New-Item -ItemType Directory -Force -Path $t | Out-Null }
    foreach ($f in $Files) {
        $src = Join-Path $SourceProfile $f
        if (Test-Path $src) {
            Copy-Item -Force $src (Join-Path $t $f)
        }
    }
    Info "Memory reparado en: $t"
}

Header "Comprobación"
powershell -ExecutionPolicy Bypass -File (Join-Path $Root "test\PROBAR_MEMORY_REACCION_UNICA.ps1")

Header "Final"
Write-Host "Cierra completamente Reachy Mini Desktop y vuelve a abrir Ahootsa."
Write-Host "Prueba: quiero el juego de animales; luego di: uno y tres."
Write-Host "El fallo debe producir un solo movimiento y un solo sonido."
