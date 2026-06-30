# FORZAR_VOZ_SOHEE_TOTAL.ps1
# Fuerza Sohee incluso si Reachy Desktop selecciona Aiden por ser la primera voz de la lista.
# v0.4.41: corregido problema de caracteres no válidos en rutas por secuencias de escape.

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Info($Text) { Write-Host "[INFO] $Text" }
function Warn($Text) { Write-Host "[AVISO] $Text" -ForegroundColor Yellow }

function Join-Many([string[]]$Parts) {
    if ($Parts.Count -eq 0) { return "" }
    $p = $Parts[0]
    for ($i = 1; $i -lt $Parts.Count; $i++) {
        $p = Join-Path $p $Parts[$i]
    }
    return $p
}

function Safe-SetVoiceFile([string]$ProfilePath, [string]$Voice) {
    if ([string]::IsNullOrWhiteSpace($ProfilePath)) { return }
    try {
        if (-not (Test-Path -LiteralPath $ProfilePath)) {
            New-Item -ItemType Directory -Force -Path $ProfilePath | Out-Null
        }
        $voiceFile = Join-Path $ProfilePath "voice.txt"
        Set-Content -Encoding UTF8 -Path $voiceFile -Value $Voice
        Info "voice.txt -> $voiceFile"
    } catch {
        Warn "No se pudo escribir voice.txt en: $ProfilePath"
        Warn $_.Exception.Message
    }
}

Header "Forzar voz Sohee total"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$ProfileName = "ahootsa_realtime_es"
$Voice = "Sohee"

Header "Variables de entorno"
foreach ($name in @(
    "AHOOTSA_VOICE",
    "OPENAI_REALTIME_VOICE",
    "REACHY_MINI_VOICE",
    "VOICE",
    "REALTIME_VOICE",
    "TTS_VOICE",
    "AUDIO_VOICE"
)) {
    [Environment]::SetEnvironmentVariable($name, $Voice, "User")
    [Environment]::SetEnvironmentVariable($name, $Voice, "Process")
    Info "$name=$Voice"
}

Header "voice.txt en perfiles conocidos"

$profiles = @(
    (Join-Many @($Root, "src", "ahootsa_realtime_ollama_desktop_app", "profiles", $ProfileName)),
    (Join-Many @($DesktopDir, "user_personalities", $ProfileName)),
    (Join-Many @($DesktopDir, "profiles", $ProfileName)),
    (Join-Many @($DesktopDir, "apps_venv", "Lib", "site-packages", "reachy_mini_conversation_app", "profiles", $ProfileName)),
    (Join-Many @($DesktopDir, "apps_venv", "Lib", "site-packages", "reachy_talk_data", "profiles", $ProfileName)),
    (Join-Many @($DesktopDir, "apps_venv", "Lib", "site-packages", "reachy_mini_conversation_app", "profiles", "default")),
    (Join-Many @($DesktopDir, "apps_venv", "Lib", "site-packages", "reachy_talk_data", "profiles", "default")),
    (Join-Many @($DesktopDir, "apps_venv", "Lib", "site-packages", "reachy_mini_conversation_app", "external_content", "external_profiles", "starter_profile"))
)

foreach ($p in $profiles) {
    Safe-SetVoiceFile -ProfilePath $p -Voice $Voice
}

Header "Buscar configuraciones con Aiden"

$extensions = @("*.json","*.toml","*.yaml","*.yml","*.ini","*.cfg","*.txt","*.env")
$scanRoots = @(
    $DesktopDir,
    (Join-Many @($DesktopDir, "apps_venv", "Lib", "site-packages", "reachy_mini_conversation_app")),
    (Join-Many @($DesktopDir, "apps_venv", "Lib", "site-packages", "reachy_talk_data"))
)

foreach ($r in $scanRoots) {
    if (-not (Test-Path -LiteralPath $r)) { continue }
    foreach ($ext in $extensions) {
        Get-ChildItem -Path $r -Filter $ext -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
            $file = $_.FullName
            try {
                $raw = Get-Content -Raw -Encoding UTF8 -LiteralPath $file
            } catch {
                return
            }

            if (($raw -match "Aiden|aiden") -and ($raw -match "voice|Voice|VOICE|voices")) {
                $backup = "$file.ahootsa_voice_backup"
                if (-not (Test-Path -LiteralPath $backup)) {
                    Copy-Item -Force -LiteralPath $file -Destination $backup
                }

                $new = $raw
                $new = $new -replace '"Aiden"\s*,\s*"Sohee"', '"Sohee", "Aiden"'
                $new = $new -replace "'Aiden'\s*,\s*'Sohee'", "'Sohee', 'Aiden'"
                $new = $new -replace '("voice"\s*:\s*)"Aiden"', '${1}"Sohee"'
                $new = $new -replace '("voice"\s*:\s*)"aiden"', '${1}"Sohee"'
                $new = $new -replace '(voice\s*=\s*)"Aiden"', '${1}"Sohee"'
                $new = $new -replace "(voice\s*=\s*)'Aiden'", "`${1}'Sohee'"
                $new = $new -replace '(VOICE\s*=\s*)Aiden', '${1}Sohee'
                $new = $new -replace '(voice\s*:\s*)Aiden', '${1}Sohee'

                if ($new -ne $raw) {
                    Set-Content -Encoding UTF8 -LiteralPath $file -Value $new
                    Info "Aiden -> Sohee en: $file"
                } else {
                    Warn "Encontrado Aiden pero no se modificó automáticamente: $file"
                }
            }
        }
    }
}

Header "Final"
Write-Host "Cierra completamente Reachy Mini Desktop y vuelve a abrirlo."
Write-Host "Comprueba con:"
Write-Host "powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_VOZ_SOHEE_TOTAL.ps1"
