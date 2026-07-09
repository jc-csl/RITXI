# PROBAR_6_SDK_SIM.ps1
# Prueba conexión SDK oficial contra daemon en simulación.

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\apps_venv\Scripts\python.exe"
$Cmd = Join-Path $Root "app\sdk_command.py"

Write-Host "============================================================"
Write-Host "Prueba SDK Reachy Mini sim"
Write-Host "============================================================"

if (-not (Test-Path $Py)) {
    Write-Host "[ERROR] No existe Python de Reachy Mini Control:"
    Write-Host $Py
    exit 1
}

try {
    $s = Invoke-RestMethod "http://127.0.0.1:8000/api/daemon/status" -TimeoutSec 3
    Write-Host "[OK] Daemon responde."
    Write-Host ($s | ConvertTo-Json -Depth 5)
} catch {
    Write-Host "[ERROR] Daemon no responde. Lanza primero:"
    Write-Host "powershell -ExecutionPolicy Bypass -File .\LANZAR_6_DAEMON_SIM_REACHY.ps1"
    exit 1
}

Write-Host ""
Write-Host "SDK probe:"
& $Py $Cmd probe

Write-Host ""
Write-Host "Movimiento antenas:"
& $Py $Cmd wiggle

Write-Host ""
Write-Host "Movimiento saludo:"
& $Py $Cmd saludo
