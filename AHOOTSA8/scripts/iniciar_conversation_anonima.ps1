param(
    [switch]$DebugMode
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
$AppRoot = Join-Path $ProjectRoot "reachy_mini_conversation_app"
$UtilsPath = Join-Path $PSScriptRoot "ahootsa_process_utils.ps1"
$Activate = Join-Path $AppRoot ".venv\Scripts\Activate.ps1"
$DotEnvPath = Join-Path $AppRoot ".env"
$LogDirectory = Join-Path $ProjectRoot "logs\anonymous"
$LogFile = Join-Path $LogDirectory "conversation_app.log"

if (-not (Test-Path $UtilsPath)) {
    throw "No se encuentra la utilidad de procesos: $UtilsPath"
}

. $UtilsPath

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

New-Item `
    -ItemType Directory `
    -Path $LogDirectory `
    -Force |
    Out-Null

if (Test-Path $LogFile) {
    Remove-Item $LogFile -Force
}

Set-Location $AppRoot
& $Activate

Write-Host ""
Write-Host "AHOOTSA - CONVERSACIÓN ANÓNIMA" -ForegroundColor Cyan
Write-Host "Perfil general: ahootsa" -ForegroundColor Gray
Write-Host "Sin usuario identificado." -ForegroundColor Yellow
Write-Host "Sin servidor local ni panel." -ForegroundColor Yellow
Write-Host "Sin informe personal." -ForegroundColor Yellow
Write-Host "Puerto: 7860" -ForegroundColor Gray
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

    Write-Host ""
    Write-Host "Conversación anónima finalizada." -ForegroundColor Yellow
}
