$ErrorActionPreference = "Stop"
$Base = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Pythons = @(
    (Join-Path $Base "cpython-3.12-windows-x86_64-none\python.exe"),
    (Join-Path $Base ".venv\Scripts\python.exe"),
    (Join-Path $Base "apps_venv\Scripts\python.exe")
)

foreach ($Py in $Pythons) {
    if (Test-Path $Py) {
        Write-Host "Desinstalando de:" $Py -ForegroundColor Cyan
        & $Py -m pip uninstall -y ahootsa-realtime-ollama-desktop-app
    }
}

$Meta = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\.app_metadata\ahootsa_realtime_ollama_app.json"
if (Test-Path $Meta) {
    Remove-Item $Meta -Force
    Write-Host "Metadata eliminado:" $Meta -ForegroundColor Green
}
