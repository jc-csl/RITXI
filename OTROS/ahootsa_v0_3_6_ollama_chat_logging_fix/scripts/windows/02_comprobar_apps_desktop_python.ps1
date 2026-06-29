$ErrorActionPreference = "Stop"
$Base = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Pythons = @(
    (Join-Path $Base "cpython-3.12-windows-x86_64-none\python.exe"),
    (Join-Path $Base ".venv\Scripts\python.exe"),
    (Join-Path $Base "apps_venv\Scripts\python.exe")
)
foreach ($Py in $Pythons) {
    if (Test-Path $Py) {
        Write-Host ""; Write-Host $Py -ForegroundColor Cyan
        & $Py -c "import importlib.metadata as m; print([ep.name for ep in m.entry_points(group='reachy_mini_apps')])"
    }
}
