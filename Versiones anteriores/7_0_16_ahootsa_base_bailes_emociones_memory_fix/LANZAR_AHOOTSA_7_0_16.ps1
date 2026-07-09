param(
    [string]$AppVenv = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv",
    [ValidateSet("ahootsa7_rapido", "ahootsa7_realtime_es", "ahootsa7_actividades", "ahootsa7_completo")][string]$Profile = "ahootsa7_realtime_es",
    [ValidateSet("deployed", "local")][string]$HFMode = "deployed",
    [string]$HFLocalWsUrl = "ws://127.0.0.1:8765/v1/realtime",
    [string]$OllamaModel = "llama3.2:3b",
    [string]$OllamaBaseUrl = "http://127.0.0.1:11434",
    [int]$DaemonPort = 8000,
    [int]$UiPort = 7860,
    [switch]$NoInstall,
    [switch]$ForceInstall,
    [switch]$RestartDaemon,
    [switch]$SkipMujoco,
    [switch]$SkipPygame,
    [switch]$SkipOpenCV,
    [switch]$SkipEmotionLibraryDownload
)
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Session = Get-Date -Format "yyyyMMdd_HHmmss"
$LogRoot = "D:\RITXI\logs"
$FotosRoot = "D:\RITXI\fotos"
New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
New-Item -ItemType Directory -Force -Path $FotosRoot | Out-Null
$PantallaLog = Join-Path $LogRoot "ahootsa7_$($Session)_pantalla.log"
$RuntimeLog = Join-Path $LogRoot "ahootsa7_$($Session)_runtime.log"
$EventosLog = Join-Path $LogRoot "ahootsa7_$($Session)_eventos.jsonl"
Start-Transcript -LiteralPath $PantallaLog -Force | Out-Null
try {
    Write-Host "============================================================"
    Write-Host "Ahootsa 7.0.16 - base estable instalable"
    Write-Host "============================================================"
    Write-Host "Root:    $Root"
    Write-Host "Logs:    $LogRoot"
    Write-Host "Fotos:   $FotosRoot"
    Write-Host "Session: $Session"
    Write-Host "Profile: $Profile"
    Write-Host "HFMode:  $HFMode"
    Write-Host "Ollama:  $OllamaModel"
    $Py = Join-Path $AppVenv "Scripts\python.exe"
    $Daemon = Join-Path $AppVenv "Scripts\reachy-mini-daemon.exe"
    if (-not (Test-Path -LiteralPath $Py)) { throw "No encuentro python.exe en $Py. Instala Reachy Mini Control/Desktop Control." }
    if (-not (Test-Path -LiteralPath $Daemon)) { throw "No encuentro reachy-mini-daemon.exe en $Daemon." }

    $NeedsInstall = $ForceInstall.IsPresent
    if (-not $NoInstall) {
        & $Py -c "import sys, importlib.metadata as m; import ahootsa_realtime_ollama_desktop_app as a; eps=list(m.entry_points(group='reachy_mini_apps')); print('AHOOTSA_INSTALLED_VERSION', a.__version__); print('HAS_AHOOTSA_ENTRYPOINT', any(e.name=='ahootsa_realtime_ollama_app' for e in eps)); sys.exit(0 if a.__version__=='7.0.16' and any(e.name=='ahootsa_realtime_ollama_app' for e in eps) else 7)"
        if ($LASTEXITCODE -ne 0) { $NeedsInstall = $true }
    }
    if ($NeedsInstall -and -not $NoInstall) {
        Write-Host "[INFO] Instalación activa no es 7.0.16 o falta entrypoint. Instalando 7.0.16..."
        $argsInstall = @('-ExecutionPolicy','Bypass','-File',(Join-Path $Root 'INSTALAR_AHOOTSA_7_0_16.ps1'),'-AppVenv',$AppVenv)
        if ($SkipMujoco) { $argsInstall += '-SkipMujoco' }
        if ($SkipPygame) { $argsInstall += '-SkipPygame' }
        if ($SkipOpenCV) { $argsInstall += '-SkipOpenCV' }
        if ($SkipEmotionLibraryDownload) { $argsInstall += '-SkipEmotionLibraryDownload' }
        & powershell @argsInstall
        if ($LASTEXITCODE -ne 0) { throw "No se pudo instalar Ahootsa 7.0.16." }
        $RestartDaemon = $true
    }
    & $Py -c "import ahootsa_realtime_ollama_desktop_app as a; print('AHOOTSA_IMPORT_OK', a.__version__)"
    if ($LASTEXITCODE -ne 0) { throw "No importa Ahootsa después de instalar." }
    & $Py -c "import importlib.metadata as m; eps=list(m.entry_points(group='reachy_mini_apps')); print('REACHY_MINI_APPS_ENTRYPOINTS', [(e.name,e.value) for e in eps]); raise SystemExit(0 if any(e.name=='ahootsa_realtime_ollama_app' for e in eps) else 2)"
    if ($LASTEXITCODE -ne 0) { throw "El entrypoint ahootsa_realtime_ollama_app no está registrado." }
    & $Py -c "import pygame; print('PYGAME_OK', pygame.version.ver)"
    if ($LASTEXITCODE -ne 0) { Write-Host "[WARN] pygame no está disponible. Instala con INSTALAR_AHOOTSA_7_0_16.ps1." }

    $env:AHOOTSA_SESSION_ID = $Session
    $env:AHOOTSA_LOG_DIR = $LogRoot
    $env:AHOOTSA_LOG_FILE_RUNTIME = $RuntimeLog
    $env:AHOOTSA_LOG_FILE_EVENTS = $EventosLog
    $env:AHOOTSA_PROFILE = $Profile
    $env:AHOOTSA_PHOTOS_DIR = $FotosRoot
    $env:HF_REALTIME_CONNECTION_MODE = $HFMode
    if ($HFMode -eq 'local') { $env:HF_REALTIME_WS_URL = $HFLocalWsUrl } else { Remove-Item Env:\HF_REALTIME_WS_URL -ErrorAction SilentlyContinue }
    $env:OLLAMA_MODEL = $OllamaModel
    $env:OLLAMA_BASE_URL = $OllamaBaseUrl
    $env:OLLAMA_VISION_MODEL = "llava:latest"
    $env:AHOOTSA_DISABLE_EMOTION_AUDIO = '0'
    $env:AHOOTSA_EMOTION_AUDIO_BACKEND = 'pygame'
    $env:AHOOTSA_MEMORY_WINSOUND_ENABLED = '0'
    $env:AHOOTSA_IDLE_REMINDER_ENABLED = '0'
    $env:AHOOTSA_POST_PLAY_WAIT_SECONDS = '0.6'
    $env:REALTIME_TRANSCRIPTION_LANGUAGE = 'es'
    $env:VOICE = 'Sohee'
    $env:REACHY_MINI_VOICE = 'Sohee'
    $env:AHOOTSA_VOICE = 'Sohee'

    try {
        $tags = Invoke-RestMethod -Uri "$OllamaBaseUrl/api/tags" -Method Get -TimeoutSec 4
        $names = @($tags.models | ForEach-Object { $_.name })
        Write-Host "[INFO] Modelos Ollama: $($names -join ', ')"
        if ($names -notcontains $OllamaModel) { Write-Host "[WARN] El modelo Ollama indicado no aparece en ollama list: $OllamaModel" }
    } catch { Write-Host "[WARN] Ollama no responde en $OllamaBaseUrl. La conversación HF puede funcionar; el panel Ollama no." }

    function Test-Url($Url) { try { Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 2 | Out-Null; return $true } catch { return $false } }
    function Stop-ReachyDaemonIfNeeded {
        Write-Host "[INFO] Reiniciando daemon para que cargue entrypoints actualizados..."
        Get-CimInstance Win32_Process |
            Where-Object { $_.CommandLine -match 'reachy-mini-daemon' } |
            ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; Write-Host "[OK] Daemon detenido PID $($_.ProcessId)" } catch {} }
        Start-Sleep -Seconds 2
    }
    if ($RestartDaemon) { Stop-ReachyDaemonIfNeeded }
    $daemonUrl = "http://127.0.0.1:$DaemonPort"
    if (-not (Test-Url "$daemonUrl/api/daemon/status")) {
        Write-Host "[INFO] Arrancando daemon MuJoCo..."
        $Tmp = Join-Path $Root ".tmp"
        New-Item -ItemType Directory -Force -Path $Tmp | Out-Null
        $DaemonScript = Join-Path $Tmp "start_daemon_$Session.ps1"
@"
`$env:AHOOTSA_SESSION_ID='$Session'
`$env:AHOOTSA_LOG_DIR='$LogRoot'
`$env:AHOOTSA_LOG_FILE_RUNTIME='$RuntimeLog'
& '$Daemon' --sim --fastapi-host 127.0.0.1 --fastapi-port $DaemonPort --no-goto-sleep-on-stop --dataset-update-interval 0 --no-preload-datasets --log-file '$RuntimeLog'
"@ | Set-Content -Encoding UTF8 -LiteralPath $DaemonScript
        Start-Process powershell -ArgumentList @('-ExecutionPolicy','Bypass','-File',$DaemonScript) -WindowStyle Minimized | Out-Null
        for ($i=1; $i -le 35; $i++) { Start-Sleep -Seconds 1; if (Test-Url "$daemonUrl/api/daemon/status") { break }; Write-Host "Esperando daemon... $i" }
    }
    if (-not (Test-Url "$daemonUrl/api/daemon/status")) { throw "Daemon no disponible en $daemonUrl" }
    Write-Host "[OK] Daemon disponible en $daemonUrl"
    Write-Host "[INFO] Arrancando app Ahootsa 7.0.16..."
    try {
        Invoke-RestMethod -Method Post -Uri "$daemonUrl/api/apps/start-app/ahootsa_realtime_ollama_app" -TimeoutSec 30 | Out-Null
    } catch {
        Write-Host "[ERROR] No se pudo arrancar ahootsa_realtime_ollama_app"
        Write-Host $_.Exception.Message
        try {
            $resp = $_.Exception.Response
            if ($resp) {
                $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
                $body = $reader.ReadToEnd()
                if ($body) { Write-Host "[ERROR_BODY] $body" }
            }
        } catch {}
        Write-Host "[INFO] Ejecuta DIAGNOSTICAR_START_APP_7_0_16.ps1 y RESUMIR_LOGS_AHOOTSA_7_0_16.ps1"
        throw
    }
    $ui = "http://127.0.0.1:$UiPort"
    for ($i=1; $i -le 45; $i++) { Start-Sleep -Seconds 1; if ((Test-Url "$ui/ahootsa/status") -or (Test-Url "$ui/ahootsa")) { break }; Write-Host "Esperando interfaz... $i" }
    Write-Host "[OK] Interfaz Ahootsa: $ui/ahootsa"
    Start-Process "$ui/ahootsa"
} finally {
    try { Stop-Transcript | Out-Null } catch {}
}
