$ErrorActionPreference = "Stop"
$projectRoot = "D:\RITXI\AHOOTSA8"
$serverRoot = Join-Path $projectRoot "ahootsa_local_server"

Write-Host "1. Checking server version..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod "http://127.0.0.1:8100/health" -TimeoutSec 3
} catch {
    throw "Start the local server with .\3_lanzar_ahootsa_server.ps1."
}

if ($health.version -ne "0.12.3") {
    throw "Expected version 0.12.3, found $($health.version)."
}
Write-Host "   Version 0.12.3 is correct." -ForegroundColor Green

Write-Host "2. Checking process utility and launchers..." -ForegroundColor Cyan
$files = @(
    (Join-Path $projectRoot "scripts\ahootsa_process_utils.ps1"),
    (Join-Path $projectRoot "0_detener_servicios_ahootsa.ps1"),
    (Join-Path $projectRoot "1_lanzar_daemon_mujoco.ps1"),
    (Join-Path $projectRoot "2_lanzar_app_ahootsa.ps1"),
    (Join-Path $serverRoot "3_lanzar_ahootsa_server.ps1")
)

foreach ($file in $files) {
    if (-not (Test-Path $file)) {
        throw "Missing file: $file"
    }

    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile(
        $file,
        [ref]$tokens,
        [ref]$errors
    ) | Out-Null

    if ($errors.Count -gt 0) {
        throw "PowerShell syntax error in $file : $($errors[0].Message)"
    }
}
Write-Host "   All startup scripts have valid syntax." -ForegroundColor Green

Write-Host "3. Checking cleanup rules..." -ForegroundColor Cyan
$daemonText = Get-Content (Join-Path $projectRoot "1_lanzar_daemon_mujoco.ps1") -Raw
$appText = Get-Content (Join-Path $projectRoot "2_lanzar_app_ahootsa.ps1") -Raw
$serverText = Get-Content (Join-Path $serverRoot "3_lanzar_ahootsa_server.ps1") -Raw

if ($daemonText -notmatch 'Port 8000') {
    throw "Daemon launcher does not clean port 8000."
}
if ($appText -notmatch 'Port 7860') {
    throw "Conversation App launcher does not clean port 7860."
}
if ($serverText -notmatch 'Port 8100') {
    throw "Local server launcher does not clean port 8100."
}

Write-Host "   Ports 8000, 7860 and 8100 are managed." -ForegroundColor Green
Write-Host ""
Write-Host "UPDATE 12.3 STARTUP SCRIPTS VALIDATED." -ForegroundColor Green
