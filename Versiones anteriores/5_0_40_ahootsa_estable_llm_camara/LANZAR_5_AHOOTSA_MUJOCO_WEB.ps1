# LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
# Ahootsa 5.0.34
# Arranca daemon MuJoCo + app Ahootsa. Logs SOLO en D:\RITXI\logs.
# Corrige placeholders y redireccion de logs del script temporal del daemon.

param(
    [int]$Port = 8000,
    [string]$HostAddress = "127.0.0.1",
    [string]$AppName = "ahootsa_realtime_ollama_app",
    [switch]$NoStartApp,
    [switch]$NoOpenBrowser,
    [switch]$StopExistingApp,
    [switch]$Headless
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogRoot = "D:\RITXI\logs"
if (-not (Test-Path -LiteralPath $LogRoot)) {
    New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
}

if (-not $env:AHOOTSA_SESSION_ID -or $env:AHOOTSA_SESSION_ID.Trim().Length -eq 0) {
    $env:AHOOTSA_SESSION_ID = Get-Date -Format "yyyyMMdd_HHmmss"
}
$Session = if ($env:AHOOTSA_SESSION) { $env:AHOOTSA_SESSION } else { Get-Date -Format "yyyyMMdd_HHmmss" }
$env:AHOOTSA_LOG_DIR = $LogRoot
[Environment]::SetEnvironmentVariable("AHOOTSA_LOG_DIR", $LogRoot, "User")

$env:AHOOTSA_LOG_FILE_SCREEN = Join-Path $LogRoot ("ahootsa5_" + $Session + "_pantalla.log")
$env:AHOOTSA_LOG_FILE_EVENTS = Join-Path $LogRoot ("ahootsa5_" + $Session + "_eventos.jsonl")
$env:AHOOTSA_LOG_FILE_RUNTIME = Join-Path $LogRoot ("ahootsa5_" + $Session + "_runtime.log")
$PsLog = $env:AHOOTSA_LOG_FILE_SCREEN
$JsonLog = $env:AHOOTSA_LOG_FILE_EVENTS

try { Start-Transcript -LiteralPath $PsLog -Append | Out-Null } catch {}

function Write-AhootsaEvent {
    param([string]$Event, [hashtable]$Data = @{})
    $Obj = [ordered]@{
        ts = (Get-Date).ToString("o")
        event = $Event
        session_id = $env:AHOOTSA_SESSION_ID
        pid = $PID
    }
    foreach ($K in $Data.Keys) { $Obj[$K] = $Data[$K] }
    try {
        ($Obj | ConvertTo-Json -Depth 12 -Compress) | Add-Content -Encoding UTF8 -LiteralPath $JsonLog
    } catch {}
}

function Test-PortOpen {
    param([int]$TestPort)
    try {
        $Client = New-Object System.Net.Sockets.TcpClient
        $Async = $Client.BeginConnect("127.0.0.1", $TestPort, $null, $null)
        $Ok = $Async.AsyncWaitHandle.WaitOne(700, $false)
        if ($Ok -and $Client.Connected) {
            $Client.EndConnect($Async)
            $Client.Close()
            return $true
        }
        $Client.Close()
        return $false
    } catch {
        return $false
    }
}

function Invoke-Api {
    param(
        [string]$Method,
        [string]$Path,
        [int]$TimeoutSec = 10
    )
    $Url = "http://$HostAddress`:$Port$Path"
    Write-AhootsaEvent "api.call.start" @{ method=$Method; url=$Url }
    try {
        if ($Method -eq "GET") {
            $Resp = Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec $TimeoutSec
        } else {
            $Resp = Invoke-RestMethod -Uri $Url -Method Post -TimeoutSec $TimeoutSec
        }
        Write-AhootsaEvent "api.call.ok" @{ method=$Method; url=$Url; response=($Resp | ConvertTo-Json -Depth 8 -Compress) }
        return $Resp
    } catch {
        Write-AhootsaEvent "api.call.error" @{ method=$Method; url=$Url; error=$_.Exception.Message }
        return $null
    }
}

# Entorno Ahootsa heredado por daemon y app.
$env:REACHY_MINI_CUSTOM_PROFILE = "ahootsa_realtime_es"
$env:REACHY_MINI_PROFILE = "ahootsa_realtime_es"
$env:REACHY_MINI_PERSONALITY = "ahootsa_realtime_es"
$env:REACHY_MINI_USER_PERSONALITY = "ahootsa_realtime_es"
$env:AHOOTSA_FORCE_DEFAULT_PROFILE = "1"
$env:AHOOTSA_RUNTIME_PROFILE_COPY = "1"
$env:AHOOTSA_NAME = "Ahootsa"
$env:ASSISTANT_NAME = "Ahootsa"
$env:ROBOT_NAME = "Ahootsa"
$env:PROJECT_NAME = "Ahootsa"
$env:AHOOTSA_LANGUAGE = "es"
$env:REACHY_MINI_LANGUAGE = "es"
$env:APP_LANGUAGE = "es"
$env:LANGUAGE = "es"
$env:OUTPUT_LANGUAGE = "es"
$env:SYSTEM_LANGUAGE = "es"
$env:REALTIME_TRANSCRIPTION_LANGUAGE = "es"
$env:TRANSCRIPTION_LANGUAGE = "es"
$env:AHOOTSA_VOICE = "Sohee"
$env:VOICE = "Sohee"
$env:REACHY_MINI_VOICE = "Sohee"
$env:OPENAI_REALTIME_VOICE = "Sohee"
$env:REALTIME_VOICE = "Sohee"
$env:TTS_VOICE = "Sohee"
$env:AUDIO_VOICE = "Sohee"
$env:OLLAMA_BASE_URL = "http://127.0.0.1:11434"
$env:OLLAMA_MODEL = "ahootsa-local:latest"
$env:AHOOTSA_OLLAMA_TIMEOUT_SECONDS = "45"
$env:SYSTEM_PROMPT_EXTRA = "Tu nombre es Ahootsa. No eres Reachy Mini. Habla siempre en castellano. ask_ollama es solo una actividad opcional de IA local."

Write-AhootsaEvent "launcher.start" @{
    root=$Root
    log_root=$LogRoot
    port=$Port
    app=$AppName
    voice=$env:AHOOTSA_VOICE
    profile=$env:REACHY_MINI_PROFILE
}

Write-Host ""
Write-Host "============================================================"
Write-Host "Ahootsa 5.0.34 - MuJoCo web backend realtime"
Write-Host "============================================================"
Write-Host "Root:    $Root"
Write-Host "Logs:    $LogRoot"
Write-Host "Pantalla:$env:AHOOTSA_LOG_FILE_SCREEN"
Write-Host "Eventos: $env:AHOOTSA_LOG_FILE_EVENTS"
Write-Host "Runtime: $env:AHOOTSA_LOG_FILE_RUNTIME"
Write-Host "Session: $Session"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Python = Join-Path $DesktopDir "apps_venv\Scripts\python.exe"
$Daemon = Join-Path $DesktopDir "apps_venv\Scripts\reachy-mini-daemon.exe"

Write-Host "Python:  $Python"
Write-Host "Daemon:  $Daemon"

if (-not (Test-Path -LiteralPath $Python)) {
    Write-Host "[ERROR] No encuentro Python de Reachy: $Python"
    Write-AhootsaEvent "launcher.error" @{ reason="python_missing"; path=$Python }
    try { Stop-Transcript | Out-Null } catch {}
    exit 1
}
if (-not (Test-Path -LiteralPath $Daemon)) {
    Write-Host "[ERROR] No encuentro daemon de Reachy: $Daemon"
    Write-AhootsaEvent "launcher.error" @{ reason="daemon_missing"; path=$Daemon }
    try { Stop-Transcript | Out-Null } catch {}
    exit 1
}

# Comprobacion de modulo Ahootsa.
$ImportCheck = & $Python -c "import ahootsa_realtime_ollama_desktop_app, pathlib; print('IMPORT_OK', pathlib.Path(ahootsa_realtime_ollama_desktop_app.__file__).resolve())" 2>&1
Write-Host $ImportCheck
Write-AhootsaEvent "module.import.check" @{ output=($ImportCheck -join "`n"); exit_code=$LASTEXITCODE }
if ($LASTEXITCODE -ne 0 -or (($ImportCheck -join "`n") -notmatch "IMPORT_OK")) {
    Write-Host "[ERROR] Ahootsa no es importable. Ejecuta primero INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1"
    try { Stop-Transcript | Out-Null } catch {}
    exit 1
}

# Comprobacion de MuJoCo.
$MujocoCheck = & $Python -c "import mujoco; print('MUJOCO_OK', mujoco.__version__)" 2>&1
Write-Host $MujocoCheck
Write-AhootsaEvent "mujoco.import.check" @{ output=($MujocoCheck -join "`n"); exit_code=$LASTEXITCODE }
if ($LASTEXITCODE -ne 0 -or (($MujocoCheck -join "`n") -notmatch "MUJOCO_OK")) {
    Write-Host "[ERROR] MuJoCo no esta instalado en apps_venv."
    try { Stop-Transcript | Out-Null } catch {}
    exit 1
}

if ($StopExistingApp) {
    $null = Invoke-Api "POST" "/api/apps/stop-current-app" 10
    Start-Sleep -Seconds 2
}

if (Test-PortOpen $Port) {
    Write-Host "[INFO] El puerto $Port ya esta abierto. Usare el daemon existente."
    Write-AhootsaEvent "daemon.already_running" @{ port=$Port }
} else {
    Write-Host "[INFO] Arrancando daemon MuJoCo..."
    $DaemonLog = $env:AHOOTSA_LOG_FILE_RUNTIME
    $TempRoot = Join-Path $Root ".tmp"
    if (-not (Test-Path -LiteralPath $TempRoot)) { New-Item -ItemType Directory -Force -Path $TempRoot | Out-Null }
    $TempScript = Join-Path $TempRoot ("start_daemon_mujoco_" + $Session + ".ps1")

    $HeadlessArg = ""
    if ($Headless) { $HeadlessArg = "--headless" }

    # PLANTILLA SEGURA: single-quoted here-string. No se expanden $variables al crear el script.
    $Template = @'
# start_daemon_mujoco.ps1 generado por Ahootsa 5.0.34
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$env:AHOOTSA_LOG_DIR = "__LOGROOT__"
$env:AHOOTSA_SESSION_ID = "__SESSION__"
$env:AHOOTSA_LOG_FILE_SCREEN = "__SCREENLOG__"
$env:AHOOTSA_LOG_FILE_EVENTS = "__EVENTLOG__"
$env:AHOOTSA_LOG_FILE_RUNTIME = "__RUNTIMELOG__"
$env:REACHY_MINI_CUSTOM_PROFILE = "ahootsa_realtime_es"
$env:REACHY_MINI_PROFILE = "ahootsa_realtime_es"
$env:REACHY_MINI_PERSONALITY = "ahootsa_realtime_es"
$env:REACHY_MINI_USER_PERSONALITY = "ahootsa_realtime_es"
$env:AHOOTSA_NAME = "Ahootsa"
$env:ASSISTANT_NAME = "Ahootsa"
$env:ROBOT_NAME = "Ahootsa"
$env:PROJECT_NAME = "Ahootsa"
$env:AHOOTSA_LANGUAGE = "es"
$env:REACHY_MINI_LANGUAGE = "es"
$env:AHOOTSA_VOICE = "Sohee"
$env:VOICE = "Sohee"
$env:REACHY_MINI_VOICE = "Sohee"
$env:OPENAI_REALTIME_VOICE = "Sohee"
$env:REALTIME_VOICE = "Sohee"
$env:TTS_VOICE = "Sohee"
$env:AUDIO_VOICE = "Sohee"
$env:OLLAMA_BASE_URL = "http://127.0.0.1:11434"
$env:OLLAMA_MODEL = "ahootsa-local:latest"

$Daemon = "__DAEMON__"
$DaemonLog = "__DAEMONLOG__"
$DaemonTranscriptLog = "__DAEMONTRANSCRIPTLOG__"
$Port = __PORT__
$HostAddress = "__HOST__"
$HeadlessArg = "__HEADLESS__"

"START_DAEMON $(Get-Date -Format o)" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
"Daemon=$Daemon" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
"Port=$Port" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
"LogRoot=$env:AHOOTSA_LOG_DIR" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
"Voice=$env:AHOOTSA_VOICE" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
$ArgsList = @(
    "--sim",
    "--fastapi-host", $HostAddress,
    "--fastapi-port", "$Port",
    "--no-goto-sleep-on-stop",
    "--dataset-update-interval", "0",
    "--no-preload-datasets",
    "--log-file", $DaemonLog
)

if ($HeadlessArg -eq "--headless") {
    $ArgsList += "--headless"
}

"ARGS=$($ArgsList -join ' ')" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
try {
    # No usamos redireccion de stderr/stdout con & porque PowerShell 5 lo muestra como NativeCommandError.
    # El propio daemon escribe su log en --log-file=$DaemonLog.
    $Proc = Start-Process -FilePath $Daemon -ArgumentList $ArgsList -NoNewWindow -PassThru
    "DAEMON_PROCESS_STARTED pid=$($Proc.Id) $(Get-Date -Format o)" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
    $Proc.WaitForExit()
    "DAEMON_EXIT_CODE=$($Proc.ExitCode) $(Get-Date -Format o)" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
} catch {
    "DAEMON_EXCEPTION=$($_.Exception.Message) $(Get-Date -Format o)" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
}
'@

    $ScriptText = $Template.
        Replace("__LOGROOT__", $LogRoot).
        Replace("__SESSION__", $Session).
        Replace("__DAEMON__", $Daemon).
        Replace("__DAEMONLOG__", $DaemonLog).
        Replace("__DAEMONCONSOLELOG__", (Join-Path $LogRoot ("ahootsa_5_mujoco_daemon_console_" + $Session + ".log"))).
        Replace("__DAEMONERRORLOG__", (Join-Path $LogRoot ("ahootsa_5_mujoco_daemon_stderr_" + $Session + ".log"))).
        Replace("__DAEMONTRANSCRIPTLOG__", (Join-Path $LogRoot ("ahootsa_5_mujoco_daemon_transcript_" + $Session + ".log"))).
        Replace("__PORT__", [string]$Port).
        Replace("__HOST__", $HostAddress).
        Replace("__HEADLESS__", $HeadlessArg)

    $ScriptText | Set-Content -Encoding UTF8 -LiteralPath $TempScript

    Write-Host "Temp daemon script: $TempScript"
    Write-Host "Daemon log:         $DaemonLog"
    Write-AhootsaEvent "daemon.temp_script.created" @{ path=$TempScript; log=$DaemonLog }

    Start-Process powershell -ArgumentList @("-ExecutionPolicy", "Bypass", "-NoExit", "-File", $TempScript) -WindowStyle Normal

    $Ready = $false
    for ($i = 1; $i -le 45; $i++) {
        Start-Sleep -Seconds 1
        if (Test-PortOpen $Port) {
            $Status = Invoke-Api "GET" "/api/daemon/status" 3
            if ($Status) {
                $Ready = $true
                break
            }
        }
        Write-Host "Esperando daemon... $i"
    }

    if (-not $Ready) {
        Write-Host "[ERROR] El daemon no quedo listo."
        Write-AhootsaEvent "daemon.ready.timeout" @{ port=$Port }
        try { Stop-Transcript | Out-Null } catch {}
        exit 1
    }
}

Write-Host "[OK] Daemon disponible en http://$HostAddress`:$Port"
Write-AhootsaEvent "daemon.ready" @{ url="http://$HostAddress`:$Port" }

if (-not $NoOpenBrowser) {
    Start-Process "http://$HostAddress`:$Port"
    Start-Process "http://$HostAddress`:$Port/docs"
}

if (-not $NoStartApp) {
    Write-Host "[INFO] Arrancando app Ahootsa..."
    Write-AhootsaEvent "app.start.request" @{ app=$AppName }
    $Resp = Invoke-Api "POST" "/api/apps/start-app/$AppName" 20
    Start-Sleep -Seconds 7

    Write-Host "[INFO] Esperando a que Ahootsa exponga /status..."
    for ($i = 1; $i -le 75; $i++) {
        try {
            $StatusProbe = Invoke-WebRequest -Uri "http://127.0.0.1:7860/status" -Method Get -TimeoutSec 3 -UseBasicParsing
            Write-AhootsaEvent "app.7860.status_ready" @{ iteration=$i; status=$StatusProbe.StatusCode }
            break
        } catch {
            Write-AhootsaEvent "app.7860.wait_status" @{ iteration=$i; error=$_.Exception.Message }
            Start-Sleep -Seconds 1
        }
    }

    Write-Host "[INFO] Voz Sohee simple: voice.txt sin BOM + aplicar una vez si la API esta lista..."
    $VoiceScript = Join-Path $Root "FORZAR_5_VOZ_SOHEE_COMPLETA.ps1"
    if (Test-Path -LiteralPath $VoiceScript) {
        powershell -ExecutionPolicy Bypass -File $VoiceScript -WaitSeconds 20
    }

    Write-Host "[INFO] Esperando backend realtime antes de hablar..."
    $WaitBackendScript = Join-Path $Root "ESPERAR_5_BACKEND_REALTIME_LISTO.ps1"
    if (Test-Path -LiteralPath $WaitBackendScript) {
        powershell -ExecutionPolicy Bypass -File $WaitBackendScript -TimeoutSeconds 120 -IntervalSeconds 3
    }

    if (-not $NoOpenBrowser) {
        Write-Host "[INFO] Abriendo interfaz..."
        Start-Process "http://127.0.0.1:7860"
    }

    Write-Host "[OK] Interfaz: http://127.0.0.1:7860"
    Write-Host "[INFO] Espera a que /status indique backend_connected=true antes de hablar."
}

Write-AhootsaEvent "launcher.end" @{ ok=$true }
try { Stop-Transcript | Out-Null } catch {}
