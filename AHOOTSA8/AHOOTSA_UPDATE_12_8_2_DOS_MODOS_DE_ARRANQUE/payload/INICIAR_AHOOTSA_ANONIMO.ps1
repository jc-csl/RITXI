param(
    [switch]$DebugMode,

    [switch]$NoAbrirNavegador
)

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$UtilsPath = Join-Path $ProjectRoot "scripts\ahootsa_process_utils.ps1"
$Cleaner = Join-Path $ProjectRoot "LIMPIAR_PROCESOS_AHOOTSA.ps1"
$DaemonScript = Join-Path $ProjectRoot "scripts\iniciar_daemon_mujoco.ps1"
$ConversationScript = Join-Path $ProjectRoot "scripts\iniciar_conversation_anonima.ps1"
$ConversationUrl = "http://127.0.0.1:7860"

foreach ($Required in @(
    $UtilsPath,
    $Cleaner,
    $DaemonScript,
    $ConversationScript
)) {
    if (-not (Test-Path $Required)) {
        throw "Falta un archivo necesario: $Required"
    }
}

. $UtilsPath

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " AHOOTSA - INICIO ANÓNIMO" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Este modo no utiliza el servidor local ni el panel." -ForegroundColor Yellow
Write-Host "No crea una sesión ni un informe personal." -ForegroundColor Yellow
Write-Host ""

Write-Host "1/3 Cerrando procesos anteriores..." -ForegroundColor Cyan
& $Cleaner

if ($LASTEXITCODE -ne 0) {
    throw "No se pudieron liberar los puertos Ahootsa."
}

Write-Host ""
Write-Host "2/3 Arrancando daemon y MuJoCo..." -ForegroundColor Cyan

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

Write-Host ""
Write-Host "3/3 Arrancando conversación anónima..." -ForegroundColor Cyan

$Arguments = @(
    "-NoExit",
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $ConversationScript
)

if ($DebugMode) {
    $Arguments += "-DebugMode"
}

Start-Process `
    powershell.exe `
    -WorkingDirectory $ProjectRoot `
    -ArgumentList $Arguments

if (
    -not (
        Wait-AhootsaPortOpen `
            -Port 7860 `
            -TimeoutSeconds 120
    )
) {
    throw "La Conversation App no responde en el puerto 7860."
}

if (Test-AhootsaPort -Port 8100) {
    throw "El servidor local se inició de forma inesperada en 8100."
}

Write-Host ""
Write-Host "MODO ANÓNIMO INICIADO CORRECTAMENTE." -ForegroundColor Green
Write-Host "Daemon:       8000" -ForegroundColor Gray
Write-Host "Conversación: 7860" -ForegroundColor Gray
Write-Host "Servidor:     8100 detenido" -ForegroundColor Gray

if (-not $NoAbrirNavegador) {
    Start-Process $ConversationUrl
}
