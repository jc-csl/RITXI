$ErrorActionPreference = "Continue"
Set-Location -LiteralPath $PSScriptRoot

$Logs = Join-Path $PSScriptRoot "logs"
New-Item -ItemType Directory -Force -Path $Logs | Out-Null

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$FastOutLog = Join-Path $Logs "ritxi_fastapi_$Stamp.out.log"
$FastErrLog = Join-Path $Logs "ritxi_fastapi_$Stamp.err.log"
$CurrentFastOut = Join-Path $Logs "ritxi_fastapi_current.out.log"
$CurrentFastErr = Join-Path $Logs "ritxi_fastapi_current.err.log"
$LauncherLog = Join-Path $Logs "lanzador_$Stamp.log"
$Url = "http://127.0.0.1:8080"

function Log($msg) {
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"
    Write-Host $line
    $line | Add-Content -Path $LauncherLog -Encoding utf8
}

function Test-Port($port) {
    try {
        $client = New-Object Net.Sockets.TcpClient
        $iar = $client.BeginConnect("127.0.0.1", $port, $null, $null)
        $ok = $iar.AsyncWaitHandle.WaitOne(700, $false)
        if (-not $ok) { $client.Close(); return $false }
        $client.EndConnect($iar)
        $client.Close()
        return $true
    } catch { return $false }
}

function Get-PortPids($port) {
    $pids = @()
    try {
        $lines = netstat -ano | Select-String "LISTENING" | Select-String ":$port"
        foreach ($line in $lines) {
            $parts = ($line.ToString() -split "\s+") | Where-Object { $_ -ne "" }
            if ($parts.Count -ge 5) {
                $pidText = $parts[-1]
                $pidValue = 0
                if ([int]::TryParse($pidText, [ref]$pidValue)) {
                    if ($pidValue -gt 0) { $pids += $pidValue }
                }
            }
        }
    } catch {}
    return $pids | Sort-Object -Unique
}

function Kill-Port($port) {
    $pids = Get-PortPids $port
    foreach ($pidValue in $pids) {
        try {
            $proc = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
            if ($null -ne $proc) {
                Log "Puerto $port ocupado por PID $pidValue ($($proc.ProcessName)). Cerrando..."
                Stop-Process -Id $pidValue -Force -ErrorAction SilentlyContinue
            }
        } catch {}
    }
}

function Wait-Port($port, $seconds, $name) {
    for ($i=1; $i -le $seconds; $i++) {
        if (Test-Port $port) { return $true }
        if (($i % 5) -eq 0) { Log "esperando $name... $i/$seconds s" }
        Start-Sleep -Seconds 1
    }
    return $false
}

Write-Host "============================================================"
Write-Host " 3 - RUN RITXI"
Write-Host "============================================================"
Write-Host "URL: $Url"
Write-Host "Log FastAPI OUT: $FastOutLog"
Write-Host "Log FastAPI ERR: $FastErrLog"
Write-Host ""

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Lanzador iniciado desde $PSScriptRoot" | Out-File -FilePath $LauncherLog -Encoding utf8 -Force

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Log "[ERROR] No existe .venv\Scripts\python.exe. Ejecuta primero 1_INSTALAR_RITXI.cmd"
    Read-Host "Pulsa ENTER para cerrar"
    exit 1
}

if (-not (Test-Port 8000)) {
    Log "[ERROR] El daemon Reachy no responde en 127.0.0.1:8000."
    Log "Abre primero otra ventana con: 2_INICIAR_DAEMON_RITXI.cmd"
    Read-Host "Pulsa ENTER para cerrar"
    exit 1
}

Log "[OK] Daemon Reachy disponible en 127.0.0.1:8000"

if (Test-Port 8080) {
    Log "[AVISO] Ya hay algo escuchando en 8080. Se cerrara para arrancar esta version limpia."
    Kill-Port 8080
    Start-Sleep -Seconds 2
}

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] FastAPI STDOUT iniciado" | Out-File -FilePath $FastOutLog -Encoding utf8 -Force
"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] FastAPI STDERR iniciado" | Out-File -FilePath $FastErrLog -Encoding utf8 -Force
Copy-Item -LiteralPath $FastOutLog -Destination $CurrentFastOut -Force -ErrorAction SilentlyContinue
Copy-Item -LiteralPath $FastErrLog -Destination $CurrentFastErr -Force -ErrorAction SilentlyContinue

# Variables correctas: si se arranca manualmente con uvicorn no se aplican.
$env:RITXI_MODE="reachy_daemon"
$env:RITXI_ROBOT_HOST="127.0.0.1"
$env:RITXI_LLM_PROVIDER="ollama"
$env:RITXI_OLLAMA_URL="http://127.0.0.1:11434"
$env:RITXI_OLLAMA_MODEL="gemma3:1b"
$env:RITXI_LLM_STREAMING_ENABLED="true"
$env:RITXI_LLM_MAX_TOKENS="40"
$env:RITXI_LLM_TIMEOUT_S=60
$env:RITXI_OLLAMA_NUM_CTX="640"
$env:RITXI_OLLAMA_TOP_K="20"
$env:RITXI_OLLAMA_TOP_P="0.85"
$env:RITXI_OLLAMA_REPEAT_PENALTY="1.15"
$env:RITXI_TTS_PROVIDER="browser"
$env:RITXI_USE_OUTPUT_AUDIO_DEFAULT="true"
$env:RITXI_USE_INPUT_MICROPHONE_DEFAULT="true"
$env:RITXI_USE_ROBOT_MOTION_DEFAULT="true"
$env:RITXI_IDLE_ENABLED_DEFAULT="false"
$env:RITXI_PLAY_RECORDED_AUDIO_DEFAULT="false"
$env:RITXI_WHISPER_COMPUTE_TYPE="int8"
$env:RITXI_WHISPER_MODEL="tiny"
$env:RITXI_STT_WHISPER_MODEL_SIZE="tiny"
$env:RITXI_RELISTEN_DELAY_MS="450"
$env:RITXI_SILENCE_SEND_MS="850"
$env:RITXI_SERVER_VAD_THRESHOLD="0.028"
$env:RITXI_SERVER_RECORD_MAX_MS="3500"
$env:RITXI_STT_PROVIDER="local_whisper"

$Python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

Log "[Ritxi] Arrancando FastAPI con entorno correcto: reachy_daemon + ollama + browser TTS"
$p = Start-Process `
    -FilePath $Python `
    -ArgumentList @("-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8080") `
    -WorkingDirectory $PSScriptRoot `
    -RedirectStandardOutput $FastOutLog `
    -RedirectStandardError $FastErrLog `
    -PassThru `
    -WindowStyle Hidden

Log "[Ritxi] FastAPI PID: $($p.Id)"
Log "[Ritxi] Esperando hasta 90 segundos a 127.0.0.1:8080..."

if (-not (Wait-Port 8080 90 "FastAPI")) {
    Log "[ERROR] FastAPI no ha abierto el puerto 8080."
    Log "STDOUT:"
    if (Test-Path $FastOutLog) { Get-Content $FastOutLog -Tail 80 }
    Log "STDERR:"
    if (Test-Path $FastErrLog) { Get-Content $FastErrLog -Tail 120 }
    Read-Host "Pulsa ENTER para cerrar"
    exit 1
}

Log "[OK] FastAPI disponible en $Url"
Log "[Ritxi] Esperando 10 segundos antes de abrir navegador..."
Start-Sleep -Seconds 10
Start-Process $Url

Log "[OK] Navegador abierto: $Url"
Write-Host ""
Write-Host "Deja abierta la ventana del daemon."
Write-Host "FastAPI queda en segundo plano."
Write-Host ""
Write-Host "Logs:"
Write-Host "  $LauncherLog"
Write-Host "  $FastOutLog"
Write-Host "  $FastErrLog"
Write-Host ""
Write-Host "Para cerrar todo usa: 4_SALIR_RITXI.cmd"
Read-Host "Pulsa ENTER para cerrar esta ventana"
