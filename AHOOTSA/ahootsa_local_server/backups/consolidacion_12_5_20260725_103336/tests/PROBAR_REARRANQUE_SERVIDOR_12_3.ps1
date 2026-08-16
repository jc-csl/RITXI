$ErrorActionPreference = "Stop"
$projectRoot = "D:\RITXI\AHOOTSA8"
$serverRoot = Join-Path $projectRoot "ahootsa_local_server"
$launcher = Join-Path $serverRoot "3_lanzar_ahootsa_server.ps1"
$utilsPath = Join-Path $projectRoot "scripts\ahootsa_process_utils.ps1"

. $utilsPath

$oldPids = @(Get-AhootsaPortProcessIds -Port 8100)
Write-Host "Old server PIDs: $($oldPids -join ', ')" -ForegroundColor Gray

Start-Process `
    -FilePath "powershell.exe" `
    -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $launcher
    ) |
    Out-Null

if (-not (Wait-AhootsaPortOpen -Port 8100 -TimeoutSeconds 30)) {
    throw "The local server did not start on port 8100."
}

Start-Sleep -Seconds 1
$health = Invoke-RestMethod "http://127.0.0.1:8100/health"
if ($health.version -ne "0.12.3") {
    throw "Wrong server version after restart: $($health.version)"
}

$newPids = @(Get-AhootsaPortProcessIds -Port 8100)
if ($newPids.Count -eq 0) {
    throw "No listener was found on port 8100."
}

if ($oldPids.Count -gt 0) {
    foreach ($oldPid in $oldPids) {
        if ($newPids -contains $oldPid) {
            throw "The previous server PID $oldPid was not replaced."
        }
    }
}

Write-Host ""
Write-Host "UPDATE 12.3 CLEAN SERVER RESTART VALIDATED." -ForegroundColor Green
Write-Host "New server PIDs: $($newPids -join ', ')" -ForegroundColor Green
