param()

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
$AppRoot = Join-Path $ProjectRoot "reachy_mini_conversation_app"
$Activate = Join-Path $AppRoot ".venv\Scripts\Activate.ps1"

if (-not (Test-Path $Activate)) {
    throw "No se encuentra el entorno oficial: $Activate"
}

Set-Location $AppRoot
& $Activate

Write-Host ""
Write-Host "REACHY MINI DAEMON + MUJOCO" -ForegroundColor Cyan
Write-Host "Puerto: 8000" -ForegroundColor Gray
Write-Host ""

reachy-mini-daemon --sim --scene minimal
