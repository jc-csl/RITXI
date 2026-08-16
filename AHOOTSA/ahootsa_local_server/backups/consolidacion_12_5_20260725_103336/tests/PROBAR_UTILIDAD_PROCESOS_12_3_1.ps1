$ErrorActionPreference = "Stop"

$projectRoot = "D:\RITXI\AHOOTSA8"
$utilsPath = Join-Path $projectRoot "scripts\ahootsa_process_utils.ps1"

if (-not (Test-Path $utilsPath)) {
    throw "Missing process utility: $utilsPath"
}

. $utilsPath

Write-Host "Checking process utility load..." -ForegroundColor Cyan

$requiredFunctions = @(
    "Get-AhootsaPortProcessIds",
    "Test-AhootsaPort",
    "Wait-AhootsaPortClosed",
    "Wait-AhootsaPortOpen",
    "Stop-AhootsaPortProcess",
    "Stop-AhootsaCommandProcesses",
    "Stop-AhootsaConversationAppGracefully"
)

foreach ($name in $requiredFunctions) {
    $command = Get-Command $name -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        throw "Function was not loaded: $name"
    }
    Write-Host "  OK: $name" -ForegroundColor Green
}

$pids = @(Get-AhootsaPortProcessIds -Port 8100)
Write-Host "Port 8100 listener count: $($pids.Count)" -ForegroundColor Gray

Write-Host ""
Write-Host "UPDATE 12.3.1 PROCESS UTILITY VALIDATED." -ForegroundColor Green
