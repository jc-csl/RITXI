# PARAR_5_AHOOTSA_MUJOCO_WEB.ps1
# Para la app actual. Solo cierra el daemon si se usa -StopDaemon.

param(
    [int]$Port = 8000,
    [string]$HostAddress = "127.0.0.1",
    [switch]$StopDaemon
)

$ErrorActionPreference = "Continue"

function Start-AhootsaLog {
    param([string]$Name)
    $script:LogRoot = "D:\RITXI\logs"
    if (-not (Test-Path -LiteralPath $script:LogRoot)) { New-Item -ItemType Directory -Force -Path $script:LogRoot | Out-Null }
    if (-not $env:AHOOTSA_SESSION_ID) { $env:AHOOTSA_SESSION_ID = Get-Date -Format "yyyyMMdd_HHmmss" }
    $env:AHOOTSA_LOG_DIR = $script:LogRoot
    $script:PsLog = Join-Path $script:LogRoot ("ahootsa_ps_" + $Name + "_" + $env:AHOOTSA_SESSION_ID + ".log")
    $script:JsonLog = Join-Path $script:LogRoot ("ahootsa_ps_events_" + $env:AHOOTSA_SESSION_ID + ".jsonl")
    try { Start-Transcript -LiteralPath $script:PsLog -Append | Out-Null } catch {}
    Write-AhootsaEvent "ps.start" @{script=$Name; pwd=(Get-Location).Path; user=$env:USERNAME}
}
function Write-AhootsaEvent {
    param([string]$Event, [hashtable]$Data=@{})
    if (-not $script:JsonLog) {
        $script:LogRoot="D:\RITXI\logs"; if (-not (Test-Path $script:LogRoot)) { New-Item -ItemType Directory -Force -Path $script:LogRoot | Out-Null }
        if (-not $env:AHOOTSA_SESSION_ID) { $env:AHOOTSA_SESSION_ID = Get-Date -Format "yyyyMMdd_HHmmss" }
        $script:JsonLog=Join-Path $script:LogRoot ("ahootsa_ps_events_" + $env:AHOOTSA_SESSION_ID + ".jsonl")
    }
    $o=[ordered]@{ts=(Get-Date).ToString("o"); event=$Event; session_id=$env:AHOOTSA_SESSION_ID; pid=$PID}
    foreach($k in $Data.Keys){$o[$k]=$Data[$k]}
    try { ($o|ConvertTo-Json -Depth 12 -Compress) | Add-Content -Encoding UTF8 -LiteralPath $script:JsonLog } catch {}
}
function Stop-AhootsaLog {
    param([string]$Name)
    Write-AhootsaEvent "ps.end" @{script=$Name}
    try { Stop-Transcript | Out-Null } catch {}
}

Start-AhootsaLog "PARAR_5_AHOOTSA_MUJOCO_WEB"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:AHOOTSA_LOG_DIR = "D:\RITXI\logs"
$env:AHOOTSA_VOICE = "Sohee"
$env:VOICE = "Sohee"
$env:REACHY_MINI_VOICE = "Sohee"
$env:OPENAI_REALTIME_VOICE = "Sohee"
$env:REALTIME_VOICE = "Sohee"
$env:TTS_VOICE = "Sohee"
$env:AUDIO_VOICE = "Sohee"
# voice.env.forced.510

function Invoke-Api($Method, $Path, [int]$TimeoutSec = 10) {
    $url = "http://$HostAddress`:$Port$Path"
    try {
        if ($Method -eq "GET") {
            return Invoke-RestMethod -Uri $url -Method Get -TimeoutSec $TimeoutSec
        } else {
            return Invoke-RestMethod -Uri $url -Method Post -TimeoutSec $TimeoutSec
        }
    } catch {
        Write-Host "[WARN] $Method $url -> $($_.Exception.Message)"
        return $null
    }
}

Write-Host "Parando app actual si existe..."
$null = Invoke-Api "POST" "/api/apps/stop-current-app" 10

if ($StopDaemon) {
    Write-Host "Parando daemon. Esto cerrará MuJoCo."
    $null = Invoke-Api "POST" "/api/daemon/stop?goto_sleep=false" 10
} else {
    Write-Host "No se ha parado el daemon. MuJoCo sigue abierto."
    Write-Host "Para cerrar todo, ejecuta:"
    Write-Host "powershell -ExecutionPolicy Bypass -File .\PARAR_5_AHOOTSA_MUJOCO_WEB.ps1 -StopDaemon"
}

Stop-AhootsaLog "PARAR_5_AHOOTSA_MUJOCO_WEB"
