# REPARAR_HTML_JUEGO_PAREJAS.ps1
# Copia el HTML del juego dentro de todos los perfiles Ahootsa instalados.
# Corrige el mensaje: "No se encontró el HTML del juego."

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Info($Text) { Write-Host "[INFO] $Text" }
function Fail($Text) { Write-Host "[ERROR] $Text" -ForegroundColor Red; exit 1 }

Header "Reparar HTML del juego de parejas"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$HtmlCandidates = @(
    (Join-Path $Root "src\ahootsa_realtime_ollama_desktop_app\profiles\ahootsa_realtime_es\memory_pairs_animales.html"),
    (Join-Path $Root "src\ahootsa_realtime_ollama_desktop_app\games\memory_pairs_animales.html")
)

$HtmlSource = $null
foreach ($h in $HtmlCandidates) {
    if (Test-Path $h) {
        $HtmlSource = $h
        break
    }
}

if (-not $HtmlSource) {
    Fail "No encuentro memory_pairs_animales.html en esta carpeta v0.4.35."
}

Info "HTML origen: $HtmlSource"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Targets = @(
    (Join-Path $DesktopDir "user_personalities\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "profiles\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles\ahootsa_realtime_es")
)

foreach ($t in $Targets) {
    if (Test-Path $t) {
        Copy-Item -Force $HtmlSource (Join-Path $t "memory_pairs_animales.html")
        Info "Copiado en: $t"
    } else {
        Info "No existe todavía: $t"
    }
}

Header "Comprobación"
foreach ($t in $Targets) {
    $f = Join-Path $t "memory_pairs_animales.html"
    if (Test-Path $f) {
        Write-Host "OK  $f"
    }
}

Header "Final"
Write-Host "Cierra Ahootsa, vuelve a abrirla y lanza el juego."
Write-Host "También puedes probar:"
Write-Host "powershell -ExecutionPolicy Bypass -File .\PROBAR_JUEGO_PAREJAS_ANIMALES.ps1"
