param(
    [switch]$IncludeDaemon
)

$ErrorActionPreference = "Continue"
$projectRoot = $PSScriptRoot
$utilsPath = Join-Path $projectRoot "scripts\ahootsa_process_utils.ps1"

if (-not (Test-Path $utilsPath)) {
    throw "Missing process utility: $utilsPath"
}
. $utilsPath

Write-Host "Stopping Ahootsa services..." -ForegroundColor Cyan

Stop-AhootsaConversationAppGracefully | Out-Null
Stop-AhootsaPortProcess `
    -Port 7860 `
    -ServiceName "Reachy Mini Conversation App" |
    Out-Null

Stop-AhootsaPortProcess `
    -Port 8100 `
    -ServiceName "Ahootsa Local Server" |
    Out-Null

if ($IncludeDaemon) {
    Stop-AhootsaPortProcess `
        -Port 8000 `
        -ServiceName "Reachy Mini daemon" |
        Out-Null
}

Write-Host ""
Write-Host "Requested services are stopped." -ForegroundColor Green
if (-not $IncludeDaemon) {
    Write-Host (
        "The daemon was preserved. Use -IncludeDaemon to stop it too."
    ) -ForegroundColor Gray
}
