param(
    [switch]$InstallMujoco
)

$ErrorActionPreference = "Stop"

# ============================================================
# Ahootsa 5.0.34 completa consolidada
# Lanzador unico. No depende de carpetas 5.0.25-5.0.33.
# ============================================================

$AppRoot = $PSScriptRoot
$RunId = Get-Date -Format "yyyyMMdd_HHmmss"
$env:AHOOTSA_SESSION = $RunId
$env:AHOOTSA_LAST_SESSION = $RunId

# Politica de audio: solo Ahootsa. Bloquear Windows/navegador/pyttsx3/SAPI.
$env:AHOOTSA_DISABLE_WINDOWS_TTS = "1"
$env:AHOOTSA_AUDIO_ONLY_AHOOTSA = "1"
$env:AHOOTSA_BLOCK_BROWSER_TTS = "1"
$env:AHOOTSA_ALLOW_WINDOWS_TTS = "0"

$LogRoot = "D:\RITXI\logs"
if (-not (Test-Path -LiteralPath $LogRoot)) { New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null }
$LastInfo = Join-Path $LogRoot "ULTIMA_EJECUCION_AHOOTSA_INFO.txt"
@(
    "Ahootsa 5.0.34 completa consolidada - ultima ejecucion",
    "timestamp=$RunId",
    "fecha=$(Get-Date -Format o)",
    "app_root=$AppRoot",
    "audio_policy=solo_ahootsa_sin_windows_tts",
    "esperados=ahootsa5_${RunId}_pantalla.log, ahootsa5_${RunId}_runtime.log, ahootsa5_${RunId}_eventos.jsonl"
) | Set-Content -Encoding UTF8 -LiteralPath $LastInfo

$Py = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\apps_venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Py)) { throw "No encuentro Python de apps_venv: $Py" }

if ($InstallMujoco) {
    Write-Host "[INFO] Instalando/actualizando MuJoCo en apps_venv..."
    & $Py -m ensurepip --upgrade
    & $Py -m pip install --upgrade pip
    & $Py -m pip install mujoco
    if ($LASTEXITCODE -ne 0) { throw "No se pudo instalar MuJoCo." }
}

# Garantiza parches de paquete por si Desktop Control reinstala/cambia site-packages.
$Tools = Join-Path $AppRoot ".ahootsa_5_0_34_patches\tools"
if (Test-Path -LiteralPath $Tools) {
    $PatchEndpoints = Join-Path $Tools "patch_ahootsa_bootstrap_endpoints_5_0_27.py"
    $PatchAudio = Join-Path $Tools "patch_windows_audio_off_5_0_33.py"
    if (Test-Path -LiteralPath $PatchEndpoints) { & $Py $PatchEndpoints | Out-Host }
    if (Test-Path -LiteralPath $PatchAudio) { & $Py $PatchAudio --project-root $AppRoot | Out-Host }
}

$OriginalLaunch = Join-Path $AppRoot "LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1"
if (-not (Test-Path -LiteralPath $OriginalLaunch)) { throw "No encuentro LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1 en $AppRoot" }

Write-Host ""
Write-Host "============================================================"
Write-Host "Ahootsa 5.0.34 completa consolidada"
Write-Host "============================================================"
Write-Host "Root:    $AppRoot"
Write-Host "Logs:    $LogRoot"
Write-Host "Session: $RunId"
Write-Host "Audio:   solo Ahootsa; Windows/navegador/pyttsx3/SAPI bloqueado"
Write-Host ""
& powershell -ExecutionPolicy Bypass -File $OriginalLaunch
