param(
    [string]$Provider = "ollama",
    [string]$OllamaModel = "llama3.2:3b",
    [string]$HFModelPath = "",
    [int]$DaemonPort = 8000,
    [int]$AppPort = 7860,
    [string]$Voice = "Sohee",
    [int]$OllamaTimeout = 25,
    [string]$OpenBrowser = "SI",
    [string]$InstallMujoco = "NO",
    [string]$InstallHFDeps = "NO"
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogRoot = "D:\RITXI\logs"
$CameraDir = Join-Path $LogRoot "camera"
New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
New-Item -ItemType Directory -Force -Path $CameraDir | Out-Null
$Session = Get-Date -Format "yyyyMMdd_HHmmss"
$PantallaLog = Join-Path $LogRoot "ahootsa5_${Session}_pantalla.log"
$RuntimeLog = Join-Path $LogRoot "ahootsa5_${Session}_runtime.log"
$EventosLog = Join-Path $LogRoot "ahootsa5_${Session}_eventos.jsonl"
$InfoFile = Join-Path $LogRoot "ULTIMA_EJECUCION_AHOOTSA_INFO.txt"
"session=$Session`nroot=$Root`npantalla=$PantallaLog`nruntime=$RuntimeLog`neventos=$EventosLog" | Set-Content -Encoding UTF8 -LiteralPath $InfoFile

function LogLine([string]$s) {
    Write-Host $s
    try { Add-Content -LiteralPath $PantallaLog -Encoding UTF8 -Value $s } catch { }
}
function Event([string]$name, $data=@{}) {
    try {
        $obj = [ordered]@{ ts=(Get-Date).ToString("o"); event=$name; session_id=$Session; data=$data }
        ($obj | ConvertTo-Json -Compress -Depth 8) | Add-Content -LiteralPath $EventosLog -Encoding UTF8
    } catch { }
}
function Invoke-Api($Method, $Url, $Body=$null, [int]$TimeoutSec=8) {
    Event "api.call.start" @{ method=$Method; url=$Url }
    if ($Body -ne $null) {
        $json = $Body | ConvertTo-Json -Compress -Depth 8
        $res = Invoke-RestMethod -Method $Method -Uri $Url -Body $json -ContentType "application/json" -TimeoutSec $TimeoutSec
    } else {
        $res = Invoke-RestMethod -Method $Method -Uri $Url -TimeoutSec $TimeoutSec
    }
    Event "api.call.ok" @{ method=$Method; url=$Url }
    return $res
}

Start-Transcript -LiteralPath $PantallaLog -Append | Out-Null
try {
    LogLine "============================================================"
    LogLine "Ahootsa 5.0.42 - version autonoma estable"
    LogLine "============================================================"
    LogLine "Root:       $Root"
    LogLine "Session:    $Session"
    LogLine "Provider:   $Provider"
    LogLine "OllamaModel:$OllamaModel"
    LogLine "Logs:       $LogRoot"
    LogLine "CameraDir:  $CameraDir"

    $Py = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv\Scripts\python.exe"
    $Daemon = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv\Scripts\reachy-mini-daemon.exe"
    if (!(Test-Path $Py)) { throw "No existe Python apps_venv: $Py" }
    if (!(Test-Path $Daemon)) { throw "No existe reachy-mini-daemon: $Daemon" }
    LogLine "Python:     $Py"
    LogLine "Daemon:     $Daemon"

    if ($InstallMujoco.ToUpperInvariant() -eq "SI") {
        LogLine "[INFO] Instalando/actualizando mujoco en apps_venv..."
        & $Py -m pip install -U mujoco | Tee-Object -FilePath $RuntimeLog -Append
    }
    $mujocoOut = & $Py -c "import mujoco; print('MUJOCO_OK', mujoco.__version__)" 2>&1
    if ($LASTEXITCODE -ne 0) { throw "MuJoCo no esta instalado en apps_venv. Ejecuta con -InstallMujoco SI. Detalle: $mujocoOut" }
    LogLine $mujocoOut

    if ($InstallHFDeps.ToUpperInvariant() -eq "SI") {
        LogLine "[INFO] Instalando dependencias HF basicas..."
        & $Py -m pip install -U transformers accelerate sentencepiece safetensors | Tee-Object -FilePath $RuntimeLog -Append
    }

    $env:AHOOTSA_VERSION = "5.0.42"
    $env:AHOOTSA_LOG_ROOT = $LogRoot
    $env:AHOOTSA_CAMERA_DIR = $CameraDir
    $env:AHOOTSA_LLM_PROVIDER = $Provider
    $env:AHOOTSA_OLLAMA_MODEL = $OllamaModel
    $env:AHOOTSA_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
    $env:AHOOTSA_OLLAMA_TIMEOUT = [string]$OllamaTimeout
    $env:AHOOTSA_OLLAMA_NUM_PREDICT = "120"
    $env:AHOOTSA_OLLAMA_TEMPERATURE = "0.45"
    $env:AHOOTSA_HF_MODEL_PATH = $HFModelPath
    $env:AHOOTSA_VOICE = $Voice
    $env:VOICE = $Voice
    $env:REACHY_MINI_VOICE = $Voice
    $env:OPENAI_REALTIME_VOICE = $Voice
    $env:REALTIME_VOICE = $Voice
    $env:TTS_VOICE = $Voice
    $env:AUDIO_VOICE = $Voice

    if ($Provider.ToLowerInvariant() -eq "ollama") {
        try {
            $tags = Invoke-RestMethod -Method GET -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 4
            $names = @($tags.models | ForEach-Object { $_.name })
            LogLine "[INFO] Modelos Ollama: $($names -join ', ')"
            if ($names -notcontains $OllamaModel) {
                LogLine "[WARN] El modelo $OllamaModel no aparece en ollama list. Modelos disponibles: $($names -join ', ')"
            }
        } catch {
            LogLine "[WARN] Ollama no responde en 127.0.0.1:11434. Abre Ollama o ejecuta: ollama serve"
        }
    }

    LogLine "[INFO] Aplicando parche autónomo 5.0.42 al paquete instalado..."
    $Patch = Join-Path $Root "tools\patch_ahootsa_5_0_42.py"
    & $Py $Patch 2>&1 | Tee-Object -FilePath $RuntimeLog -Append
    if ($LASTEXITCODE -ne 0) { throw "No se pudo aplicar el parche 5.0.42." }

    # Arranque daemon en proceso aparte.
    $Tmp = Join-Path $Root ".tmp"
    New-Item -ItemType Directory -Force -Path $Tmp | Out-Null
    $DaemonScript = Join-Path $Tmp "start_daemon_5_0_42_$Session.ps1"
    @"
`$env:AHOOTSA_VERSION = '5.0.42'
`$env:AHOOTSA_LOG_ROOT = '$LogRoot'
`$env:AHOOTSA_CAMERA_DIR = '$CameraDir'
`$env:AHOOTSA_LLM_PROVIDER = '$Provider'
`$env:AHOOTSA_OLLAMA_MODEL = '$OllamaModel'
`$env:AHOOTSA_OLLAMA_BASE_URL = 'http://127.0.0.1:11434'
`$env:AHOOTSA_OLLAMA_TIMEOUT = '$OllamaTimeout'
`$env:AHOOTSA_HF_MODEL_PATH = '$HFModelPath'
`$env:AHOOTSA_VOICE = '$Voice'
Add-Content -Encoding UTF8 -LiteralPath '$RuntimeLog' -Value ('START_DAEMON ' + (Get-Date -Format o))
& '$Daemon' --sim --fastapi-host 127.0.0.1 --fastapi-port $DaemonPort --no-goto-sleep-on-stop --dataset-update-interval 0 --no-preload-datasets --log-file '$RuntimeLog'
"@ | Set-Content -Encoding UTF8 -LiteralPath $DaemonScript

    LogLine "[INFO] Arrancando daemon en puerto $DaemonPort..."
    Start-Process powershell -ArgumentList @('-ExecutionPolicy','Bypass','-File',$DaemonScript) -WindowStyle Minimized | Out-Null
    $ready = $false
    for ($i=1; $i -le 30; $i++) {
        Start-Sleep -Seconds 2
        try {
            $st = Invoke-RestMethod -Method GET -Uri "http://127.0.0.1:$DaemonPort/api/daemon/status" -TimeoutSec 3
            if ($st.state) { $ready = $true; break }
        } catch { }
        LogLine "Esperando daemon... $i"
    }
    if (-not $ready) { throw "Daemon no disponible en http://127.0.0.1:$DaemonPort" }
    LogLine "[OK] Daemon disponible en http://127.0.0.1:$DaemonPort"

    LogLine "[INFO] Arrancando app ahootsa_realtime_ollama_app..."
    try { Invoke-Api POST "http://127.0.0.1:$DaemonPort/api/apps/start-app/ahootsa_realtime_ollama_app" @{} 10 | Out-Null } catch { LogLine "[WARN] start-app devolvio: $($_.Exception.Message)" }

    $appReady = $false
    for ($i=1; $i -le 35; $i++) {
        Start-Sleep -Seconds 2
        try {
            $r = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$AppPort/status" -TimeoutSec 3
            if ($r.StatusCode -eq 200) { $appReady = $true; break }
        } catch { }
        LogLine "Esperando app 7860/status... $i"
    }
    if (-not $appReady) { throw "Ahootsa no responde en http://127.0.0.1:$AppPort/status" }
    LogLine "[OK] Interfaz: http://127.0.0.1:$AppPort"
    LogLine "[OK] Cámara PC: http://127.0.0.1:$AppPort/camera/page"
    LogLine "[OK] Ollama status: http://127.0.0.1:$AppPort/ollama/status"
    Event "launcher.end" @{ ok=$true; url="http://127.0.0.1:$AppPort" }
    if ($OpenBrowser.ToUpperInvariant() -eq "SI") { Start-Process "http://127.0.0.1:$AppPort" }
    LogLine "[INFO] Prueba ahora el panel flotante Ahootsa 5.0.42 o abre /camera/page."
} catch {
    Event "launcher.error" @{ error=$_.Exception.Message }
    LogLine "[ERROR] $($_.Exception.Message)"
    throw
} finally {
    try { Stop-Transcript | Out-Null } catch { }
}
