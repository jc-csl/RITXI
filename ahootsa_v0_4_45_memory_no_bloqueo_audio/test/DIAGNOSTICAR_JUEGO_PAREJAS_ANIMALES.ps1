# DIAGNOSTICAR_JUEGO_PAREJAS_ANIMALES.ps1
# Ubicación actual: subcarpeta test.
# Ejecutar desde la raíz con: powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_JUEGO_PAREJAS_ANIMALES.ps1

# DIAGNOSTICAR_JUEGOS_PAREJAS_JSON.ps1
# Diagnostica instalación de juegos JSON en el perfil Ahootsa.

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$profiles = @(
    (Join-Path $DesktopDir "user_personalities\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "profiles\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles\ahootsa_realtime_es")
)

Header "Perfiles Ahootsa"
foreach ($p in $profiles) {
    Write-Host ""
    Write-Host "Perfil: $p"
    Write-Host "exists=" (Test-Path $p)
    foreach ($f in @("memory_pairs_game_server.py","memory_pairs_generic.html","animales.json","ciudades.json","alimentos.json","start_memory_pairs_game.py","choose_memory_cards.py","list_memory_pairs_games.py","tools.txt")) {
        Write-Host $f "=" (Test-Path (Join-Path $p $f))
    }
    $tools = Join-Path $p "tools.txt"
    if (Test-Path $tools) {
        Select-String -Path $tools -Pattern "memory_pairs|choose_memory|start_memory|list_memory" -CaseSensitive:$false
    }
}

Header "Paquete Ahootsa"
$Python = Join-Path $DesktopDir "apps_venv\Scripts\python.exe"
if (Test-Path $Python) {
    & $Python -c "import importlib.metadata as m; print('version=', m.version('ahootsa-realtime-ollama-desktop-app'))"
}

Header "Prueba"
Write-Host "powershell -ExecutionPolicy Bypass -File .\PROBAR_JUEGOS_PAREJAS_JSON.ps1"
