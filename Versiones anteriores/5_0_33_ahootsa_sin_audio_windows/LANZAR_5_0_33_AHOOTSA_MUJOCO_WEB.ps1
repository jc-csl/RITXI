param(
    [string]$AppRoot = "D:\RITXI\5_0_25_ahootsa_logs_simples_actividades_recuperadas",
    [switch]$InstallMujoco
)

$ErrorActionPreference = "Stop"

# Sesion nueva por ejecucion.
$RunId = Get-Date -Format "yyyyMMdd_HHmmss"
$env:AHOOTSA_SESSION = $RunId
$env:AHOOTSA_LAST_SESSION = $RunId

# Politica de audio: solo Ahootsa, no Windows TTS.
$env:AHOOTSA_DISABLE_WINDOWS_TTS = "1"
$env:AHOOTSA_AUDIO_ONLY_AHOOTSA = "1"
$env:AHOOTSA_BLOCK_BROWSER_TTS = "1"
$env:AHOOTSA_ALLOW_WINDOWS_TTS = "0"

$LogRoot = "D:\RITXI\logs"
if (-not (Test-Path -LiteralPath $LogRoot)) {
    New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
}
$LastInfo = Join-Path $LogRoot "ULTIMA_EJECUCION_AHOOTSA_INFO.txt"
@(
    "Ahootsa 5.0.33 - ultima ejecucion",
    "timestamp=$RunId",
    "fecha=$(Get-Date -Format o)",
    "app_root=$AppRoot",
    "audio_policy=solo_ahootsa_sin_windows_tts",
    "env_AHOOTSA_DISABLE_WINDOWS_TTS=$env:AHOOTSA_DISABLE_WINDOWS_TTS",
    "esperados=ahootsa5_${RunId}_pantalla.log, ahootsa5_${RunId}_runtime.log, ahootsa5_${RunId}_eventos.jsonl"
) | Set-Content -Encoding UTF8 -LiteralPath $LastInfo

$Apply = Join-Path $PSScriptRoot "0_APLICAR_CORRECCION_5_0_33.ps1"
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
if ($LASTEXITCODE -ne 0) { throw "No se pudo aplicar la correccion 5.0.33." }

$Launch = Join-Path $AppRoot "LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1"
if (-not (Test-Path -LiteralPath $Launch)) {
    throw "No encuentro el script original de lanzamiento: $Launch"
}

Write-Host ""
Write-Host "[INFO] Lanzando Ahootsa original con correcciones 5.0.33..."
Write-Host "[INFO] Nueva sesion/logs: $RunId"
Write-Host "[INFO] Audio Windows TTS: DESACTIVADO"
Write-Host "[INFO] Resumen de ultima ejecucion: $LastInfo"
& powershell -ExecutionPolicy Bypass -File $Launch
