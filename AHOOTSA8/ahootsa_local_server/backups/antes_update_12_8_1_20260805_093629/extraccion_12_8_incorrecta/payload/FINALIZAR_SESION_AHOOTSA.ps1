param(
    [switch]$DetenerTodo
)

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$UtilsPath = Join-Path `
    $ProjectRoot `
    "scripts\ahootsa_process_utils.ps1"
$ServerScript = Join-Path `
    $ProjectRoot `
    "scripts\iniciar_servidor_local.ps1"
$Cleaner = Join-Path `
    $ProjectRoot `
    "LIMPIAR_PROCESOS_AHOOTSA.ps1"
$ServerRoot = Join-Path `
    $ProjectRoot `
    "ahootsa_local_server"
$AppRoot = Join-Path `
    $ProjectRoot `
    "reachy_mini_conversation_app"
$ActiveSessionFile = Join-Path `
    $ServerRoot `
    "data\active_session.json"
$PythonExe = Join-Path `
    $ServerRoot `
    ".venv\Scripts\python.exe"
$ReportTool = Join-Path `
    $ServerRoot `
    "tools\ahootsa_session_report.py"
$DotEnvPath = Join-Path $AppRoot ".env"
$ServerUrl = "http://127.0.0.1:8100"

if (-not (Test-Path $UtilsPath)) {
    throw "No se encuentra la utilidad de procesos: $UtilsPath"
}

. $UtilsPath

Write-Host ""
Write-Host "FINALIZAR SESIÓN AHOOTSA" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-AhootsaPort -Port 8100)) {
    Write-Host (
        "Arrancando temporalmente el servidor local..."
    ) -ForegroundColor Cyan

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
}

$Bootstrap = Invoke-RestMethod `
    -Uri "$ServerUrl/panel/api/bootstrap" `
    -Method Get `
    -TimeoutSec 10

$SessionId = $null
$SessionDirectory = $null
$LogFile = $null

if ($null -ne $Bootstrap.active_session) {
    $SessionId = [int]$Bootstrap.active_session.session_id
}

if (Test-Path $ActiveSessionFile) {
    $SessionData = Get-Content `
        $ActiveSessionFile `
        -Raw `
        -Encoding UTF8 |
        ConvertFrom-Json

    if ($null -eq $SessionId) {
        $SessionId = [int]$SessionData.session_id
    }

    $SessionDirectory = [string]$SessionData.session_directory
    $LogFile = [string]$SessionData.log_file
}

if (
    $null -ne $SessionId -and
    [string]::IsNullOrWhiteSpace($SessionDirectory)
) {
    $SessionDirectory = Join-Path `
        $ServerRoot `
        ("data\sessions\session_{0:D6}" -f $SessionId)

    $LogFile = Join-Path `
        $SessionDirectory `
        "conversation_app.log"
}

$Marker = $null

if ($null -ne $SessionId) {
    New-Item `
        -ItemType Directory `
        -Path $SessionDirectory `
        -Force |
        Out-Null

    $Marker = Join-Path `
        $SessionDirectory `
        "external_finish_requested.flag"

    [System.IO.File]::WriteAllText(
        $Marker,
        "FINALIZAR_SESION_AHOOTSA.ps1 controla el cierre.",
        (New-Object System.Text.UTF8Encoding($false))
    )
}

try {
    if (Test-AhootsaPort -Port 7860) {
        Write-Host "Cerrando la Conversation App..." -ForegroundColor Cyan

        $Graceful = Stop-AhootsaConversationAppGracefully

        if (-not $Graceful) {
            Stop-AhootsaPortProcess `
                -Port 7860 `
                -ServiceName "Conversation App" |
                Out-Null
        }
    } else {
        Write-Host (
            "La Conversation App ya estaba cerrada."
        ) -ForegroundColor Gray
    }

    if ($null -eq $SessionId) {
        Set-AhootsaDotEnvProfile `
            -DotEnvPath $DotEnvPath `
            -ProfileName "ahootsa"

        Write-Host ""
        Write-Host (
            "No había una sesión identificada. " +
            "Se ha cerrado la conversación anónima."
        ) -ForegroundColor Yellow
    } else {
        if (
            -not (
                Wait-AhootsaFileStable `
                    -Path $LogFile `
                    -TimeoutSeconds 20
            )
        ) {
            Write-Host (
                "Aviso: el log no existe o no quedó estable."
            ) -ForegroundColor Yellow
        }

        if (-not (Test-Path $PythonExe)) {
            throw "No se encuentra el Python del servidor: $PythonExe"
        }

        if (-not (Test-Path $ReportTool)) {
            throw "No se encuentra el generador de informes: $ReportTool"
        }

        Write-Host ""
        Write-Host (
            "Finalizando la sesión $SessionId y generando informes..."
        ) -ForegroundColor Cyan

        & $PythonExe `
            $ReportTool `
            --session-id $SessionId `
            --server-url $ServerUrl `
            --log $LogFile `
            --session-dir $SessionDirectory

        if ($LASTEXITCODE -ne 0) {
            throw "No se pudo generar el informe de la sesión $SessionId."
        }

        Write-Host ""
        Write-Host (
            "SESIÓN $SessionId FINALIZADA CORRECTAMENTE."
        ) -ForegroundColor Green

        Write-Host (
            "Carpeta: $SessionDirectory"
        ) -ForegroundColor Gray
    }
} finally {
    if (
        $null -ne $Marker -and
        (Test-Path $Marker)
    ) {
        Remove-Item $Marker -Force
    }
}

if ($DetenerTodo) {
    Write-Host ""
    Write-Host (
        "Deteniendo también servidor y daemon..."
    ) -ForegroundColor Cyan

    & $Cleaner
}
