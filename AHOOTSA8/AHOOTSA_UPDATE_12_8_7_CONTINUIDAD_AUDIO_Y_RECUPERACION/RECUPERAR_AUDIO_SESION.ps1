param(
    [switch]$DebugMode
)

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$ServerRoot = Join-Path $ProjectRoot "ahootsa_local_server"
$AppRoot = Join-Path $ProjectRoot "reachy_mini_conversation_app"
$UtilsPath = Join-Path `
    $ProjectRoot `
    "scripts\ahootsa_process_utils.ps1"
$ConversationLauncher = Join-Path `
    $ProjectRoot `
    "scripts\iniciar_conversation_sesion.ps1"
$ActiveSessionFile = Join-Path `
    $ServerRoot `
    "data\active_session.json"
$DotEnvPath = Join-Path $AppRoot ".env"
$ServerUrl = "http://127.0.0.1:8100"

foreach ($Required in @(
    $UtilsPath,
    $ConversationLauncher,
    $ActiveSessionFile,
    $DotEnvPath
)) {
    if (-not (Test-Path $Required)) {
        throw "Falta un archivo necesario: $Required"
    }
}

. $UtilsPath

if (-not (Test-AhootsaPort -Port 8100)) {
    throw "El servidor local no está activo en el puerto 8100."
}

if (-not (Test-AhootsaPort -Port 8000)) {
    throw "El daemon no está activo en el puerto 8000."
}

$SessionData = Get-Content `
    $ActiveSessionFile `
    -Raw `
    -Encoding UTF8 |
    ConvertFrom-Json

$SessionId = [int]$SessionData.session_id
$SessionDirectory = [string]$SessionData.session_directory
$LogFile = [string]$SessionData.log_file
$RecoveryMarker = Join-Path `
    $SessionDirectory `
    "external_finish_requested.flag"

$Bootstrap = Invoke-RestMethod `
    -Uri "$ServerUrl/panel/api/bootstrap" `
    -Method Get `
    -TimeoutSec 10

if ($null -eq $Bootstrap.active_session) {
    throw "No existe una sesión preparada o activa en el panel."
}

if ([int]$Bootstrap.active_session.session_id -ne $SessionId) {
    throw "La sesión del panel no coincide con active_session.json."
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " AHOOTSA - RECUPERAR AUDIO DE LA SESIÓN" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Sesión: $SessionId" -ForegroundColor Green
Write-Host "Se conservarán usuario, actividad y eventos." -ForegroundColor Gray
Write-Host "No se detendrán el servidor ni el daemon." -ForegroundColor Gray
Write-Host ""

if (Test-AhootsaPort -Port 7860) {
    [System.IO.File]::WriteAllText(
        $RecoveryMarker,
        (
            "audio_recovery_requested=" +
            (Get-Date).ToString("o")
        ),
        (New-Object System.Text.UTF8Encoding($false))
    )

    Write-Host "1/3 Deteniendo solo Conversation App..." -ForegroundColor Cyan

    $Stopped = Stop-AhootsaConversationAppGracefully `
        -ConversationPort 7860 `
        -DaemonPort 8000

    if (-not $Stopped) {
        Stop-AhootsaPortProcess `
            -Port 7860 `
            -ServiceName "Conversation App" `
            -WaitSeconds 20 |
            Out-Null
    }

    if (
        -not (
            Wait-AhootsaPortClosed `
                -Port 7860 `
                -TimeoutSeconds 30
        )
    ) {
        throw "Conversation App sigue activa en el puerto 7860."
    }

    Wait-AhootsaFileStable `
        -Path $LogFile `
        -TimeoutSeconds 20 |
        Out-Null

    Write-Host "Conversation App detenida." -ForegroundColor Green

    Write-Host ""
    Write-Host "2/3 Esperando el cierre limpio del lanzador..." -ForegroundColor Cyan

    $Deadline = (Get-Date).AddSeconds(30)
    $ProfileRestored = $false

    while ((Get-Date) -lt $Deadline) {
        $DotEnv = Get-Content `
            $DotEnvPath `
            -Raw `
            -Encoding UTF8

        if (
            $DotEnv -match (
                '(?m)^\s*REACHY_MINI_CUSTOM_PROFILE\s*=\s*' +
                'ahootsa\s*$'
            )
        ) {
            $ProfileRestored = $true
            break
        }

        Start-Sleep -Milliseconds 500
    }

    if (-not $ProfileRestored) {
        throw (
            "El lanzador anterior no restauró el perfil general. " +
            "No se reinicia para evitar mezclar perfiles."
        )
    }

    Remove-Item `
        $RecoveryMarker `
        -Force `
        -ErrorAction SilentlyContinue

    Write-Host "Cierre limpio confirmado." -ForegroundColor Green
} else {
    Write-Host (
        "Conversation App ya estaba detenida. " +
        "Se iniciará de nuevo con la sesión activa."
    ) -ForegroundColor Yellow

    Remove-Item `
        $RecoveryMarker `
        -Force `
        -ErrorAction SilentlyContinue
}

$Bootstrap = Invoke-RestMethod `
    -Uri "$ServerUrl/panel/api/bootstrap" `
    -Method Get `
    -TimeoutSec 10

if ($null -eq $Bootstrap.active_session) {
    throw (
        "La sesión dejó de estar activa durante la recuperación. " +
        "No se inicia una conversación sin contexto."
    )
}

if ([int]$Bootstrap.active_session.session_id -ne $SessionId) {
    throw "La sesión activa cambió durante la recuperación."
}

Write-Host ""
Write-Host "3/3 Reiniciando Conversation App..." -ForegroundColor Cyan

$Arguments = @(
    "-NoExit",
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $ConversationLauncher
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
            -TimeoutSeconds 75
    )
) {
    throw "Conversation App no volvió a responder en el puerto 7860."
}

Write-Host ""
Write-Host "AUDIO Y CONVERSACIÓN RECUPERADOS." -ForegroundColor Green
Write-Host "La sesión $SessionId continúa activa." -ForegroundColor Cyan
Write-Host "El log seguirá añadiéndose en:" -ForegroundColor Gray
Write-Host "  $LogFile" -ForegroundColor Gray
