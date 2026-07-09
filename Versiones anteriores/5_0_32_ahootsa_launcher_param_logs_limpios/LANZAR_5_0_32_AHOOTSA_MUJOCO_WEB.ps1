param(
    [string]$AppRoot = "D:\RITXI\5_0_25_ahootsa_logs_simples_actividades_recuperadas",
    [switch]$InstallMujoco
)

$ErrorActionPreference = "Stop"

# Nueva sesion por ejecucion. El lanzador original reparado usara esta variable.
$RunId = Get-Date -Format "yyyyMMdd_HHmmss"
$env:AHOOTSA_SESSION = $RunId
$env:AHOOTSA_LAST_SESSION = $RunId

$LogRoot = "D:\RITXI\logs"
if (-not (Test-Path -LiteralPath $LogRoot)) {
    New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
}
$LastInfo = Join-Path $LogRoot "ULTIMA_EJECUCION_AHOOTSA_INFO.txt"
@(
    "Ahootsa 5.0.32 - ultima ejecucion",
    "timestamp=$RunId",
    "fecha=$(Get-Date -Format o)",
    "app_root=$AppRoot",
    "esperados=ahootsa5_${RunId}_pantalla.log, ahootsa5_${RunId}_runtime.log, ahootsa5_${RunId}_eventos.jsonl"
) | Set-Content -Encoding UTF8 -LiteralPath $LastInfo

$Apply = Join-Path $PSScriptRoot "0_APLICAR_CORRECCION_5_0_32.ps1"
if (-not (Test-Path -LiteralPath $Apply)) {
    throw "No encuentro el script de correccion: $Apply"
}

$ApplyArgs = @(
    "-ExecutionPolicy", "Bypass",
    "-File", $Apply,
    "-AppRoot", $AppRoot
)
if ($InstallMujoco.IsPresent) { $ApplyArgs += "-InstallMujoco" }

& powershell @ApplyArgs
if ($LASTEXITCODE -ne 0) { throw "No se pudo aplicar la correccion 5.0.32." }

$Launch = Join-Path $AppRoot "LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1"
if (-not (Test-Path -LiteralPath $Launch)) {
    throw "No encuentro el script original de lanzamiento: $Launch"
}

Write-Host ""
Write-Host "[INFO] Lanzando Ahootsa original con correcciones 5.0.32..."
Write-Host "[INFO] Nueva sesion/logs: $RunId"
Write-Host "[INFO] Resumen de ultima ejecucion: $LastInfo"
& powershell -ExecutionPolicy Bypass -File $Launch
