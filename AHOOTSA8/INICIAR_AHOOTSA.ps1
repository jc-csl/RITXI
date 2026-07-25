param(
    [switch]$DebugMode
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

function Test-LocalPort {
    param([int]$Port)

    $Client = New-Object System.Net.Sockets.TcpClient
    try {
        $Async = $Client.BeginConnect("127.0.0.1", $Port, $null, $null)
        if (-not $Async.AsyncWaitHandle.WaitOne(400)) {
            return $false
        }
        $Client.EndConnect($Async)
        return $true
    } catch {
        return $false
    } finally {
        $Client.Close()
    }
}

function Wait-LocalPort {
    param(
        [int]$Port,
        [int]$TimeoutSeconds
    )

    $Deadline = (Get-Date).AddSeconds($TimeoutSeconds)

    while ((Get-Date) -lt $Deadline) {
        if (Test-LocalPort -Port $Port) {
            return $true
        }
        Start-Sleep -Milliseconds 500
    }

    return (Test-LocalPort -Port $Port)
}

if (Test-LocalPort -Port 7860) {
    Write-Host (
        "La Conversation App ya esta activa en el puerto 7860."
    ) -ForegroundColor Yellow
    exit 0
}

if (-not (Test-LocalPort -Port 8100)) {
    $ServerScript = Join-Path `
        $ProjectRoot `
        "ahootsa_local_server\3_lanzar_ahootsa_server.ps1"

    if (-not (Test-Path $ServerScript)) {
        throw "No se encuentra el lanzador del servidor: $ServerScript"
    }

    Write-Host "Arrancando Ahootsa Local Server..." -ForegroundColor Cyan
    Start-Process `
        powershell.exe `
        -WorkingDirectory (Split-Path $ServerScript -Parent) `
        -ArgumentList @(
            "-NoExit",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            $ServerScript
        )

    if (-not (Wait-LocalPort -Port 8100 -TimeoutSeconds 45)) {
        throw "El servidor local no responde en el puerto 8100."
    }
}

if (-not (Test-LocalPort -Port 8000)) {
    $DaemonScript = Join-Path $ProjectRoot "1_lanzar_daemon_mujoco.ps1"

    if (-not (Test-Path $DaemonScript)) {
        throw "No se encuentra el lanzador del daemon: $DaemonScript"
    }

    Write-Host "Arrancando Reachy Mini daemon y MuJoCo..." -ForegroundColor Cyan
    Start-Process `
        powershell.exe `
        -WorkingDirectory $ProjectRoot `
        -ArgumentList @(
            "-NoExit",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            $DaemonScript
        )

    if (-not (Wait-LocalPort -Port 8000 -TimeoutSeconds 60)) {
        throw "El daemon no responde en el puerto 8000."
    }
}

$Bootstrap = Invoke-RestMethod `
    -Uri "http://127.0.0.1:8100/panel/api/bootstrap" `
    -Method Get `
    -TimeoutSec 10

Write-Host ""
if ($null -eq $Bootstrap.active_session) {
    Write-Host "Inicio sin sesion activa." -ForegroundColor Yellow
    Write-Host (
        "Se utilizara el perfil ahootsa sin identificacion."
    ) -ForegroundColor Yellow
} else {
    Write-Host (
        "Inicio con sesion identificada {0}." -f
        $Bootstrap.active_session.session_id
    ) -ForegroundColor Green
    Write-Host (
        "Se utilizara ahootsa_session y se generara un informe al cerrar."
    ) -ForegroundColor Green
}
Write-Host ""

$ConversationScript = Join-Path $ProjectRoot "2_lanzar_app_ahootsa.ps1"

if ($DebugMode) {
    & $ConversationScript -DebugMode
} else {
    & $ConversationScript
}
exit $LASTEXITCODE
