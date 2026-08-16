param(
    [switch]$DetenerTodo
)

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$UtilsPath = Join-Path $ProjectRoot "scripts\ahootsa_process_utils.ps1"
$LoggingUtilsPath = Join-Path $ProjectRoot "scripts\ahootsa_logging_utils.ps1"
$DiagnosticTool = Join-Path $ProjectRoot "scripts\ahootsa_log_diagnostics.py"
$Cleaner = Join-Path $ProjectRoot "LIMPIAR_PROCESOS_AHOOTSA.ps1"
$ServerScript = Join-Path $ProjectRoot "scripts\iniciar_servidor_local.ps1"
$ServerRoot = Join-Path $ProjectRoot "ahootsa_local_server"
$AppRoot = Join-Path $ProjectRoot "reachy_mini_conversation_app"
$ActiveSessionFile = Join-Path $ServerRoot "data\active_session.json"
$PythonExe = Join-Path $ServerRoot ".venv\Scripts\python.exe"
$AppPythonExe = Join-Path $AppRoot ".venv\Scripts\python.exe"
$ReportTool = Join-Path $ServerRoot "tools\ahootsa_session_report.py"
$DotEnvPath = Join-Path $AppRoot ".env"
$ServerUrl = "http://127.0.0.1:8100"

foreach ($Required in @(
    $UtilsPath,
    $LoggingUtilsPath,
    $DiagnosticTool
)) {
    if (-not (Test-Path $Required)) {
        throw "Falta un archivo necesario: $Required"
    }
}

. $UtilsPath
. $LoggingUtilsPath

Write-Host ""
Write-Host "FINALIZAR AHOOTSA" -ForegroundColor Cyan
Write-Host ""

$HasLocalServer = Test-AhootsaPort -Port 8100
$HasActiveFile = Test-Path $ActiveSessionFile

if (-not $HasLocalServer -and -not $HasActiveFile) {
    Write-Host "Modo detectado: conversación anónima." -ForegroundColor Yellow

    if (Test-AhootsaPort -Port 7860) {
        if (-not (Stop-AhootsaConversationAppGracefully)) {
            Stop-AhootsaPortProcess `
                -Port 7860 `
                -ServiceName "Conversation App" |
                Out-Null
        }
    }

    Set-AhootsaDotEnvProfile `
        -DotEnvPath $DotEnvPath `
        -ProfileName "ahootsa"

    $LastAnonymousPointer = Join-Path `
        $ProjectRoot `
        "logs\ULTIMO_ANONIMO.txt"

    if (Test-Path $LastAnonymousPointer) {
        $AnonymousDirectory = (
            Get-Content `
                $LastAnonymousPointer `
                -Raw `
                -Encoding UTF8
        ).Trim()
        $AnonymousLog = Join-Path `
            $AnonymousDirectory `
            "conversation_app.log"

        Invoke-AhootsaLogDiagnostics `
            -PythonExe $AppPythonExe `
            -DiagnosticTool $DiagnosticTool `
            -LogFile $AnonymousLog `
            -OutputDirectory $AnonymousDirectory `
            -Mode "anonymous" `
            -State "finished" `
            -Profile "ahootsa" `
            -Voice "Sohee" |
            Out-Null
    }

    Write-Host "Conversación anónima finalizada." -ForegroundColor Green

    if ($DetenerTodo) {
        & $Cleaner
    }

    exit 0
}

if (-not $HasLocalServer) {
    Write-Host "Arrancando temporalmente el servidor local..." -ForegroundColor Cyan

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

if ($HasActiveFile) {
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

if ($null -eq $SessionId) {
    Write-Host (
        "No hay una sesión identificada activa. " +
        "Se cerrará únicamente la Conversation App."
    ) -ForegroundColor Yellow

    if (Test-AhootsaPort -Port 7860) {
        if (-not (Stop-AhootsaConversationAppGracefully)) {
            Stop-AhootsaPortProcess `
                -Port 7860 `
                -ServiceName "Conversation App" |
                Out-Null
        }
    }

    Set-AhootsaDotEnvProfile `
        -DotEnvPath $DotEnvPath `
        -ProfileName "ahootsa"

    if ($DetenerTodo) {
        & $Cleaner
    }

    exit 0
}

if ([string]::IsNullOrWhiteSpace($SessionDirectory)) {
    $SessionDirectory = Join-Path `
        $ServerRoot `
        ("data\sessions\session_{0:D6}" -f $SessionId)

    $LogFile = Join-Path $SessionDirectory "conversation_app.log"
}

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

try {
    if (Test-AhootsaPort -Port 7860) {
        if (-not (Stop-AhootsaConversationAppGracefully)) {
            Stop-AhootsaPortProcess `
                -Port 7860 `
                -ServiceName "Conversation App" |
                Out-Null
        }
    }

    Wait-AhootsaFileStable `
        -Path $LogFile `
        -TimeoutSeconds 20 |
        Out-Null

    if (-not (Test-Path $PythonExe)) {
        throw "No se encuentra el Python del servidor: $PythonExe"
    }

    if (-not (Test-Path $ReportTool)) {
        throw "No se encuentra el generador de informes: $ReportTool"
    }

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

    $CentralContext = Initialize-AhootsaSessionLogContext `
        -ProjectRoot $ProjectRoot `
        -SessionId $SessionId `
        -SessionDirectory $SessionDirectory `
        -SessionLogFile $LogFile

    Sync-AhootsaCentralLog `
        -SourceLogFile $LogFile `
        -CentralLogFile $CentralContext.CentralLogFile

    Invoke-AhootsaLogDiagnostics `
        -PythonExe $AppPythonExe `
        -DiagnosticTool $DiagnosticTool `
        -LogFile $LogFile `
        -OutputDirectory $CentralContext.Directory `
        -Mode "identified_session" `
        -State "finished" `
        -SessionId $SessionId `
        -Profile "ahootsa_session" `
        -Voice "Sohee" `
        -SourceSessionDirectory $SessionDirectory |
        Out-Null

    Write-Host ""
    Write-Host (
        "SESIÓN $SessionId FINALIZADA CORRECTAMENTE."
    ) -ForegroundColor Green
    Write-Host "Carpeta: $SessionDirectory" -ForegroundColor Gray
} finally {
    Remove-Item $Marker -Force -ErrorAction SilentlyContinue

    Set-AhootsaDotEnvProfile `
        -DotEnvPath $DotEnvPath `
        -ProfileName "ahootsa"
}

if ($DetenerTodo) {
    & $Cleaner
}
