$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Ahootsa Realtime Ollama v0.4.34 - instalar" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Cierra primero Reachy Mini Desktop App y cualquier app Ahootsa activa." -ForegroundColor Yellow
Write-Host ""

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Base = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"

$Pythons = @(
    (Join-Path $Base "cpython-3.12-windows-x86_64-none\python.exe"),
    (Join-Path $Base ".venv\Scripts\python.exe"),
    (Join-Path $Base "apps_venv\Scripts\python.exe")
)

foreach ($Py in $Pythons) {
    if (Test-Path $Py) {
        Write-Host ""
        Write-Host "Instalando en:" $Py -ForegroundColor Cyan
        Write-Host "Base estable: se mantienen intactas las herramientas originales de la app oficial." -ForegroundColor Cyan
        & $Py -m pip install --break-system-packages --no-deps -e $ProjectRoot
        Write-Host "Entry-points reachy_mini_apps:" -ForegroundColor Cyan
        & $Py -c "import importlib.metadata as m; print([ep.name for ep in m.entry_points(group='reachy_mini_apps')])"
        Write-Host "Modulo cargado desde:" -ForegroundColor Cyan
        & $Py -c "import ahootsa_realtime_ollama_desktop_app.main as mod; print(mod.__file__)"
    } else {
        Write-Host "No existe, se omite:" $Py -ForegroundColor DarkYellow
    }
}

Write-Host ""
Write-Host "Instalacion terminada." -ForegroundColor Green
Write-Host "Ejecuta ahora:" -ForegroundColor Green
Write-Host "  .\scripts\windows\05_instalar_metadata_desktop.ps1" -ForegroundColor Green
