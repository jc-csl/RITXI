param(
    [switch]$InstallMujoco
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe"
$Patch = Join-Path $Root "tools\patch_camera_pc_5_0_35.py"
$OriginalLauncher = Join-Path $Root "LANZAR_AHOOTSA.ps1"

Write-Host "============================================================"
Write-Host "Ahootsa 5.0.35 - Camara PC + version consolidada"
Write-Host "============================================================"
Write-Host "Root: $Root"

if (!(Test-Path -LiteralPath $Py)) {
    throw "No encuentro python.exe del apps_venv: $Py"
}

if ($InstallMujoco) {
    & $Py -m pip install mujoco
    if ($LASTEXITCODE -ne 0) { throw "No se pudo instalar mujoco." }
}

Write-Host "[INFO] Aplicando soporte de camara PC..."
& $Py $Patch $Root
if ($LASTEXITCODE -ne 0) { throw "No se pudo aplicar soporte de camara PC." }

if (!(Test-Path -LiteralPath $OriginalLauncher)) {
    throw "No encuentro LANZAR_AHOOTSA.ps1 dentro de esta version: $OriginalLauncher"
}

Write-Host "[INFO] Lanzando Ahootsa 5.0.35..."
if ($InstallMujoco) {
    & powershell -ExecutionPolicy Bypass -File $OriginalLauncher -InstallMujoco
} else {
    & powershell -ExecutionPolicy Bypass -File $OriginalLauncher
}
