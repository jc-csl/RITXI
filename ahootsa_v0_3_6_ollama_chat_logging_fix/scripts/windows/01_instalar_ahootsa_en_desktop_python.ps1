$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Ahootsa v0.3.6 - instalar en Reachy Desktop" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Cierra primero Reachy Mini Desktop App y cualquier daemon activo." -ForegroundColor Yellow
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
        & $Py -m pip install --break-system-packages --no-deps -e $ProjectRoot
        Write-Host "Entry-points reachy_mini_apps:" -ForegroundColor Cyan
        & $Py -c "import importlib.metadata as m; print([ep.name for ep in m.entry_points(group='reachy_mini_apps')])"
    } else {
        Write-Host "No existe, se omite:" $Py -ForegroundColor DarkYellow
    }
}

Write-Host ""
Write-Host "Listo. Ahora ejecuta, opcionalmente:" -ForegroundColor Green
Write-Host "  scripts\windows\04_instalar_logo_ahootsa_en_conversation_ui.ps1" -ForegroundColor Green
Write-Host ""
Write-Host "Abre Reachy Mini Desktop App y pulsa Start en Ahootsa Ollama Local o Ahootsa clásico." -ForegroundColor Green
Write-Host "Panel Ahootsa clásico:" -ForegroundColor Green
Write-Host "  http://127.0.0.1:7860" -ForegroundColor Green
Write-Host "Panel Ahootsa Ollama Local Chat:" -ForegroundColor Green
Write-Host "  http://127.0.0.1:7862" -ForegroundColor Green
