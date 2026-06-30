# INSTALAR_CAMARA_PC.ps1
# Instala OpenCV en el entorno Python que usa Reachy Mini Desktop para que camera_pc funcione.
# No modifica el código original de la app oficial.

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Info($Text) { Write-Host "[INFO] $Text" }
function Warn($Text) { Write-Host "[AVISO] $Text" -ForegroundColor Yellow }
function Fail($Text) { Write-Host "[ERROR] $Text" -ForegroundColor Red; exit 1 }

Header "Instalar soporte de cámara PC para Ahootsa"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$pythons = @(
    (Join-Path $DesktopDir "apps_venv\Scripts\python.exe"),
    (Join-Path $DesktopDir ".venv\Scripts\python.exe"),
    (Join-Path $DesktopDir "cpython-3.12-windows-x86_64-none\python.exe")
) | Where-Object { Test-Path $_ } | Select-Object -Unique

if ($pythons.Count -eq 0) {
    Fail "No se encontraron Python internos de Reachy Mini Desktop."
}

foreach ($py in $pythons) {
    Info "Comprobando OpenCV en: $py"
    & $py -c "import cv2; print('opencv=', cv2.__version__)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Info "OpenCV ya está instalado en $py"
        continue
    }

    Info "Instalando opencv-python en: $py"
    & $py -m pip install opencv-python
    if ($LASTEXITCODE -ne 0) {
        Warn "Instalación normal falló. Reintentando con --break-system-packages..."
        & $py -m pip install --break-system-packages opencv-python
    }

    & $py -c "import cv2; print('opencv=', cv2.__version__)"
    if ($LASTEXITCODE -ne 0) {
        Warn "No se pudo verificar OpenCV en $py"
    }
}

Header "Final"
Write-Host "Soporte camera_pc instalado/verificado."
Write-Host "Puedes probar con:"
Write-Host "powershell -ExecutionPolicy Bypass -File .\test\PROBAR_CAMARA_PC.ps1"
