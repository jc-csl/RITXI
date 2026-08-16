param(
    [switch]$DebugMode
)

$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
$appRoot = Join-Path $projectRoot "reachy_mini_conversation_app"
$serverRoot = Join-Path $projectRoot "ahootsa_local_server"
$activeSessionFile = Join-Path $serverRoot "data\active_session.json"

if (-not (Test-Path (Join-Path $appRoot ".venv\Scripts\Activate.ps1"))) {
    Write-Host "The official app virtual environment was not found." -ForegroundColor Red
    Write-Host "  $appRoot\.venv\Scripts\Activate.ps1"
    exit 1
}

$logFile = Join-Path $serverRoot ("data\conversation_app_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".log")
$sessionId = $null

if (Test-Path $activeSessionFile) {
    try {
        $activeSession = Get-Content $activeSessionFile -Raw -Encoding UTF8 | ConvertFrom-Json
        $sessionId = $activeSession.session_id
        if ($activeSession.log_file) {
            $logFile = [string]$activeSession.log_file
        }
    } catch {
        Write-Host "Warning: active_session.json could not be read." -ForegroundColor Yellow
    }
}

$logDirectory = Split-Path $logFile -Parent
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null

Set-Location $appRoot
& ".\.venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Starting Reachy Mini Conversation App for Ahootsa" -ForegroundColor Cyan
Write-Host "Profile: ahootsa_session" -ForegroundColor Gray
if ($null -ne $sessionId) {
    Write-Host "Session: $sessionId" -ForegroundColor Gray
}
Write-Host "Log: $logFile" -ForegroundColor Gray
Write-Host ""

Start-Transcript -Path $logFile -Append | Out-Null
try {
    if ($DebugMode) {
        reachy-mini-conversation-app --ui --debug
    } else {
        reachy-mini-conversation-app --ui
    }
}
finally {
    try { Stop-Transcript | Out-Null } catch {}
}
