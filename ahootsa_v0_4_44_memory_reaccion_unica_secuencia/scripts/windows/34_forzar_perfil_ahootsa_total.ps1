# FORZAR_PERFIL_AHOOTSA_TOTAL.ps1
# Fuerza Ahootsa como perfil efectivo incluso si Reachy Mini Desktop ignora REACHY_MINI_CUSTOM_PROFILE.
# Copia el perfil completo Ahootsa a:
# - perfiles Ahootsa conocidos
# - perfiles default/starter oficiales con backup
#
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
function Fail($Text) { Write-Host "[ERROR] $Text" -ForegroundColor Red; exit 1 }

Header "Forzar perfil Ahootsa total"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$ProfileName = "ahootsa_realtime_es"
$SourceProfile = Join-Path $Root "src\ahootsa_realtime_ollama_desktop_app\profiles\$ProfileName"

if (-not (Test-Path $SourceProfile)) {
    Fail "No encuentro perfil fuente: $SourceProfile"
}

$RequiredFiles = @(
    "instructions.txt",
    "greeting.txt",
    "voice.txt",
    "tools.txt",
    "ask_ollama.py",
    "start_memory_pairs_game.py",
    "choose_memory_cards.py",
    "memory_pairs_game_server.py",
    "play_emotion.py"
)

foreach ($f in $RequiredFiles) {
    if (-not (Test-Path (Join-Path $SourceProfile $f))) {
        Fail "Falta archivo requerido en perfil fuente: $f"
    }
}

Header "Variables de entorno usuario"

[Environment]::SetEnvironmentVariable("REACHY_MINI_CUSTOM_PROFILE", $ProfileName, "User")
[Environment]::SetEnvironmentVariable("REACHY_MINI_PROFILE", $ProfileName, "User")
[Environment]::SetEnvironmentVariable("REACHY_MINI_PERSONALITY", $ProfileName, "User")
[Environment]::SetEnvironmentVariable("REACHY_MINI_USER_PERSONALITY", $ProfileName, "User")
[Environment]::SetEnvironmentVariable("AHOOTSA_FORCE_DEFAULT_PROFILE", "1", "User")
[Environment]::SetEnvironmentVariable("REALTIME_TRANSCRIPTION_LANGUAGE", "es", "User")
[Environment]::SetEnvironmentVariable("AHOOTSA_VOICE", "Sohee", "User")
[Environment]::SetEnvironmentVariable("OPENAI_REALTIME_VOICE", "Sohee", "User")
[Environment]::SetEnvironmentVariable("REACHY_MINI_VOICE", "Sohee", "User")
[Environment]::SetEnvironmentVariable("AHOOTSA_EMOTION_AUDIO_BACKEND", "pygame", "User")

Info "REACHY_MINI_CUSTOM_PROFILE=$ProfileName"
Info "AHOOTSA_FORCE_DEFAULT_PROFILE=1"
Info "Voz=Sohee"

Header "Copiar perfil Ahootsa por nombre"

$NamedTargets = @(
    (Join-Path $DesktopDir "user_personalities\$ProfileName"),
    (Join-Path $DesktopDir "profiles\$ProfileName"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\$ProfileName"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles\$ProfileName")
)

foreach ($t in $NamedTargets) {
    New-Item -ItemType Directory -Force -Path $t | Out-Null
    Copy-Item -Force -Recurse (Join-Path $SourceProfile "*") $t
    Info "Perfil Ahootsa copiado: $t"
}

Header "Copiar Ahootsa sobre perfiles default/starter con backup"

$ProfileRoots = @(
    (Join-Path $DesktopDir "profiles"),
    (Join-Path $DesktopDir "user_personalities"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\external_content\external_profiles"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\external_content\external_profiles")
)

$FallbackNames = @("default", "starter_profile", "starter", "base")

foreach ($rootProfiles in $ProfileRoots) {
    if (-not (Test-Path $rootProfiles)) { continue }

    foreach ($name in $FallbackNames) {
        $dst = Join-Path $rootProfiles $name

        if (Test-Path $dst) {
            $marker = Join-Path $dst ".ahootsa_backup_created"
            if (-not (Test-Path $marker)) {
                $backup = "$dst.ahootsa_backup"
                if (-not (Test-Path $backup)) {
                    Copy-Item -Recurse -Force $dst $backup
                    Info "Backup creado: $backup"
                }
                Set-Content -Encoding UTF8 -Path $marker -Value $backup
            }
        }

        New-Item -ItemType Directory -Force -Path $dst | Out-Null
        Copy-Item -Force -Recurse (Join-Path $SourceProfile "*") $dst
        Info "Fallback forzado: $dst"
    }
}

Header "Comprobación rápida"

$CheckTargets = @(
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\$ProfileName"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\default"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles\default")
)

foreach ($p in $CheckTargets) {
    Write-Host ""
    Write-Host "Perfil: $p"
    Write-Host " exists=" (Test-Path $p)
    foreach ($f in @("greeting.txt","voice.txt","tools.txt","start_memory_pairs_game.py","choose_memory_cards.py")) {
        $file = Join-Path $p $f
        Write-Host "  $f =" (Test-Path $file)
    }
    $tools = Join-Path $p "tools.txt"
    if (Test-Path $tools) {
        Select-String -Path $tools -Pattern "memory|start_memory|choose_memory|play_emotion_with_audio" -CaseSensitive:$false
    }
}

Header "Final"
Write-Host "Cierra completamente Reachy Mini Desktop."
Write-Host "Vuelve a abrir Ahootsa."
Write-Host "Debe decir: ¡Hola! Soy Ahootsa..."
Write-Host "Y debe conocer: juego de animales, ciudades y alimentos."
