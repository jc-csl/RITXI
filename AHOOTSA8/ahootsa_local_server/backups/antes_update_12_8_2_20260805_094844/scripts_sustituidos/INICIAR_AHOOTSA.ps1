param(
    [switch]$Anonimo,

    [switch]$DebugMode,

    [switch]$NoAbrirNavegador,

    [int]$TiempoEsperaSesionMinutos = 20
)

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$UtilsPath = Join-Path `
    $ProjectRoot `
    "scripts\ahootsa_process_utils.ps1"
$Cleaner = Join-Path `
    $ProjectRoot `
    "LIMPIAR_PROCESOS_AHOOTSA.ps1"
$ServerScript = Join-Path `
    $ProjectRoot `
    "scripts\iniciar_servidor_local.ps1"
$DaemonScript = Join-Path `
    $ProjectRoot `
    "scripts\iniciar_daemon_mujoco.ps1"
$ConversationScript = Join-Path `
    $ProjectRoot `
    "scripts\iniciar_conversation_app.ps1"
$Checker = Join-Path `
    $ProjectRoot `
    "COMPROBAR_AHOOTSA.ps1"
$PanelUrl = "http://127.0.0.1:8100/panel-12-7-2"
$ConversationUrl = "http://127.0.0.1:7860"

foreach ($Required in @(
    $UtilsPath,
    $Cleaner,
    $ServerScript,
    $DaemonScript,
    $ConversationScript,
    $Checker
)) {
    if (-not (Test-Path $Required)) {
        throw "Falta un archivo necesario: $Required"
    }
}

. $UtilsPath

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " AHOOTSA - ARRANQUE COMPLETO" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1/5 Cerrando procesos anteriores..." -ForegroundColor Cyan

& $Cleaner

if ($LASTEXITCODE -ne 0) {
    throw "No se pudieron liberar los puertos 7860, 8100 y 8000."
}

Write-Host ""
Write-Host "2/5 Arrancando Ahootsa Local Server..." -ForegroundColor Cyan

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
Write-Host "3/5 Arrancando Reachy Mini daemon..." -ForegroundColor Cyan

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

if (-not $NoAbrirNavegador) {
    Start-Process $PanelUrl
}

Write-Host ""
Write-Host "4/5 Seleccionando el modo de conversación..." -ForegroundColor Cyan

$Bootstrap = Invoke-RestMethod `
    -Uri "http://127.0.0.1:8100/panel/api/bootstrap" `
    -Method Get `
    -TimeoutSec 10

if ($Anonimo) {
    Write-Host (
        "Modo anónimo solicitado. Se utilizará el perfil ahootsa."
    ) -ForegroundColor Yellow
} elseif ($null -eq $Bootstrap.active_session) {
    Write-Host (
        "No hay una sesión preparada."
    ) -ForegroundColor Yellow

    Write-Host (
        "Prepara la persona, actividad y nivel en el panel."
    ) -ForegroundColor Yellow

    Write-Host (
        "El arranque esperará hasta $TiempoEsperaSesionMinutos minutos."
    ) -ForegroundColor Gray

    $Deadline = (Get-Date).AddMinutes(
        $TiempoEsperaSesionMinutos
    )

    while ((Get-Date) -lt $Deadline) {
        if (Test-AhootsaPort -Port 7860) {
            break
        }

        try {
            $Bootstrap = Invoke-RestMethod `
                -Uri "http://127.0.0.1:8100/panel/api/bootstrap" `
                -Method Get `
                -TimeoutSec 5
        } catch {
            $Bootstrap = $null
        }

        if (
            $null -ne $Bootstrap -and
            $null -ne $Bootstrap.active_session
        ) {
            break
        }

        Start-Sleep -Seconds 2
    }

    if (
        -not (Test-AhootsaPort -Port 7860) -and
        (
            $null -eq $Bootstrap -or
            $null -eq $Bootstrap.active_session
        )
    ) {
        Write-Host (
            "No se preparó una sesión. Se iniciará en modo anónimo."
        ) -ForegroundColor Yellow
    }
}

if (-not (Test-AhootsaPort -Port 7860)) {
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
}

Write-Host ""
Write-Host "5/5 Esperando la Conversation App..." -ForegroundColor Cyan

if (
    -not (
        Wait-AhootsaPortOpen `
            -Port 7860 `
            -TimeoutSeconds 120
    )
) {
    throw "La Conversation App no responde en el puerto 7860."
}

Write-Host "Conversation App activa en 7860." -ForegroundColor Green

if (-not $NoAbrirNavegador) {
    Start-Process $ConversationUrl
}

Write-Host ""
Write-Host "ARRANQUE COMPLETO FINALIZADO." -ForegroundColor Green
Write-Host ""
Write-Host "Panel:        $PanelUrl" -ForegroundColor Gray
Write-Host "Conversación: $ConversationUrl" -ForegroundColor Gray
Write-Host "Daemon:       http://127.0.0.1:8000/docs" -ForegroundColor Gray
Write-Host ""

& $Checker
