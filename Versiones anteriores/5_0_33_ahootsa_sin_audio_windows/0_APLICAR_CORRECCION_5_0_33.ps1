param(
    [string]$AppRoot = "D:\RITXI\5_0_25_ahootsa_logs_simples_actividades_recuperadas",
    [switch]$InstallMujoco,
    [switch]$PackageOnly
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host "Ahootsa 5.0.33 - eliminar audio Windows + logs limpios"
Write-Host "============================================================"
Write-Host "AppRoot: $AppRoot"
Write-Host "PackageOnly: $PackageOnly"

$Py = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\apps_venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Py)) {
    throw "No encuentro el Python de apps_venv: $Py"
}
Write-Host "Python: $Py"

if ($InstallMujoco) {
    Write-Host "[INFO] Instalando/actualizando MuJoCo en apps_venv..."
    & $Py -m ensurepip --upgrade
    & $Py -m pip install --upgrade pip
    & $Py -m pip install mujoco
    if ($LASTEXITCODE -ne 0) { throw "No se pudo instalar mujoco en apps_venv." }
}

Write-Host "[INFO] Comprobando import del paquete Ahootsa..."
& $Py -c "import ahootsa_realtime_ollama_desktop_app as p; import pathlib; print('IMPORT_OK', pathlib.Path(p.__file__).resolve())"
if ($LASTEXITCODE -ne 0) { throw "No se puede importar ahootsa_realtime_ollama_desktop_app desde apps_venv." }

$Tools = Join-Path $PSScriptRoot "tools"
$PatchEndpoints = Join-Path $Tools "patch_ahootsa_bootstrap_endpoints_5_0_27.py"
$PatchLogsSession = Join-Path $Tools "patch_logs_session_5_0_32.py"
$PatchAudioWindows = Join-Path $Tools "patch_windows_audio_off_5_0_33.py"

Write-Host ""
Write-Host "[1/3] Aplicando endpoints de compatibilidad..."
& $Py $PatchEndpoints
if ($LASTEXITCODE -ne 0) { throw "El parche de endpoints no se pudo aplicar." }

Write-Host ""
Write-Host "[2/3] Reparando lanzador PowerShell y logs por ejecucion..."
if (Test-Path -LiteralPath $AppRoot) {
    & $Py $PatchLogsSession --target-root $AppRoot
    if ($LASTEXITCODE -ne 0) { throw "El parche de lanzador/logs no se pudo aplicar." }
} else {
    Write-Host "[WARN] AppRoot no existe. Se omite parche de logs sobre carpeta 5_0_25: $AppRoot"
}

Write-Host ""
Write-Host "[3/3] Eliminando audio Windows/navegador 5.0.33..."
if ($PackageOnly) {
    & $Py $PatchAudioWindows --package-only
} else {
    & $Py $PatchAudioWindows --project-root $AppRoot
}
if ($LASTEXITCODE -ne 0) { throw "El parche para eliminar audio Windows no se pudo aplicar." }

Write-Host ""
Write-Host "============================================================"
Write-Host "Correccion 5.0.33 aplicada"
Write-Host "============================================================"
Write-Host "Cambios principales:"
Write-Host "- elimina voz Windows/navegador por Web Speech API;"
Write-Host "- elimina TTS Windows desde Python: pyttsx3/SAPI;"
Write-Host "- mantiene audio Ahootsa/OpenAI/Realtime;"
Write-Host "- mantiene logs limpios por ejecucion y endpoints de compatibilidad."
Write-Host ""
Write-Host "IMPORTANTE: cierra y vuelve a abrir la ventana de Desktop Control para evitar cache del navegador."
