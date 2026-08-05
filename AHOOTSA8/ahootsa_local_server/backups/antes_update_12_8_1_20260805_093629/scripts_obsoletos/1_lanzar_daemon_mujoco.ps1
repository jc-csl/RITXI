param(
    [switch]$KeepExisting
)

$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
$appRoot = Join-Path $projectRoot "reachy_mini_conversation_app"
$utilsPath = Join-Path $projectRoot "scripts\ahootsa_process_utils.ps1"
$activate = Join-Path $appRoot ".venv\Scripts\Activate.ps1"

if (-not (Test-Path $utilsPath)) {
    throw "Missing process utility: $utilsPath"
}
. $utilsPath

if (-not (Test-Path $activate)) {
    throw "Missing official app virtual environment: $activate"
}

if (-not $KeepExisting) {
    Stop-AhootsaPortProcess `
        -Port 8000 `
        -ServiceName "Reachy Mini daemon" |
        Out-Null

    Stop-AhootsaCommandProcesses `
        -Patterns @("reachy-mini-daemon", "--sim") `
        -ServiceName "Reachy Mini daemon"
}

Set-Location $appRoot
& $activate

Write-Host ""
Write-Host "Starting Reachy Mini daemon with MuJoCo..." -ForegroundColor Cyan
Write-Host "Port: 8000" -ForegroundColor Gray
Write-Host ""

reachy-mini-daemon --sim --scene minimal
