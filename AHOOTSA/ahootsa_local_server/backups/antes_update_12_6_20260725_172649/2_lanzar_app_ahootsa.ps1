param(
    [switch]$DebugMode,
    [switch]$KeepExisting
)

$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
$appRoot = Join-Path $projectRoot "reachy_mini_conversation_app"
$serverRoot = Join-Path $projectRoot "ahootsa_local_server"
$utilsPath = Join-Path $projectRoot "scripts\ahootsa_process_utils.ps1"
$activate = Join-Path $appRoot ".venv\Scripts\Activate.ps1"
$activeSessionFile = Join-Path $serverRoot "data\active_session.json"

if (-not (Test-Path $utilsPath)) {
    throw "Missing process utility: $utilsPath"
}
. $utilsPath

if (-not (Test-Path $activate)) {
    throw "Missing official app virtual environment: $activate"
}

if (-not $KeepExisting) {
    Stop-AhootsaConversationAppGracefully |
        Out-Null

    Stop-AhootsaPortProcess `
        -Port 7860 `
        -ServiceName "Reachy Mini Conversation App" |
        Out-Null

    Stop-AhootsaCommandProcesses `
        -Patterns @("reachy-mini-conversation-app") `
        -ServiceName "Reachy Mini Conversation App"
}

$logFile = Join-Path $serverRoot (
    "data\conversation_app_" +
    (Get-Date -Format "yyyyMMdd_HHmmss") +
    ".log"
)
$sessionId = $null

if (Test-Path $activeSessionFile) {
    try {
        $activeSession = Get-Content `
            $activeSessionFile `
            -Raw `
            -Encoding UTF8 |
            ConvertFrom-Json

        $sessionId = $activeSession.session_id
        if ($activeSession.log_file) {
            $logFile = [string]$activeSession.log_file
        }
    } catch {
        Write-Host (
            "Warning: active_session.json could not be read."
        ) -ForegroundColor Yellow
    }
}

$logDirectory = Split-Path $logFile -Parent
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null

Set-Location $appRoot
& $activate

Write-Host ""
Write-Host "Starting Reachy Mini Conversation App for Ahootsa" -ForegroundColor Cyan
Write-Host "Profile: ahootsa_session" -ForegroundColor Gray
if ($null -ne $sessionId) {
    Write-Host "Session: $sessionId" -ForegroundColor Gray
}
Write-Host "Log: $logFile" -ForegroundColor Gray
Write-Host "Port: 7860" -ForegroundColor Gray
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
    try {
        Stop-Transcript | Out-Null
    } catch {}
}
