$ErrorActionPreference = "Stop"
$Script = Join-Path $PSScriptRoot "scripts\windows\00_INSTALACION_COMPLETA_DESDE_CERO.ps1"
if (-not (Test-Path $Script)) {
    Write-Host "No encuentro el instalador completo:" $Script -ForegroundColor Red
    exit 1
}
& $Script @args
