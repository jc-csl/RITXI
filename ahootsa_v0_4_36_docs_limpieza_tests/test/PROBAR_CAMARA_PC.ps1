# PROBAR_CAMARA_PC.ps1
# Ubicación actual: subcarpeta test.
# Ejecutar desde la raíz con: powershell -ExecutionPolicy Bypass -File .\test\PROBAR_CAMARA_PC.ps1

# Prueba la webcam del PC desde el Python de Reachy Mini Desktop.

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Fail($Text) { Write-Host "[ERROR] $Text" -ForegroundColor Red; exit 1 }

Header "Probar cámara PC"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Python = Join-Path $DesktopDir "apps_venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Fail "No existe apps_venv Python: $Python"
}

$tmp = Join-Path $env:TEMP "probar_camera_pc_ahootsa.py"

@'
import os, datetime, pathlib, sys, time

try:
    import cv2
except Exception as e:
    print("ERROR: no se puede importar cv2:", repr(e))
    sys.exit(2)

out_dir = pathlib.Path(os.environ.get("LOCALAPPDATA", ".")) / "Reachy Mini Control" / "ahootsa_captures"
out_dir.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: no se puede abrir la cámara índice 0.")
    sys.exit(3)

frame = None
for _ in range(5):
    ok, frame = cap.read()
    time.sleep(0.05)

ok, frame = cap.read()
cap.release()

if not ok or frame is None:
    print("ERROR: la cámara no devolvió imagen.")
    sys.exit(4)

path = out_dir / ("test_camera_pc_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg")
if not cv2.imwrite(str(path), frame):
    print("ERROR: no se pudo guardar", path)
    sys.exit(5)

print("OK")
print(path)
'@ | Set-Content -Encoding UTF8 $tmp

& $Python $tmp

Remove-Item $tmp -Force -ErrorAction SilentlyContinue

Header "Final"
Write-Host "Si aparece OK y una ruta .jpg, camera_pc debería funcionar."
