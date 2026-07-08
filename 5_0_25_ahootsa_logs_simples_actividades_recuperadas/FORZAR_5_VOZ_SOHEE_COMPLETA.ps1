# FORZAR_5_VOZ_SOHEE_COMPLETA.ps1
# Ahootsa 5.0.25
# Voz simple: escribe Sohee sin BOM y, si la app esta lista, aplica una vez por API.
# No usa watcher ni bucles largos.

param(
    [switch]$NoApi,
    [int]$WaitSeconds = 15
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$LogRoot = "D:\RITXI\logs"
if (-not (Test-Path -LiteralPath $LogRoot)) { New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null }
if (-not $env:AHOOTSA_SESSION_ID) { $env:AHOOTSA_SESSION_ID = Get-Date -Format "yyyyMMdd_HHmmss" }
$env:AHOOTSA_LOG_DIR = $LogRoot
[Environment]::SetEnvironmentVariable("AHOOTSA_LOG_DIR", $LogRoot, "User")

$Log = if ($env:AHOOTSA_LOG_FILE_SCREEN) { $env:AHOOTSA_LOG_FILE_SCREEN } else { Join-Path $LogRoot ("ahootsa5_" + $env:AHOOTSA_SESSION_ID + "_pantalla.log") }
try { "VOICE_START $(Get-Date -Format o)" | Add-Content -Encoding UTF8 -LiteralPath $Log  -ErrorAction SilentlyContinue} catch {}

function Write-TextNoBom {
    param([string]$Path, [string]$Text)
    $Parent = Split-Path -Parent $Path
    if ($Parent -and -not (Test-Path -LiteralPath $Parent)) { New-Item -ItemType Directory -Force -Path $Parent | Out-Null }
    $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Text, $Utf8NoBom)
}

$Voice = "Sohee"

"AHOOTSA_VOICE","VOICE","REACHY_MINI_VOICE","OPENAI_REALTIME_VOICE","REALTIME_VOICE","TTS_VOICE","AUDIO_VOICE" | ForEach-Object {
    [Environment]::SetEnvironmentVariable($_, $Voice, "User")
    Set-Item -Path "Env:$_" -Value $Voice
    Write-Host "[OK] $_=$Voice"
}

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$SP = Join-Path $DesktopDir "apps_venv\Lib\site-packages"
$Files = @(
    (Join-Path $SP "reachy_mini_conversation_app\profiles\ahootsa_realtime_es\voice.txt"),
    (Join-Path $SP "reachy_mini_conversation_app\profiles\default\voice.txt"),
    (Join-Path $SP "reachy_mini_conversation_app\profiles\starter_profile\voice.txt"),
    (Join-Path $SP "reachy_talk_data\profiles\ahootsa_realtime_es\voice.txt"),
    (Join-Path $SP "reachy_talk_data\profiles\default\voice.txt"),
    (Join-Path $SP "reachy_talk_data\profiles\starter_profile\voice.txt"),
    (Join-Path $SP "ahootsa_realtime_ollama_desktop_app\profiles\ahootsa_realtime_es\voice.txt"),
    (Join-Path $SP "ahootsa_realtime_ollama_desktop_app\profiles\default\voice.txt"),
    (Join-Path $SP "ahootsa_realtime_ollama_desktop_app\profiles\starter_profile\voice.txt")
)

foreach ($F in $Files) {
    try {
        Write-TextNoBom -Path $F -Text $Voice
        Write-Host "[OK] voice.txt sin BOM -> $F"
    } catch {
        Write-Host "[WARN] $F : $($_.Exception.Message)"
    }
}

if (-not $NoApi) {
    $Ready = $false
    for ($i=1; $i -le $WaitSeconds; $i++) {
        try {
            $Current = Invoke-WebRequest -Uri "http://127.0.0.1:7860/voices/current" -Method Get -TimeoutSec 3 -UseBasicParsing
            $Ready = $true
            break
        } catch {
            Start-Sleep -Seconds 1
        }
    }

    if ($Ready) {
        try {
            $Body = "{""voice"":""Sohee""}"
            $Resp = Invoke-WebRequest -Uri "http://127.0.0.1:7860/voices/apply" -Method Post -ContentType "application/json" -Body $Body -TimeoutSec 5 -UseBasicParsing
            Write-Host "[OK] /voices/apply ->" $Resp.Content
        } catch {
            Write-Host "[WARN] No se pudo aplicar por API: $($_.Exception.Message)"
        }

        try {
            $Current = Invoke-WebRequest -Uri "http://127.0.0.1:7860/voices/current" -Method Get -TimeoutSec 5 -UseBasicParsing
            Write-Host "[INFO] voices/current =" $Current.Content
        } catch {}
    } else {
        Write-Host "[INFO] App 7860 no lista. Solo se han escrito variables y voice.txt."
    }
}

try { "VOICE_END $(Get-Date -Format o)" | Add-Content -Encoding UTF8 -LiteralPath $Log  -ErrorAction SilentlyContinue} catch {}
Write-Host "Log unificado: $Log"
