# REINICIAR_5_APP_AHOOTSA.ps1
# Reinicia solo la app Ahootsa sin cerrar MuJoCo ni el daemon.

param(
    [int]$Port = 8000,
    [string]$HostAddress = "127.0.0.1",
    [string]$AppName = "ahootsa_realtime_ollama_app"
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

Start-AhootsaLog "REINICIAR_5_APP_AHOOTSA"
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

Write-Host "Reiniciando solo Ahootsa. MuJoCo y daemon quedan abiertos."
$null = Invoke-Api "POST" "/api/apps/stop-current-app" 15
Start-Sleep -Seconds 3
$null = Invoke-Api "POST" "/api/apps/start-app/$AppName" 20
Start-Sleep -Seconds 5
Start-Process "http://localhost:7860"
Write-Host "Listo. Abierto http://localhost:7860"

Stop-AhootsaLog "REINICIAR_5_APP_AHOOTSA"
