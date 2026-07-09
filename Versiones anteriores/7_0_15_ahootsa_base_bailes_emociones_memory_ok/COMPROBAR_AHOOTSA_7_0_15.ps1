param(
    [string]$AppVenv = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv",
    [string]$OllamaBaseUrl = "http://127.0.0.1:11434"
)
$ErrorActionPreference = "Continue"
$Session = Get-Date -Format "yyyyMMdd_HHmmss"
$Out = "D:\RITXI\logs\ahootsa7_$($Session)_diagnostico.txt"
New-Item -ItemType Directory -Force -Path "D:\RITXI\logs" | Out-Null
Start-Transcript -LiteralPath $Out -Force | Out-Null
try {
    Write-Host "============================================================"
    Write-Host "Diagnóstico Ahootsa 7.0.15"
    Write-Host "============================================================"
    $Py = Join-Path $AppVenv "Scripts\python.exe"
    $Daemon = Join-Path $AppVenv "Scripts\reachy-mini-daemon.exe"
    Write-Host "Python: $Py"
    Write-Host "Daemon: $Daemon"
    if (Test-Path $Py) {
        $TmpPy = Join-Path $env:TEMP 'ahootsa_diag_imports_7_0_15.py'
@'
import importlib, importlib.metadata as m
mods = ['reachy_mini_conversation_app','ahootsa_realtime_ollama_desktop_app','pygame','mujoco','cv2','huggingface_hub']
for mod in mods:
    try:
        x = importlib.import_module(mod)
        print('IMPORT_OK', mod, getattr(x, '__version__', ''))
    except Exception as exc:
        print('IMPORT_FAIL', mod, type(exc).__name__, exc)
try:
    eps=[e for e in m.entry_points(group='reachy_mini_apps') if 'ahootsa' in e.name or 'conversation' in e.name]
    print('REACHY_ENTRYPOINTS', [(e.name, e.value) for e in eps])
except Exception as exc:
    print('ENTRYPOINTS_FAIL', exc)
'@ | Set-Content -Encoding UTF8 -LiteralPath $TmpPy
        & $Py $TmpPy
    }
    Write-Host "`n[Ollama]"
    try { Invoke-RestMethod -Uri "$OllamaBaseUrl/api/tags" -Method Get -TimeoutSec 5 | ConvertTo-Json -Depth 6 } catch { Write-Host "OLLAMA_FAIL $($_.Exception.Message)" }
    Write-Host "`n[Emotion library]"
    $emotionDir = "D:\RITXI\reachy-mini-emotions-library"
    if (Test-Path (Join-Path $emotionDir 'dance1.ogg')) { Write-Host "EMOTIONS_OK $emotionDir" } else { Write-Host "EMOTIONS_WARN No veo dance1.ogg en $emotionDir" }
    Write-Host "`n[Photos dir]"
    if (Test-Path "D:\RITXI\fotos") { Get-ChildItem "D:\RITXI\fotos" -ErrorAction SilentlyContinue | Select-Object -Last 5 | Format-Table } else { Write-Host "No existe D:\RITXI\fotos" }
    Write-Host "`n[App endpoints si están en marcha]"
    foreach($url in @('http://127.0.0.1:8000/api/daemon/status','http://127.0.0.1:7860/status','http://127.0.0.1:7860/ahootsa/status','http://127.0.0.1:7860/ollama/status','http://127.0.0.1:7860/audio/status','http://127.0.0.1:7860/memory/state','http://127.0.0.1:7860/memory/games','http://127.0.0.1:7860/camera_pc/latest')) {
        try { $r=Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 3; Write-Host "OK $url"; $r | ConvertTo-Json -Depth 6 } catch { Write-Host "NO $url -> $($_.Exception.Message)" }
    }
    Write-Host "`n[Procesos]"
    Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'ahootsa|reachy|ollama|uvicorn|python' } | Select-Object ProcessId, Name, CommandLine | Format-List
} finally {
    Stop-Transcript | Out-Null
    Write-Host "Diagnóstico guardado en $Out"
}

Write-Host ""
Write-Host "[INFO] Comprobando endpoints de configuración si la app está arrancada..."
try {
    $cfg = Invoke-RestMethod -Uri "http://127.0.0.1:7860/config/list" -Method Get -TimeoutSec 5
    Write-Host "CONFIG_LIST_OK archivos=" $cfg.files.Count
} catch {
    Write-Host "[WARN] No responde /config/list. Arranca primero LANZAR_AHOOTSA_7_0_15.ps1 si quieres probar el panel."
    Write-Host $_.Exception.Message
}
