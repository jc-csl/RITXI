$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
$utilsPath = Join-Path $projectRoot "scripts\ahootsa_process_utils.ps1"

if (-not (Test-Path $utilsPath)) {
    throw "Missing process utility: $utilsPath"
}
. $utilsPath

$services = @(
    @{ Name = "Reachy Mini daemon"; Port = 8000 },
    @{ Name = "Conversation App"; Port = 7860 },
    @{ Name = "Ahootsa Local Server"; Port = 8100 }
)

foreach ($service in $services) {
    $pids = @(Get-AhootsaPortProcessIds -Port $service.Port)
    if ($pids.Count -eq 0) {
        Write-Host (
            "{0,-28} port {1}: STOPPED" -f $service.Name, $service.Port
        ) -ForegroundColor DarkGray
        continue
    }

    foreach ($processId in $pids) {
        $processName = "unknown"
        try {
            $processName = (Get-Process -Id $processId -ErrorAction Stop).ProcessName
        } catch {}

        Write-Host (
            "{0,-28} port {1}: RUNNING PID {2} ({3})" -f `
                $service.Name,
                $service.Port,
                $processId,
                $processName
        ) -ForegroundColor Green
    }
}
