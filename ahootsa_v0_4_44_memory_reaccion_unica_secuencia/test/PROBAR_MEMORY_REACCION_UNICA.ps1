# PROBAR_MEMORY_REACCION_UNICA.ps1
# Comprueba que los archivos de Memory contienen la protección anti-duplicado.

$ErrorActionPreference = "Continue"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Profile = Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es"
$Choose = Join-Path $Profile "choose_memory_cards.py"
$Server = Join-Path $Profile "memory_pairs_game_server.py"

Write-Host "choose_memory_cards.py =" (Test-Path $Choose)
Write-Host "memory_pairs_game_server.py =" (Test-Path $Server)

if (Test-Path $Choose) {
    $txt = Get-Content -Raw -Encoding UTF8 $Choose
    Write-Host "anti duplicate window =" ($txt -match "_DUPLICATE_WINDOW_SECONDS")
    Write-Host "duplicate_ignored =" ($txt -match "duplicate_ignored")
    Write-Host "no extra emotion instruction =" ($txt -match "No llames a play_emotion")
    Write-Host "post flip delay 1.2 =" ($txt -match "1.2")
}

if (Test-Path $Server) {
    $txt = Get-Content -Raw -Encoding UTF8 $Server
    Write-Host "repeat_miss =" ($txt -match "repeat_miss")
    Write-Host "reveal seconds 4 =" ($txt -match "REVEAL_SECONDS")
}

Write-Host ""
Write-Host "Si todo sale True, cierra Desktop y prueba por voz."
