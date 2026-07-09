param(
    [string]$AppVenv = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv",
    [string]$Profile = "ahootsa_realtime_es",
    [ValidateSet("deployed", "local")][string]$HFMode = "deployed",
    [string]$HFLocalWsUrl = "ws://127.0.0.1:8765/v1/realtime",
    [string]$OllamaModel = "llama3.2:3b",
    [string]$OllamaBaseUrl = "http://127.0.0.1:11434",
    [int]$DaemonPort = 8000,
    [int]$UiPort = 7860,
    [switch]$Install,
    [switch]$InstallMujoco,
    [switch]$InstallOpenCV
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Session = Get-Date -Format "yyyyMMdd_HHmmss"
$LogRoot = "D:\RITXI\logs"
New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
$PantallaLog = Join-Path $LogRoot "ahootsa5_$($Session)_pantalla.log"
$RuntimeLog = Join-Path $LogRoot "ahootsa5_$($Session)_runtime.log"
$EventosLog = Join-Path $LogRoot "ahootsa5_$($Session)_eventos.jsonl"
Start-Transcript -LiteralPath $PantallaLog -Force | Out-Null
try {
    Write-Host "============================================================"
    Write-Host "Ahootsa 5.0.44 - base estable instalable"
    Write-Host "============================================================"
    Write-Host "Root:    $Root"
    Write-Host "Logs:    $LogRoot"
    Write-Host "Session: $Session"
    Write-Host "Profile: $Profile"
    Write-Host "HFMode:  $HFMode"
    Write-Host "Ollama:  $OllamaModel"
    $Py = Join-Path $AppVenv "Scripts\python.exe"
    $Daemon = Join-Path $AppVenv "Scripts\reachy-mini-daemon.exe"
    if (-not (Test-Path -LiteralPath $Py)) { throw "No encuentro python.exe en $Py. Instala Reachy Mini Control/Desktop Control." }
    if (-not (Test-Path -LiteralPath $Daemon)) { throw "No encuentro reachy-mini-daemon.exe en $Daemon." }
    if ($Install) {
        $argsInstall = @('-ExecutionPolicy','Bypass','-File',(Join-Path $Root 'INSTALAR_AHOOTSA_5_0_44.ps1'),'-AppVenv',$AppVenv)
        if ($InstallMujoco) { $argsInstall += '-InstallMujoco' }
        if ($InstallOpenCV) { $argsInstall += '-InstallOpenCV' }
        & powershell @argsInstall
    }
    & $Py -c "import ahootsa_realtime_ollama_desktop_app as a; print('AHOOTSA_IMPORT_OK', a.__version__)"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[INFO] Ahootsa no está instalada; instalando..."
        & powershell -ExecutionPolicy Bypass -File (Join-Path $Root 'INSTALAR_AHOOTSA_5_0_44.ps1') -AppVenv $AppVenv
    }
    $env:AHOOTSA_SESSION_ID = $Session
    $env:AHOOTSA_LOG_DIR = $LogRoot
    $env:AHOOTSA_LOG_FILE_RUNTIME = $RuntimeLog
    $env:AHOOTSA_LOG_FILE_EVENTS = $EventosLog
    $env:AHOOTSA_PROFILE = $Profile
    $env:HF_REALTIME_CONNECTION_MODE = $HFMode
    if ($HFMode -eq 'local') { $env:HF_REALTIME_WS_URL = $HFLocalWsUrl } else { Remove-Item Env:\HF_REALTIME_WS_URL -ErrorAction SilentlyContinue }
    $env:OLLAMA_MODEL = $OllamaModel
    $env:OLLAMA_BASE_URL = $OllamaBaseUrl
    $env:AHOOTSA_DISABLE_EMOTION_AUDIO = '1'
    $env:AHOOTSA_MEMORY_WINSOUND_ENABLED = '0'
    $env:AHOOTSA_IDLE_REMINDER_ENABLED = '0'
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
        for ($i=1; $i -le 30; $i++) { Start-Sleep -Seconds 1; if (Test-Url "$daemonUrl/api/daemon/status") { break }; Write-Host "Esperando daemon... $i" }
    }
    if (-not (Test-Url "$daemonUrl/api/daemon/status")) { throw "Daemon no disponible en $daemonUrl" }
    Write-Host "[OK] Daemon disponible en $daemonUrl"
    Write-Host "[INFO] Arrancando app Ahootsa..."
    Invoke-RestMethod -Method Post -Uri "$daemonUrl/api/apps/start-app/ahootsa_realtime_ollama_app" -TimeoutSec 20 | Out-Null
    $ui = "http://127.0.0.1:$UiPort"
    for ($i=1; $i -le 45; $i++) { Start-Sleep -Seconds 1; if (Test-Url "$ui/status") { break }; Write-Host "Esperando interfaz... $i" }
    Write-Host "[OK] Interfaz Ahootsa: $ui/ahootsa"
    Start-Process "$ui/ahootsa"
} finally {
    Stop-Transcript | Out-Null
}
