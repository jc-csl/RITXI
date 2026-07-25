param(
    [switch]$KeepExisting
)

$ErrorActionPreference = "Stop"
$serverRoot = $PSScriptRoot
$projectRoot = Split-Path $serverRoot -Parent
$utilsPath = Join-Path $projectRoot "scripts\ahootsa_process_utils.ps1"
$pythonExe = Join-Path $serverRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $utilsPath)) {
    throw "Missing process utility: $utilsPath"
}
. $utilsPath

if (-not (Test-Path $pythonExe)) {
    Write-Host (
        "The ahootsa_local_server virtual environment was not found."
    ) -ForegroundColor Red
    exit 1
}

if (-not $KeepExisting) {
    Stop-AhootsaPortProcess `
        -Port 8100 `
        -ServiceName "Ahootsa Local Server" |
        Out-Null

    Stop-AhootsaCommandProcesses `
        -Patterns @("uvicorn", "app\.main:app", "ahootsa_local_server") `
        -ServiceName "Ahootsa Local Server"
}

Set-Location $serverRoot
try {
    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
} catch {}

Write-Host "Starting Ahootsa Local Server 0.12.3" -ForegroundColor Cyan
Write-Host "Panel: http://127.0.0.1:8100/panel" -ForegroundColor Gray
Write-Host "API:   http://127.0.0.1:8100" -ForegroundColor Gray
Write-Host "Docs:  http://127.0.0.1:8100/docs" -ForegroundColor Gray
Write-Host "Port:  8100" -ForegroundColor Gray
Write-Host ""

& $pythonExe -m uvicorn app.main:app --host 127.0.0.1 --port 8100
