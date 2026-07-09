# DIAGNOSTICAR_6_FALLBACK_LOCAL.ps1
# Ahootsa 6.0.0 fallback local

param(
    [int]$Port = 8090
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = Join-Path $Root ".venv\Scripts\python.exe"

Write-Host "============================================================"
Write-Host "Diagnostico Ahootsa 6.1 fallback local + SDK sim"
Write-Host "============================================================"

Write-Host "Root: $Root"
Write-Host "Python venv existe:" (Test-Path $PythonExe)

if (Test-Path $PythonExe) {
    & $PythonExe --version
    & $PythonExe -c "import fastapi, uvicorn, httpx; print('imports OK')"
}

Write-Host ""
Write-Host "Servidor local:"
try {
    $Status = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/status" -TimeoutSec 5
    Write-Host "[OK] http://127.0.0.1:$Port/api/status"
    Write-Host ($Status | ConvertTo-Json -Depth 8)
} catch {
    Write-Host "[WARN] No responde Ahootsa 6 en puerto $Port"
    Write-Host $_.Exception.Message
}

Write-Host ""
Write-Host "Ollama:"
try {
    $Tags = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 5
    Write-Host "[OK] Ollama responde"
    $Tags.models | Select-Object name, modified_at, size | Format-Table -AutoSize
} catch {
    Write-Host "[WARN] Ollama no responde"
    Write-Host $_.Exception.Message
}

Write-Host ""
Write-Host "Procesos relacionados:"
Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -match "uvicorn|ahootsa6|ollama" } |
    Select-Object ProcessId, CommandLine |
    Format-Table -AutoSize


Write-Host ""
Write-Host "Reachy daemon HTTP:"
try {
    $D = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/daemon/status" -TimeoutSec 5
    Write-Host "[OK] Daemon Reachy responde"
    Write-Host ($D | ConvertTo-Json -Depth 8)
} catch {
    Write-Host "[WARN] Daemon Reachy no responde en 8000"
    Write-Host $_.Exception.Message
}

Write-Host ""
Write-Host "SDK Python:"
$SdkPy = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\apps_venv\Scripts\python.exe"
Write-Host "Path: $SdkPy"
Write-Host "Existe:" (Test-Path $SdkPy)
if (Test-Path $SdkPy) {
    & $SdkPy -c "import reachy_mini; print('reachy_mini import OK', getattr(reachy_mini, '__file__', ''))"
}
