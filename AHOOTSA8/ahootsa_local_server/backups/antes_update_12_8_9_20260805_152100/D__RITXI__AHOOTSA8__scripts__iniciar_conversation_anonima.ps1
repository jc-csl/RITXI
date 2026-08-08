param(
    [switch]$DebugMode
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
$AppRoot = Join-Path $ProjectRoot "reachy_mini_conversation_app"
$UtilsPath = Join-Path $PSScriptRoot "ahootsa_process_utils.ps1"
$LoggingUtilsPath = Join-Path $PSScriptRoot "ahootsa_logging_utils.ps1"
$Activate = Join-Path $AppRoot ".venv\Scripts\Activate.ps1"
$DotEnvPath = Join-Path $AppRoot ".env"
$PythonExe = Join-Path $AppRoot ".venv\Scripts\python.exe"
$DiagnosticTool = Join-Path $PSScriptRoot "ahootsa_log_diagnostics.py"

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

if (Test-AhootsaPort -Port 8100) {
    throw (
        "El modo anónimo no utiliza el servidor local. " +
        "El puerto 8100 debe estar libre."
    )
}

if (Test-AhootsaPort -Port 7860) {
    Write-Host (
        "La Conversation App ya está activa en el puerto 7860."
    ) -ForegroundColor Yellow

    exit 0
}

# The anonymous default is the general Ahootsa profile.
# No user profile, session context or local API is loaded.
Set-AhootsaDotEnvProfile `
    -DotEnvPath $DotEnvPath `
    -ProfileName "ahootsa"

$env:REACHY_MINI_CUSTOM_PROFILE = "ahootsa"

$LogContext = New-AhootsaAnonymousLogContext `
    -ProjectRoot $ProjectRoot

$RunId = [string]$LogContext.RunId
$LogDirectory = [string]$LogContext.Directory
$LogFile = [string]$LogContext.LogFile

Set-Location $AppRoot
& $Activate

Write-Host ""
Write-Host "AHOOTSA - CONVERSACIÓN ANÓNIMA" -ForegroundColor Cyan
Write-Host "Perfil general: ahootsa" -ForegroundColor Gray
Write-Host "Sin usuario identificado." -ForegroundColor Yellow
Write-Host "Sin servidor local ni panel." -ForegroundColor Yellow
Write-Host "Sin informe personal." -ForegroundColor Yellow
Write-Host "Puerto: 7860" -ForegroundColor Gray
Write-Host "Logs: $LogDirectory" -ForegroundColor Gray
Write-Host ""

Start-Transcript `
    -Path $LogFile `
    -Force |
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

    Set-AhootsaDotEnvProfile `
        -DotEnvPath $DotEnvPath `
        -ProfileName "ahootsa"

    $env:REACHY_MINI_CUSTOM_PROFILE = "ahootsa"

    Invoke-AhootsaLogDiagnostics `
        -PythonExe $PythonExe `
        -DiagnosticTool $DiagnosticTool `
        -LogFile $LogFile `
        -OutputDirectory $LogDirectory `
        -Mode "anonymous" `
        -State "finished" `
        -RunId $RunId `
        -Profile "ahootsa" `
        -Voice "Sohee" |
        Out-Null

    Write-Host ""
    Write-Host "Conversación anónima finalizada." -ForegroundColor Yellow
}
