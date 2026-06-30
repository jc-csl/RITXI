# FORZAR_INICIO_CASTELLANO_SOHEE.ps1
# Fuerza saludo inicial en castellano y voz Sohee.
# Motivo: algunas versiones de la app oficial saludan primero desde su perfil default
# con "Hi there, I'm Reachy Mini" antes de cargar el perfil Ahootsa.
# Este script copia greeting/instructions/voice a Ahootsa y, con copia de seguridad,
# cambia el greeting del perfil default oficial para evitar el saludo en inglés.

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Info($Text) { Write-Host "[INFO] $Text" }
function Warn($Text) { Write-Host "[AVISO] $Text" -ForegroundColor Yellow }

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProfileName = "ahootsa_realtime_es"
$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Greeting = "¡Hola! Soy Ahootsa. Estoy lista para ayudarte. ¿Qué quieres hacer?"
$Voice = "Sohee"

Header "Forzar Ahootsa en castellano + Sohee"

$sourceProfile = Join-Path $Root "src\ahootsa_realtime_ollama_desktop_app\profiles\$ProfileName"
$profiles = @(
    $sourceProfile,
    (Join-Path $DesktopDir "user_personalities\$ProfileName"),
    (Join-Path $DesktopDir "profiles\$ProfileName"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\$ProfileName"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles\$ProfileName")
)

foreach ($p in $profiles) {
    if (-not (Test-Path $p)) {
        New-Item -ItemType Directory -Force -Path $p | Out-Null
    }
    Set-Content -Encoding UTF8 -Path (Join-Path $p "voice.txt") -Value $Voice
    Set-Content -Encoding UTF8 -Path (Join-Path $p "greeting.txt") -Value $Greeting
    Info "Ahootsa perfil actualizado: $p"
}

# Variables de usuario por si el backend oficial las lee.
[Environment]::SetEnvironmentVariable("AHOOTSA_VOICE", $Voice, "User")
[Environment]::SetEnvironmentVariable("REACHY_MINI_CUSTOM_PROFILE", $ProfileName, "User")
[Environment]::SetEnvironmentVariable("REACHY_MINI_PROFILE", $ProfileName, "User")
[Environment]::SetEnvironmentVariable("REALTIME_TRANSCRIPTION_LANGUAGE", "es", "User")
[Environment]::SetEnvironmentVariable("OPENAI_REALTIME_VOICE", $Voice, "User")
[Environment]::SetEnvironmentVariable("REACHY_MINI_VOICE", $Voice, "User")

Header "Evitar saludo inicial inglés del perfil default"

$officialProfileRoots = @(
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles")
)

foreach ($rootProfiles in $officialProfileRoots) {
    if (-not (Test-Path $rootProfiles)) { continue }

    $candidateDirs = Get-ChildItem -Path $rootProfiles -Directory -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -in @("default", "starter_profile", "starter", "base")
    }

    foreach ($dir in $candidateDirs) {
        $g = Join-Path $dir.FullName "greeting.txt"
        if (Test-Path $g) {
            $bak = "$g.ahootsa_backup"
            if (-not (Test-Path $bak)) {
                Copy-Item -Force $g $bak
                Info "Backup creado: $bak"
            }
            Set-Content -Encoding UTF8 -Path $g -Value $Greeting
            Info "Greeting default cambiado a castellano: $g"
        }
        $v = Join-Path $dir.FullName "voice.txt"
        if (Test-Path $v) {
            $bakv = "$v.ahootsa_backup"
            if (-not (Test-Path $bakv)) { Copy-Item -Force $v $bakv }
            Set-Content -Encoding UTF8 -Path $v -Value $Voice
            Info "Voice default cambiada a Sohee: $v"
        }
    }
}

Header "Comprobación"
foreach ($p in $profiles) {
    $v = Join-Path $p "voice.txt"
    $g = Join-Path $p "greeting.txt"
    if (Test-Path $v) { Write-Host "$v -> $(Get-Content $v -Raw -Encoding UTF8)" }
    if (Test-Path $g) { Write-Host "$g -> $(Get-Content $g -Raw -Encoding UTF8)" }
}

Header "Final"
Write-Host "Cierra completamente Reachy Mini Desktop y vuelve a abrir Ahootsa."
Write-Host "El saludo esperado es: ¡Hola! Soy Ahootsa..."
