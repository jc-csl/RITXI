# REPARAR_JUEGOS_PAREJAS_JSON.ps1
# Copia HTML, JSON y herramientas del motor de juegos al perfil instalado.

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Info($Text) { Write-Host "[INFO] $Text" }
function Fail($Text) { Write-Host "[ERROR] $Text" -ForegroundColor Red; exit 1 }

Header "Reparar motor JSON de juegos de parejas"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceProfile = Join-Path $Root "src\ahootsa_realtime_ollama_desktop_app\profiles\ahootsa_realtime_es"

if (-not (Test-Path $SourceProfile)) {
    Fail "No encuentro el perfil fuente: $SourceProfile"
}

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Targets = @(
    (Join-Path $DesktopDir "user_personalities\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "profiles\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles\ahootsa_realtime_es")
)

$Files = @(
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
            foreach ($toolName in @("start_memory_pairs_game","choose_memory_cards","reset_memory_pairs_game","memory_pairs_game_status","list_memory_pairs_games")) {
                $raw = Get-Content $tools -Raw -Encoding UTF8
                if ($raw -notmatch $toolName) {
                    Add-Content -Encoding UTF8 -Path $tools -Value "`n$toolName"
                }
            }
        }
        Info "Reparado: $t"
    }
}

Header "Final"
Write-Host "Cierra Ahootsa y vuelve a abrirla."
Write-Host "Prueba: quiero un juego de parejas de ciudades"
