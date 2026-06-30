# REPARAR_PANEL_INTEGRADO_DESKTOP.ps1
# Corrige la integración de Ahootsa en Reachy Mini Desktop.
# Problema: la app arranca, pero Desktop se queda en la lista Applications y no muestra el panel web integrado.
#
# Corrección:
# - usa http://localhost:7860 como URL embebible;
# - actualiza metadata local;
# - reinstala Ahootsa en los Python internos para que custom_app_url quede corregido;
# - mantiene intacta la app oficial.

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

function Install-In-Python($PythonExe, $Root) {
    Info "Reinstalando Ahootsa en: $PythonExe"
    & $PythonExe -m pip uninstall -y ahootsa-realtime-ollama-desktop-app 2>$null
    & $PythonExe -m pip install --no-deps --force-reinstall -e $Root
    if ($LASTEXITCODE -ne 0) {
        Warn "Instalación normal falló. Reintentando con --break-system-packages..."
        & $PythonExe -m pip install --break-system-packages --no-deps --force-reinstall -e $Root
    }
    if ($LASTEXITCODE -ne 0) {
        Fail "No se pudo instalar en $PythonExe"
    }
    & $PythonExe -c "import importlib.metadata as m; print('version=', m.version('ahootsa-realtime-ollama-desktop-app'))"
}

Header "Reparar panel integrado Desktop Ahootsa"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$MetaDir = Join-Path $DesktopDir ".app_metadata"
$MetadataPath = Join-Path $MetaDir "ahootsa_realtime_ollama_app.json"

if (-not (Test-Path $DesktopDir)) {
    Fail "No existe Reachy Mini Control. Abre Reachy Mini Desktop una vez."
}

Header "1. Liberar puerto 7860"
$conns = Get-NetTCPConnection -LocalPort 7860 -State Listen -ErrorAction SilentlyContinue
foreach ($conn in $conns) {
    try {
        Info "Cerrando PID $($conn.OwningProcess) en puerto 7860"
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    } catch {
        Warn "No se pudo cerrar PID $($conn.OwningProcess)"
    }
}

Header "2. Reinstalar wrapper Ahootsa con custom_app_url localhost"

$pythons = @(
    (Join-Path $DesktopDir "cpython-3.12-windows-x86_64-none\python.exe"),
    (Join-Path $DesktopDir ".venv\Scripts\python.exe"),
    (Join-Path $DesktopDir "apps_venv\Scripts\python.exe")
) | Where-Object { Test-Path $_ } | Select-Object -Unique

if ($pythons.Count -eq 0) {
    Fail "No se encontraron Python internos de Reachy Mini Desktop."
}

foreach ($py in $pythons) {
    Install-In-Python -PythonExe $py -Root $Root
}

Header "3. Actualizar metadata local"

New-Item -ItemType Directory -Force -Path $MetaDir | Out-Null

$metadata = @{
    _id = "local-ahootsa-realtime-ollama-app"
    id = "local-user/ahootsa_realtime_ollama_app"
    sdk = "static"
    author = "Centro San Luis"
    cardData = @{
        title = "Ahootsa Realtime Ollama"
        emoji = "🤖"
        short_description = "Conversación en español con herramientas originales, Ollama local y cámara PC en SIM"
        tags = @("reachy_mini", "reachy_mini_python_app", "ollama", "ahootsa")
    }
    host = "http://localhost:7860"
    url = "http://localhost:7860"
    app_url = "http://localhost:7860"
    custom_app_url = "http://localhost:7860/"
    isPythonApp = $true
} | ConvertTo-Json -Depth 10

$metadata | Set-Content -Encoding UTF8 $MetadataPath
Info "Metadata actualizada: $MetadataPath"

Header "4. Comprobación"

Get-Content $MetadataPath -Raw -Encoding UTF8

Write-Host ""
Write-Host "Comprobando custom_app_url importado:"
foreach ($py in $pythons) {
    Write-Host ""
    Write-Host "Python: $py"
    & $py -c "from ahootsa_realtime_ollama_desktop_app.main import AhootsaRealtimeOllamaApp; print(AhootsaRealtimeOllamaApp.custom_app_url)"
}

Header "Final"

Write-Host "Ahora:"
Write-Host "1. Cierra completamente Reachy Mini Desktop."
Write-Host "2. Comprueba que no queda ningún proceso Reachy Mini Desktop abierto."
Write-Host "3. Abre Reachy Mini Desktop."
Write-Host "4. Pulsa Start en Ahootsa Realtime Ollama."
Write-Host "5. Si no cambia automáticamente al panel, pulsa dos veces sobre la tarjeta verde de Ahootsa o el icono de abrir si aparece."
Write-Host ""
Write-Host "Si el panel integrado sigue sin aparecer, prueba en navegador:"
Write-Host "http://localhost:7860"
Write-Host ""
Write-Host "Si localhost funciona pero Desktop no lo incrusta, el problema está en la gestión del WebView de Desktop, no en Ahootsa."
