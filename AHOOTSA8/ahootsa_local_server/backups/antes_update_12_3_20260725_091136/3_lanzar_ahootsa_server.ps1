$ErrorActionPreference = "Stop"
$serverRoot = $PSScriptRoot
$pythonExe = Join-Path $serverRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "No existe el entorno virtual de ahootsa_local_server (.venv)." -ForegroundColor Red
    exit 1
}

Set-Location $serverRoot
try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false) } catch {}

Write-Host "Iniciando Ahootsa Local Server 0.12.2" -ForegroundColor Cyan
Write-Host "Panel: http://127.0.0.1:8100/panel" -ForegroundColor Gray
Write-Host "API:   http://127.0.0.1:8100" -ForegroundColor Gray
Write-Host "Docs:  http://127.0.0.1:8100/docs" -ForegroundColor Gray
Write-Host ""

& $pythonExe -m uvicorn app.main:app --host 127.0.0.1 --port 8100
