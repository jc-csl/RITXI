# LANZAR_6_DAEMON_SIM_REACHY.ps1
# Lanza el daemon oficial de Reachy Mini en modo simulacion.
# No usa --wireless-version.

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$Daemon = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\apps_venv\Scripts\reachy-mini-daemon.exe"
$LogRoot = "D:\RITXI\logs"
if (-not (Test-Path $LogRoot)) { New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null }

Write-Host "============================================================"
Write-Host "Reachy Mini daemon --sim"
Write-Host "============================================================"

try {
    $s = Invoke-RestMethod "http://127.0.0.1:8000/api/daemon/status" -TimeoutSec 3
    Write-Host "[OK] El daemon ya responde en 8000."
    Write-Host ($s | ConvertTo-Json -Depth 5)
    exit 0
} catch {
    Write-Host "[INFO] El daemon no responde todavía. Se intentará lanzar."
}

if (-not (Test-Path $Daemon)) {
    Write-Host "[ERROR] No existe el daemon:"
    Write-Host $Daemon
    exit 1
}

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$out = Join-Path $LogRoot "ahootsa6_daemon_sim_$ts.log"
$err = Join-Path $LogRoot "ahootsa6_daemon_sim_$ts.stderr.log"

$proc = Start-Process -FilePath $Daemon -ArgumentList @("--sim") -PassThru -WindowStyle Minimized `
    -RedirectStandardOutput $out -RedirectStandardError $err

Write-Host "PID daemon: $($proc.Id)"
Write-Host "Log stdout: $out"
Write-Host "Log stderr: $err"

for ($i=1; $i -le 40; $i++) {
    Start-Sleep -Seconds 1
    try {
        $s = Invoke-RestMethod "http://127.0.0.1:8000/api/daemon/status" -TimeoutSec 2
        Write-Host "[OK] Daemon sim listo."
        Write-Host ($s | ConvertTo-Json -Depth 5)
        exit 0
    } catch {
        Write-Host "Esperando daemon sim... $i"
    }
}

Write-Host "[ERROR] Daemon sim no listo."
Write-Host "Revisa:"
Write-Host $out
Write-Host $err
exit 1
