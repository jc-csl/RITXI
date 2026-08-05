param()

$ErrorActionPreference = "Continue"

$ProjectRoot = $PSScriptRoot
$UtilsPath = Join-Path $ProjectRoot "scripts\ahootsa_process_utils.ps1"
$ServerRoot = Join-Path $ProjectRoot "ahootsa_local_server"
$ActiveSessionFile = Join-Path $ServerRoot "data\active_session.json"

if (-not (Test-Path $UtilsPath)) {
    throw "No se encuentra la utilidad de procesos: $UtilsPath"
}

. $UtilsPath

Write-Host ""
Write-Host "ESTADO AHOOTSA" -ForegroundColor Cyan
Write-Host ""

foreach ($Service in @(
    @{
        Name = "Reachy Mini daemon"
        Port = 8000
    },
    @{
        Name = "Ahootsa Local Server"
        Port = 8100
    },
    @{
        Name = "Conversation App"
        Port = 7860
    }
)) {
    $ProcessIds = @(Get-AhootsaPortProcessIds -Port $Service.Port)

    if ($ProcessIds.Count -eq 0) {
        Write-Host (
            "{0,-27} puerto {1}: DETENIDO" -f
            $Service.Name,
            $Service.Port
        ) -ForegroundColor DarkGray

        continue
    }

    foreach ($ProcessId in $ProcessIds) {
        $Description = Get-AhootsaProcessDescription -ProcessId $ProcessId

        Write-Host (
            "{0,-27} puerto {1}: ACTIVO PID {2} ({3})" -f
            $Service.Name,
            $Service.Port,
            $ProcessId,
            $Description.Name
        ) -ForegroundColor Green
    }
}

Write-Host ""

if (
    (Test-AhootsaPort -Port 8000) -and
    (Test-AhootsaPort -Port 7860) -and
    (-not (Test-AhootsaPort -Port 8100))
) {
    Write-Host "Modo detectado: ANÓNIMO" -ForegroundColor Yellow
} elseif (
    (Test-AhootsaPort -Port 8000) -and
    (Test-AhootsaPort -Port 8100)
) {
    Write-Host "Modo detectado: SESIÓN LOCAL" -ForegroundColor Green
} else {
    Write-Host "Modo detectado: INCOMPLETO O DETENIDO" -ForegroundColor Gray
}

if (Test-AhootsaPort -Port 8100) {
    try {
        $Bootstrap = Invoke-RestMethod `
            -Uri "http://127.0.0.1:8100/panel/api/bootstrap" `
            -Method Get `
            -TimeoutSec 8

        Write-Host (
            "Servidor Ahootsa: versión $($Bootstrap.version)"
        ) -ForegroundColor Green

        if ($null -eq $Bootstrap.active_session) {
            Write-Host "Sesión activa: ninguna" -ForegroundColor Gray
        } else {
            Write-Host (
                "Sesión activa: $($Bootstrap.active_session.session_id) - " +
                "$($Bootstrap.active_session.user.preferred_name)"
            ) -ForegroundColor Yellow
        }
    } catch {
        Write-Host (
            "El puerto 8100 está abierto, pero bootstrap no responde."
        ) -ForegroundColor Yellow
    }
}

if (Test-Path $ActiveSessionFile) {
    Write-Host "active_session.json: PRESENTE" -ForegroundColor Yellow
} else {
    Write-Host "active_session.json: no existe" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Scripts operativos esperados:" -ForegroundColor Cyan

foreach ($Name in @(
    "INICIAR_AHOOTSA_ANONIMO.ps1",
    "INICIAR_AHOOTSA_SESION.ps1",
    "FINALIZAR_SESION_AHOOTSA.ps1",
    "COMPROBAR_AHOOTSA.ps1",
    "LIMPIAR_PROCESOS_AHOOTSA.ps1"
)) {
    if (Test-Path (Join-Path $ProjectRoot $Name)) {
        Write-Host "  OK  $Name" -ForegroundColor Green
    } else {
        Write-Host "  FALTA  $Name" -ForegroundColor Red
    }
}
