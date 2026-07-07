# VALIDAR_5_VOZ_SESION_SOHEE.ps1
# Ahootsa 5.0.23
# Aplica Sohee sobre la sesion activa durante 60 segundos.

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Watcher = Join-Path $Root "MANTENER_5_VOZ_SOHEE_WATCHER.ps1"

if (-not (Test-Path -LiteralPath $Watcher)) {
    Write-Host "[ERROR] No existe $Watcher"
    exit 1
}

powershell -ExecutionPolicy Bypass -File $Watcher -DurationSeconds 60 -IntervalSeconds 3 -InitialDelaySeconds 1 -Voice "Sohee"
