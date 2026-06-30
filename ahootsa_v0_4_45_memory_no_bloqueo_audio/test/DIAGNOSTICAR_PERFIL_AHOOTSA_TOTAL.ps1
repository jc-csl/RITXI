# DIAGNOSTICAR_PERFIL_AHOOTSA_TOTAL.ps1
# Comprueba si el perfil activo/instalado contiene identidad Ahootsa y herramientas del juego Memory.

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$ProfileName = "ahootsa_realtime_es"

Header "Variables"
foreach ($v in @(
    "REACHY_MINI_CUSTOM_PROFILE",
    "REACHY_MINI_PROFILE",
    "REACHY_MINI_PERSONALITY",
    "REACHY_MINI_USER_PERSONALITY",
    "AHOOTSA_FORCE_DEFAULT_PROFILE",
    "REALTIME_TRANSCRIPTION_LANGUAGE",
    "AHOOTSA_VOICE"
)) {
    Write-Host "$v=" ([Environment]::GetEnvironmentVariable($v, "User"))
}

Header "Perfiles a comprobar"

$paths = @(
    (Join-Path $DesktopDir "user_personalities\$ProfileName"),
    (Join-Path $DesktopDir "profiles\$ProfileName"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\$ProfileName"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles\$ProfileName"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\default"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles\default"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\external_content\external_profiles\starter_profile")
)

foreach ($p in $paths) {
    Write-Host ""
    Write-Host "Perfil: $p"
    Write-Host " exists=" (Test-Path $p)
    if (-not (Test-Path $p)) { continue }

    foreach ($f in @("greeting.txt","voice.txt","instructions.txt","tools.txt","start_memory_pairs_game.py","choose_memory_cards.py","memory_pairs_game_server.py")) {
        $file = Join-Path $p $f
        Write-Host "  $f =" (Test-Path $file)
    }

    $g = Join-Path $p "greeting.txt"
    if (Test-Path $g) {
        $content = Get-Content $g -Raw -Encoding UTF8
        Write-Host "  greeting: $content"
    }

    $instr = Join-Path $p "instructions.txt"
    if (Test-Path $instr) {
        Select-String -Path $instr -Pattern "Ahootsa|juego de parejas|Memory|Reachy Mini" -CaseSensitive:$false | Select-Object -First 5
    }

    $tools = Join-Path $p "tools.txt"
    if (Test-Path $tools) {
        Select-String -Path $tools -Pattern "start_memory_pairs_game|choose_memory_cards|play_emotion_with_audio|ask_ollama" -CaseSensitive:$false
    }
}

Header "Paquete instalado"
$Python = Join-Path $DesktopDir "apps_venv\Scripts\python.exe"
if (Test-Path $Python) {
    & $Python -c "import importlib.metadata as m; print('ahootsa version=', m.version('ahootsa-realtime-ollama-desktop-app'))"
}
