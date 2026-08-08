param(
    [switch]$DebugMode
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
$AppRoot = Join-Path $ProjectRoot "reachy_mini_conversation_app"
$ServerRoot = Join-Path $ProjectRoot "ahootsa_local_server"
$UtilsPath = Join-Path $PSScriptRoot "ahootsa_process_utils.ps1"
$LoggingUtilsPath = Join-Path $PSScriptRoot "ahootsa_logging_utils.ps1"
$Activate = Join-Path $AppRoot ".venv\Scripts\Activate.ps1"
$DotEnvPath = Join-Path $AppRoot ".env"
$ActiveSessionFile = Join-Path $ServerRoot "data\active_session.json"
$PythonExe = Join-Path $ServerRoot ".venv\Scripts\python.exe"
$AppPythonExe = Join-Path $AppRoot ".venv\Scripts\python.exe"
$DiagnosticTool = Join-Path $PSScriptRoot "ahootsa_log_diagnostics.py"
$ReportTool = Join-Path $ServerRoot "tools\ahootsa_session_report.py"
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

if (-not (Test-Path $Activate)) {
    throw "No se encuentra el entorno oficial: $Activate"
}

if (-not (Test-AhootsaPort -Port 8100)) {
    throw "El modo sesión necesita el servidor local en el puerto 8100."
}

if (-not (Test-AhootsaPort -Port 8000)) {
    throw "El modo sesión necesita el daemon en el puerto 8000."
}

if (Test-AhootsaPort -Port 7860) {
    Write-Host (
        "La Conversation App ya está activa en el puerto 7860."
    ) -ForegroundColor Yellow

    exit 0
}

$Bootstrap = Invoke-RestMethod `
    -Uri "$ServerUrl/panel/api/bootstrap" `
    -Method Get `
    -TimeoutSec 10

if ($null -eq $Bootstrap.active_session) {
    throw (
        "No hay una sesión preparada. " +
        "Crea la sesión en el panel antes de iniciar la conversación."
    )
}

$SessionId = [int]$Bootstrap.active_session.session_id

if (-not (Test-Path $ActiveSessionFile)) {
    throw "Falta active_session.json para la sesión $SessionId."
}

$SessionData = Get-Content `
    $ActiveSessionFile `
    -Raw `
    -Encoding UTF8 |
    ConvertFrom-Json

if ([int]$SessionData.session_id -ne $SessionId) {
    throw "La sesión activa no coincide con active_session.json."
}

$SessionDirectory = [string]$SessionData.session_directory
$LogFile = [string]$SessionData.log_file

$CentralLogContext = Initialize-AhootsaSessionLogContext `
    -ProjectRoot $ProjectRoot `
    -SessionId $SessionId `
    -SessionDirectory $SessionDirectory `
    -SessionLogFile $LogFile

$CentralLogDirectory = [string]$CentralLogContext.Directory
$CentralLogFile = [string]$CentralLogContext.CentralLogFile

Set-AhootsaDotEnvProfile `
    -DotEnvPath $DotEnvPath `
    -ProfileName "ahootsa_session"

$env:REACHY_MINI_CUSTOM_PROFILE = "ahootsa_session"

New-Item `
    -ItemType Directory `
    -Path $SessionDirectory `
    -Force |
    Out-Null

Set-Location $AppRoot
& $Activate

Write-Host ""
Write-Host "AHOOTSA - SESIÓN LOCAL IDENTIFICADA" -ForegroundColor Cyan
Write-Host "Sesión: $SessionId" -ForegroundColor Green
Write-Host "Perfil: ahootsa_session" -ForegroundColor Gray
Write-Host "Servidor local: 8100" -ForegroundColor Gray
Write-Host "Conversation App: 7860" -ForegroundColor Gray
Write-Host "Log de sesión: $LogFile" -ForegroundColor Gray
Write-Host "Logs centralizados: $CentralLogDirectory" -ForegroundColor Gray
Write-Host ""

Start-Transcript `
    -Path $LogFile `
    -Append |
    Out-Null

try {
    if ($DebugMode) {
        reachy-mini-conversation-app --ui --debug
    } else {
        reachy-mini-conversation-app --ui
    }
} finally {
    try {
        Stop-Transcript | Out-Null
    } catch {}

    Sync-AhootsaCentralLog `
        -SourceLogFile $LogFile `
        -CentralLogFile $CentralLogFile

    Invoke-AhootsaLogDiagnostics `
        -PythonExe $AppPythonExe `
        -DiagnosticTool $DiagnosticTool `
        -LogFile $LogFile `
        -OutputDirectory $CentralLogDirectory `
        -Mode "identified_session" `
        -State "conversation_app_stopped" `
        -SessionId $SessionId `
        -Profile "ahootsa_session" `
        -Voice "Sohee" `
        -SourceSessionDirectory $SessionDirectory |
        Out-Null

    $PanelMarker = Join-Path `
        $SessionDirectory `
        "panel_finish_requested.flag"

    $ScriptMarker = Join-Path `
        $SessionDirectory `
        "external_finish_requested.flag"

    $ExternalFinalizer = (
        (Test-Path $PanelMarker) -or
        (Test-Path $ScriptMarker)
    )

    if ($ExternalFinalizer) {
        Write-Host ""
        Write-Host (
            "El panel o FINALIZAR_SESION_AHOOTSA.ps1 " +
            "completará el informe."
        ) -ForegroundColor Cyan
    } elseif (
        (Test-Path $PythonExe) -and
        (Test-Path $ReportTool)
    ) {
        Write-Host ""
        Write-Host (
            "Procesando la sesión identificada y generando el informe..."
        ) -ForegroundColor Cyan

        & $PythonExe `
            $ReportTool `
            --session-id $SessionId `
            --server-url $ServerUrl `
            --log $LogFile `
            --session-dir $SessionDirectory

        if ($LASTEXITCODE -ne 0) {
            Write-Host (
                "El informe queda pendiente. Ejecuta " +
                "FINALIZAR_SESION_AHOOTSA.ps1."
            ) -ForegroundColor Yellow
        }
    }

    Set-AhootsaDotEnvProfile `
        -DotEnvPath $DotEnvPath `
        -ProfileName "ahootsa"

    $env:REACHY_MINI_CUSTOM_PROFILE = "ahootsa"
}
