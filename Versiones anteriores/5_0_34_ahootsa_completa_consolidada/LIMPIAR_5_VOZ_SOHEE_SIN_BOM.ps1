# LIMPIAR_5_VOZ_SOHEE_SIN_BOM.ps1
# Ahootsa 5.0.34
# Reescribe todos los voice.txt conocidos como UTF-8 SIN BOM.
# El bug detectado era /voices/current = {"voice":"ï»¿Sohee"}, lo que deja la UI en Sohee pero la sesion puede caer en Aiden.

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$LogRoot = "D:\RITXI\logs"
if (-not (Test-Path -LiteralPath $LogRoot)) { New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null }
if (-not $env:AHOOTSA_SESSION_ID) { $env:AHOOTSA_SESSION_ID = Get-Date -Format "yyyyMMdd_HHmmss" }
$env:AHOOTSA_LOG_DIR = $LogRoot
[Environment]::SetEnvironmentVariable("AHOOTSA_LOG_DIR", $LogRoot, "User")

function Write-TextNoBom {
    param([string]$Path, [string]$Text)
    $Parent = Split-Path -Parent $Path
    if ($Parent -and -not (Test-Path -LiteralPath $Parent)) { New-Item -ItemType Directory -Force -Path $Parent | Out-Null }
    $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Text, $Utf8NoBom)
}
function Read-TextTrimBom {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return "" }
    return ([System.IO.File]::ReadAllText($Path).Trim([char]0xFEFF).Trim())
}
function Has-Bom {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    $Bytes = [System.IO.File]::ReadAllBytes($Path)
    return ($Bytes.Length -ge 3 -and $Bytes[0] -eq 239 -and $Bytes[1] -eq 187 -and $Bytes[2] -eq 191)
}

$Log = Join-Path $LogRoot ("ahootsa_clean_voice_bom_" + $env:AHOOTSA_SESSION_ID + ".log")
$JsonLog = Join-Path $LogRoot ("ahootsa_clean_voice_bom_events_" + $env:AHOOTSA_SESSION_ID + ".jsonl")
try { Start-Transcript -LiteralPath $Log -Append | Out-Null } catch {}

function Write-CleanEvent {
    param([string]$Event, [hashtable]$Data=@{})
    $Obj = [ordered]@{ ts=(Get-Date).ToString("o"); event=$Event; session_id=$env:AHOOTSA_SESSION_ID; pid=$PID }
    foreach ($K in $Data.Keys) { $Obj[$K] = $Data[$K] }
    try { ($Obj | ConvertTo-Json -Depth 10 -Compress) | Add-Content -Encoding UTF8 -LiteralPath $JsonLog } catch {}
}

$Voice = "Sohee"
$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$SP = Join-Path $DesktopDir "apps_venv\Lib\site-packages"
$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$Files = @(
    (Join-Path $SP "reachy_mini_conversation_app\profiles\ahootsa_realtime_es\voice.txt"),
    (Join-Path $SP "reachy_mini_conversation_app\profiles\default\voice.txt"),
    (Join-Path $SP "reachy_mini_conversation_app\profiles\starter_profile\voice.txt"),
    (Join-Path $SP "reachy_talk_data\profiles\ahootsa_realtime_es\voice.txt"),
    (Join-Path $SP "reachy_talk_data\profiles\default\voice.txt"),
    (Join-Path $SP "reachy_talk_data\profiles\starter_profile\voice.txt"),
    (Join-Path $SP "ahootsa_realtime_ollama_desktop_app\profiles\ahootsa_realtime_es\voice.txt"),
    (Join-Path $SP "ahootsa_realtime_ollama_desktop_app\profiles\default\voice.txt"),
    (Join-Path $SP "ahootsa_realtime_ollama_desktop_app\profiles\starter_profile\voice.txt"),
    (Join-Path $RootDir "src\ahootsa_realtime_ollama_desktop_app\profiles\ahootsa_realtime_es\voice.txt"),
    (Join-Path $RootDir "src\ahootsa_realtime_ollama_desktop_app\profiles\default\voice.txt")
)

Write-CleanEvent "clean_voice_bom.start" @{ count=$Files.Count; voice=$Voice }

foreach ($F in $Files) {
    try {
        $BeforeExists = Test-Path -LiteralPath $F
        $BeforeBom = Has-Bom $F
        $BeforeValue = Read-TextTrimBom $F
        Write-TextNoBom -Path $F -Text $Voice
        $AfterBom = Has-Bom $F
        $AfterValue = Read-TextTrimBom $F
        Write-Host "[OK] $F before_exists=$BeforeExists before_bom=$BeforeBom before='$BeforeValue' after_bom=$AfterBom after='$AfterValue'"
        Write-CleanEvent "clean_voice_bom.file" @{
            path=$F
            before_exists=$BeforeExists
            before_bom=$BeforeBom
            before_value=$BeforeValue
            after_bom=$AfterBom
            after_value=$AfterValue
        }
    } catch {
        Write-Host "[WARN] $F : $($_.Exception.Message)"
        Write-CleanEvent "clean_voice_bom.error" @{ path=$F; error=$_.Exception.Message }
    }
}

# Variables tambien.
"AHOOTSA_VOICE","VOICE","REACHY_MINI_VOICE","OPENAI_REALTIME_VOICE","REALTIME_VOICE","TTS_VOICE","AUDIO_VOICE" | ForEach-Object {
    [Environment]::SetEnvironmentVariable($_, $Voice, "User")
    Set-Item -Path "Env:$_" -Value $Voice
}

# Si la app esta viva, comprobar current.
try {
    $Current = Invoke-WebRequest -Uri "http://127.0.0.1:7860/voices/current" -Method Get -TimeoutSec 5 -UseBasicParsing
    Write-Host "voices/current =" $Current.Content
    Write-CleanEvent "clean_voice_bom.current" @{ status=[int]$Current.StatusCode; body=[string]$Current.Content }
} catch {
    Write-Host "voices/current no disponible: $($_.Exception.Message)"
    Write-CleanEvent "clean_voice_bom.current.error" @{ error=$_.Exception.Message }
}

Write-CleanEvent "clean_voice_bom.end" @{ voice=$Voice }
try { Stop-Transcript | Out-Null } catch {}
Write-Host "Log: $Log"
