# REPARAR_MEMORY_START_SERVER.ps1
# Corrige:
# AttributeError: module 'ahootsa_memory_pairs_game_server' has no attribute 'start_server'
#
# Debe ejecutarse con Reachy Mini Desktop cerrado.

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

Header "Reparar Memory start_server"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceProfile = Join-Path $Root "src\ahootsa_realtime_ollama_desktop_app\profiles\ahootsa_realtime_es"

if (-not (Test-Path $SourceProfile)) {
    Fail "No encuentro perfil fuente: $SourceProfile"
}

Header "Cerrar proceso que use puerto 7870"
$conns = Get-NetTCPConnection -LocalPort 7870 -State Listen -ErrorAction SilentlyContinue
foreach ($conn in $conns) {
    try {
        Info "Cerrando PID $($conn.OwningProcess) en puerto 7870"
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    } catch {
        Warn "No se pudo cerrar PID $($conn.OwningProcess)"
    }
}

Header "Copiar servidor y herramientas"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Targets = @(
    (Join-Path $DesktopDir "user_personalities\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "profiles\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles\ahootsa_realtime_es")
)

$Files = @(
    "voice.txt",
    "memory_pairs_game_server.py",
    "memory_pairs_generic.html",
    "memory_pairs_animales.html",
    "animales.json",
    "ciudades.json",
    "alimentos.json",
    "start_memory_pairs_game.py",
    "choose_memory_cards.py",
    "reset_memory_pairs_game.py",
    "memory_pairs_game_status.py",
    "list_memory_pairs_games.py",
    "hint_memory_pairs_game.py",
    "actividades_disponibles.txt"
)

foreach ($t in $Targets) {
    if (Test-Path $t) {
        foreach ($f in $Files) {
            $src = Join-Path $SourceProfile $f
            if (Test-Path $src) {
                Copy-Item -Force $src (Join-Path $t $f)
            }
        }
        $tools = Join-Path $t "tools.txt"
        if (Test-Path $tools) {
            foreach ($toolName in @("start_memory_pairs_game","choose_memory_cards","reset_memory_pairs_game","memory_pairs_game_status","list_memory_pairs_games","hint_memory_pairs_game")) {
                $raw = Get-Content $tools -Raw -Encoding UTF8
                if ($raw -notmatch $toolName) {
                    Add-Content -Encoding UTF8 -Path $tools -Value "`n$toolName"
                }
            }
        }
        Info "Reparado: $t"
    }
}

Header "Verificar start_server"

$Python = Join-Path $DesktopDir "apps_venv\Scripts\python.exe"
$ServerPy = Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es\memory_pairs_game_server.py"

if (-not (Test-Path $Python)) {
    Fail "No existe Python apps_venv: $Python"
}
if (-not (Test-Path $ServerPy)) {
    Fail "No existe servidor instalado: $ServerPy"
}

$tmp = Join-Path $env:TEMP "verify_memory_start_server_ahootsa.py"
@'
import importlib.util, sys, json
from pathlib import Path

server_py = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("verify_memory_pairs_game_server", server_py)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

print("server_py=", server_py)
print("has_start_server=", hasattr(mod, "start_server"))
print("has_status=", hasattr(mod, "status"))
print("self_test=", json.dumps(mod._self_test(), ensure_ascii=False))

if not hasattr(mod, "start_server"):
    sys.exit(2)
'@ | Set-Content -Encoding UTF8 $tmp

& $Python $tmp $ServerPy
$code = $LASTEXITCODE
Remove-Item $tmp -Force -ErrorAction SilentlyContinue

if ($code -ne 0) {
    Fail "La verificación start_server ha fallado."
}

Header "Final"
Write-Host "Reparación OK."
Write-Host "Ahora cierra completamente Reachy Mini Desktop si seguía abierto."
Write-Host "Abre Reachy Mini Desktop y prueba: quiero el juego de animales"
Write-Host ""
Write-Host "También puedes probar sin Desktop:"
Write-Host "powershell -ExecutionPolicy Bypass -File .\PROBAR_MEMORY_START_SERVER.ps1"
