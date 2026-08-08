param()

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
$ServerRoot = Join-Path $ProjectRoot "ahootsa_local_server"
$PythonExe = Join-Path $ServerRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    throw "No se encuentra el Python del servidor local: $PythonExe"
}

Set-Location $ServerRoot

try {
    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
} catch {}

Write-Host ""
Write-Host "AHOOTSA LOCAL SERVER" -ForegroundColor Cyan
Write-Host "Panel: http://127.0.0.1:8100/panel-12-8-5" -ForegroundColor Gray
Write-Host "API:   http://127.0.0.1:8100/docs" -ForegroundColor Gray
Write-Host "Puerto: 8100" -ForegroundColor Gray
Write-Host ""

& $PythonExe `
    -m uvicorn `
    app.main:app `
    --host 127.0.0.1 `
    --port 8100
