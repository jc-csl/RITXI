$serverRoot = $PSScriptRoot
$pythonExe = Join-Path $serverRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "No existe el entorno virtual (.venv)." -ForegroundColor Red
    exit 1
}

Set-Location $serverRoot
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Iniciando Ahootsa Local Server - Servidor principal" -ForegroundColor Cyan
Write-Host "API:  http://127.0.0.1:8100" -ForegroundColor Gray
Write-Host "Docs: http://127.0.0.1:8100/docs" -ForegroundColor Gray
Write-Host ""

& $pythonExe -m uvicorn app.main:app --host 127.0.0.1 --port 8100

