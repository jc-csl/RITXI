param(
    [string]$AppVenv = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv",
    [int]$DaemonPort = 8000
)
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Py = Join-Path $AppVenv "Scripts\python.exe"
$daemonUrl = "http://127.0.0.1:$DaemonPort"
Write-Host "============================================================"
Write-Host "Diagnóstico start-app Ahootsa 7.0.16"
Write-Host "============================================================"
Write-Host "Daemon: $daemonUrl"
Write-Host "Python: $Py"
Write-Host ""
Write-Host "[1] Paquete instalado / pip show"
& $Py -m pip show ahootsa-realtime-ollama-desktop-app
Write-Host ""
Write-Host "[2] Imports, versión y entrypoints"
& $Py -c "import importlib.metadata as m; import ahootsa_realtime_ollama_desktop_app as a; print('ahootsa package', a.__version__, a.__file__); print('entrypoints:', [(e.name,e.value) for e in m.entry_points(group='reachy_mini_apps')]); from ahootsa_realtime_ollama_desktop_app.main import AhootsaRealtimeOllamaApp; print('class ok', AhootsaRealtimeOllamaApp)"
Write-Host ""
Write-Host "[3] Dependencias críticas"
& $Py -c "import pygame, mujoco; print('pygame', pygame.version.ver); print('mujoco', mujoco.__version__)"
& $Py -c "import cv2; print('opencv', cv2.__version__)"
Write-Host ""
Write-Host "[4] Procesos daemon"
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'reachy-mini-daemon|ahootsa|conversation' } | Select-Object ProcessId, Name, CommandLine | Format-List
Write-Host ""
Write-Host "[5] Estado daemon"
try { Invoke-RestMethod -Uri "$daemonUrl/api/daemon/status" -TimeoutSec 5 | ConvertTo-Json -Depth 8 } catch { Write-Host $_.Exception.Message }
Write-Host ""
Write-Host "[6] Intento start-app con cuerpo de error"
try {
    Invoke-RestMethod -Method Post -Uri "$daemonUrl/api/apps/start-app/ahootsa_realtime_ollama_app" -TimeoutSec 30 | ConvertTo-Json -Depth 8
} catch {
    Write-Host "ERROR:" $_.Exception.Message
    try {
        $resp=$_.Exception.Response
        if ($resp) { $reader=New-Object System.IO.StreamReader($resp.GetResponseStream()); $body=$reader.ReadToEnd(); Write-Host "BODY:"; Write-Host $body }
    } catch {}
}
