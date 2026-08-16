param(
    [switch]$NoAbrirNavegador
)

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$UtilsPath = Join-Path $ProjectRoot "scripts\ahootsa_process_utils.ps1"
$Cleaner = Join-Path $ProjectRoot "LIMPIAR_PROCESOS_AHOOTSA.ps1"
$ServerScript = Join-Path $ProjectRoot "scripts\iniciar_servidor_local.ps1"
$DaemonScript = Join-Path $ProjectRoot "scripts\iniciar_daemon_mujoco.ps1"
$PanelUrl = "http://127.0.0.1:8100/panel-12-8-5"

foreach ($Required in @(
    $UtilsPath,
    $Cleaner,
    $ServerScript,
    $DaemonScript
)) {
    if (-not (Test-Path $Required)) {
        throw "Falta un archivo necesario: $Required"
    }
}

. $UtilsPath

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " AHOOTSA - INICIO DE SESIÓN LOCAL" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host (
    "Este modo utiliza el panel para seleccionar persona, " +
    "actividad y nivel."
) -ForegroundColor Yellow
Write-Host ""

Write-Host "1/3 Cerrando procesos anteriores..." -ForegroundColor Cyan
& $Cleaner

if ($LASTEXITCODE -ne 0) {
    throw "No se pudieron liberar los puertos Ahootsa."
}

Write-Host ""
Write-Host "2/3 Arrancando servidor local..." -ForegroundColor Cyan

Start-Process `
    powershell.exe `
    -WorkingDirectory $ProjectRoot `
    -ArgumentList @(
        "-NoExit",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $ServerScript
    )

if (
    -not (
        Wait-AhootsaPortOpen `
            -Port 8100 `
            -TimeoutSeconds 60
    )
) {
    throw "El servidor local no responde en el puerto 8100."
}

Write-Host "Servidor local activo en 8100." -ForegroundColor Green

Write-Host ""
Write-Host "3/3 Arrancando daemon y MuJoCo..." -ForegroundColor Cyan

Start-Process `
    powershell.exe `
    -WorkingDirectory $ProjectRoot `
    -ArgumentList @(
        "-NoExit",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $DaemonScript
    )

if (
    -not (
        Wait-AhootsaPortOpen `
            -Port 8000 `
            -TimeoutSeconds 90
    )
) {
    throw "El daemon no responde en el puerto 8000."
}

Write-Host "Daemon activo en 8000." -ForegroundColor Green

if (Test-AhootsaPort -Port 7860) {
    throw "La Conversation App se inició antes de preparar la sesión."
}

Write-Host ""
Write-Host "MODO SESIÓN LOCAL PREPARADO." -ForegroundColor Green
Write-Host "Panel:  $PanelUrl" -ForegroundColor Gray
Write-Host ""
Write-Host "Procedimiento:" -ForegroundColor Yellow
Write-Host "  1. Crear o seleccionar una persona." -ForegroundColor Gray
Write-Host "  2. Elegir actividad y nivel." -ForegroundColor Gray
Write-Host "  3. Pulsar Preparar." -ForegroundColor Gray
Write-Host "  4. Pulsar Iniciar conversación." -ForegroundColor Gray
Write-Host "  5. Finalizar desde el panel o con el script de cierre." -ForegroundColor Gray

if (-not $NoAbrirNavegador) {
    Start-Process $PanelUrl
}
