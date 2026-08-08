param(
    [ValidateSet("verify","test","full","qwen","speech","mujoco","app")]
    [string]$Mode = "full"
)

$ErrorActionPreference = "Stop"

$Root = "D:\RITXI\AHOOTSA_LOCAL"
$ReachyDir = Join-Path $Root "reachy_mini_conversation_app"
$SpeechDir = Join-Path $Root "speech_engine"

$ReachyActivate = Join-Path $ReachyDir ".venv\Scripts\Activate.ps1"
$SpeechActivate = Join-Path $SpeechDir ".venv\Scripts\Activate.ps1"
$PidFile = Join-Path $Root ".ahootsa_local_v8_pids.json"

# v8: Qwen3 4B Q4. Aproximadamente 2.5 GB de GGUF.
$LlmRepo = "ggml-org/Qwen3-4B-GGUF"
$LlmSpec = "ggml-org/Qwen3-4B-GGUF:Q4_K_M"

# Una sola linea, sin comillas internas, para Windows PowerShell 5.1.
$PromptAocha = "Eres Aocha, un asistente conversacional. Sigue exactamente la ultima peticion del usuario usando el contexto anterior. No devuelvas una pregunta si puedes ejecutar directamente lo pedido. Si el usuario te deja elegir, elige tu y continua. No repitas respuestas anteriores. Si cambia de tema, sigue el nuevo tema. Habla en espanol salvo que pida otro idioma. Responde de forma breve, natural y correcta."

function Test-Port([int]$Port) {
    $c = New-Object System.Net.Sockets.TcpClient
    try {
        $r = $c.BeginConnect("127.0.0.1", $Port, $null, $null)
        if (-not $r.AsyncWaitHandle.WaitOne(500, $false)) { return $false }
        $c.EndConnect($r)
        return $true
    } catch {
        return $false
    } finally {
        $c.Close()
    }
}

function Wait-Port([int]$Port, [int]$Seconds, [string]$Name) {
    Write-Host "Esperando $Name en puerto $Port..." -ForegroundColor Yellow
    for ($i = 0; $i -lt $Seconds; $i++) {
        if (Test-Port $Port) {
            Write-Host "OK - $Name disponible." -ForegroundColor Green
            return
        }
        Start-Sleep -Seconds 1
    }
    throw "Timeout esperando $Name en puerto $Port."
}

function Wait-Qwen {
    Write-Host "Esperando Qwen /health..." -ForegroundColor Yellow
    for ($i = 0; $i -lt 600; $i++) {
        try {
            $h = Invoke-RestMethod -Uri "http://127.0.0.1:8080/health" -TimeoutSec 2
            if ($h) {
                Write-Host "OK - Qwen preparado." -ForegroundColor Green
                return
            }
        } catch {}
        Start-Sleep -Seconds 1
    }
    throw "Qwen no ha quedado preparado en 10 minutos."
}

function Start-Self([string]$ChildMode) {
    return Start-Process powershell.exe -PassThru -ArgumentList @(
        "-NoExit",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", $PSCommandPath,
        "-Mode", $ChildMode
    )
}

function Get-SpeechCommonArgs([string]$Command) {
    return @(
        $Command,

        "--stt", "parakeet-tdt",
        "--parakeet_tdt_device", "cpu",
        "--parakeet_tdt_language", "es",

        "--llm_backend", "responses-api",
        "--model_name", $LlmRepo,
        "--user_role", "user",
        "--init_chat_role", "system",
        "--init_chat_prompt", $PromptAocha,
        "--chat_size", "10",

        "--responses_api_base_url", "http://127.0.0.1:8080/v1",
        "--responses_api_api_key", "local",
        "--responses_api_disable_thinking",

        "--tts", "kokoro",
        "--kokoro_device", "cpu",
        "--kokoro_lang_code", "e",
        "--kokoro_voice", "ef_dora",

        # Conversacion estable antes que latencia extrema.
        "--no_enable_live_transcription",
        "--no_smart_turn",
        "--thresh", "0.70",
        "--min_speech_ms", "384",
        "--min_speech_continuation_ms", "384",
        "--min_silence_ms", "600",
        "--speculative_reopen_ms", "0",
        "--unanswered_reopen_ms", "0",

        "--stream_batch_sentences", "1"
    )
}

# ============================================================
# QWEN 4B
# ============================================================
if ($Mode -eq "qwen") {
    $Host.UI.RawUI.WindowTitle = "AHOOTSA v8 - QWEN3 4B"

    Write-Host ""
    Write-Host "AHOOTSA v8 - QWEN3 4B Q4" -ForegroundColor Cyan
    Write-Host "Primera ejecucion: descargara aproximadamente 2.5 GB." -ForegroundColor Yellow
    Write-Host ""

    llama serve `
        -hf $LlmSpec `
        -np 1 `
        -c 4096 `
        --reasoning off `
        --host 127.0.0.1 `
        --port 8080

    exit
}

# ============================================================
# SPEECH SERVE PARA REACHY
# ============================================================
if ($Mode -eq "speech") {
    $Host.UI.RawUI.WindowTitle = "AHOOTSA v8 - SPEECH SERVE"

    Set-Location $SpeechDir
    . $SpeechActivate

    Write-Host ""
    Write-Host "AHOOTSA v8 - SPEECH SERVE" -ForegroundColor Cyan
    Write-Host "VENV: $env:VIRTUAL_ENV" -ForegroundColor DarkGray
    Write-Host "LLM: $LlmRepo" -ForegroundColor DarkGray

    $SpeechArgs = Get-SpeechCommonArgs "serve"
    $SpeechArgs += @("--port", "8765")

    & speech-to-speech @SpeechArgs
    exit
}

# ============================================================
# MUJOCO
# ============================================================
if ($Mode -eq "mujoco") {
    $Host.UI.RawUI.WindowTitle = "AHOOTSA v8 - REACHY MUJOCO"

    Set-Location $ReachyDir
    . $ReachyActivate

    Write-Host ""
    Write-Host "AHOOTSA v8 - REACHY + MUJOCO" -ForegroundColor Cyan
    Write-Host "VENV: $env:VIRTUAL_ENV" -ForegroundColor DarkGray

    python -c "import mujoco; print('MuJoCo:', mujoco.__version__)"
    reachy-mini-daemon --sim --scene minimal
    exit
}

# ============================================================
# CONVERSATION APP
# ============================================================
if ($Mode -eq "app") {
    $Host.UI.RawUI.WindowTitle = "AHOOTSA v8 - CONVERSATION APP"

    Set-Location $ReachyDir
    . $ReachyActivate

    Write-Host ""
    Write-Host "AHOOTSA v8 - CONVERSATION APP" -ForegroundColor Cyan
    Write-Host "VENV: $env:VIRTUAL_ENV" -ForegroundColor DarkGray

    $env:HF_REALTIME_CONNECTION_MODE = "local"
    $env:HF_REALTIME_WS_URL = "ws://127.0.0.1:8765/v1/realtime"
    $env:REALTIME_TRANSCRIPTION_LANGUAGE = "es"

    reachy-mini-conversation-app --ui --no-camera
    exit
}

# ============================================================
# VERIFY
# ============================================================
if ($Mode -eq "verify") {
    Write-Host ""
    Write-Host "AHOOTSA LOCAL v8 - VERIFICACION" -ForegroundColor Cyan

    if (-not (Get-Command llama -ErrorAction SilentlyContinue)) {
        throw "No se encuentra llama."
    }
    if (-not (Test-Path $SpeechActivate)) {
        throw "No existe speech_engine\.venv."
    }
    if (-not (Test-Path $ReachyActivate)) {
        throw "No existe reachy_mini_conversation_app\.venv."
    }

    llama --version

    Set-Location $SpeechDir
    . $SpeechActivate
    Write-Host "Speech VENV: $env:VIRTUAL_ENV"
    python --version
    python -c "import importlib.metadata as m; print('speech-to-speech:', m.version('speech-to-speech')); import hf_xet; print('hf_xet OK')"
    deactivate

    Set-Location $ReachyDir
    . $ReachyActivate
    Write-Host "Reachy VENV: $env:VIRTUAL_ENV"
    python --version
    python -c "import importlib.metadata as m; print('reachy-mini:', m.version('reachy-mini')); import mujoco; print('mujoco:', mujoco.__version__)"
    deactivate

    Write-Host ""
    Write-Host "Modelo v8: $LlmSpec" -ForegroundColor Green
    Write-Host "VERIFICACION OK" -ForegroundColor Green
    exit
}

# ============================================================
# TEST - SOLO PC
# ============================================================
if ($Mode -eq "test") {
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host " AHOOTSA LOCAL v8 - PRUEBA QWEN3 4B" -ForegroundColor Cyan
    Write-Host "========================================================" -ForegroundColor Cyan

    if (-not (Get-Command llama -ErrorAction SilentlyContinue)) {
        throw "No se encuentra llama."
    }
    if (-not (Test-Path $SpeechActivate)) {
        throw "No existe $SpeechActivate"
    }

    if (Test-Port 8080) {
        Write-Host ""
        Write-Host "ATENCION: ya hay un modelo en el puerto 8080." -ForegroundColor Yellow
        Write-Host "Para asegurar que pruebas Qwen3 4B, cierra primero la ventana Qwen anterior con Ctrl+C." -ForegroundColor Yellow
        Write-Host "Despues vuelve a ejecutar este script." -ForegroundColor Yellow
        exit 2
    }

    Write-Host "[1/2] Arrancando Qwen3 4B..." -ForegroundColor Cyan
    Start-Self "qwen" | Out-Null
    Wait-Qwen

    Write-Host "[2/2] Activando speech_engine\.venv..." -ForegroundColor Cyan
    Set-Location $SpeechDir
    . $SpeechActivate

    Write-Host "VENV activo: $env:VIRTUAL_ENV" -ForegroundColor DarkGray

    $LocalArgs = Get-SpeechCommonArgs "local"
    $LocalArgs += @("--local_audio_block_mic_during_playback")

    Write-Host ""
    Write-Host "Prueba concreta:" -ForegroundColor Yellow
    Write-Host "1. Hola, me llamo Pepe. Como te llamas?"
    Write-Host "   ESPERA a que Aocha termine de responder."
    Write-Host "2. Ensename dos palabras en ingles."
    Write-Host "3. Sabes un chiste?"
    Write-Host "4. El que tu quieras."
    Write-Host "5. De que hablabamos antes del chiste?"
    Write-Host ""
    Write-Host "No hables de nuevo hasta que termine el audio de Aocha." -ForegroundColor Yellow
    Write-Host ""

    & speech-to-speech @LocalArgs
    exit
}

# ============================================================
# FULL
# ============================================================
if ($Mode -eq "full") {
    Write-Host ""
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host " AHOOTSA LOCAL v8 - REACHY + MUJOCO COMPLETO" -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Cyan

    if (-not (Get-Command llama -ErrorAction SilentlyContinue)) {
        throw "No se encuentra llama."
    }
    if (-not (Test-Path $SpeechActivate)) {
        throw "No existe $SpeechActivate"
    }
    if (-not (Test-Path $ReachyActivate)) {
        throw "No existe $ReachyActivate"
    }

    foreach ($p in @(8765,8000,7860)) {
        if (Test-Port $p) {
            throw "El puerto $p ya esta ocupado. Cierra la ejecucion anterior."
        }
    }

    $Pids = [ordered]@{}

    if (-not (Test-Port 8080)) {
        Write-Host "[1/4] Arrancando Qwen3 4B..." -ForegroundColor Cyan
        $proc = Start-Self "qwen"
        $Pids["qwen"] = $proc.Id
    } else {
        Write-Host "[1/4] Hay un LLM activo en 8080. Se reutiliza." -ForegroundColor Yellow
        Write-Host "Asegurate de que es Qwen3 4B, no el antiguo 1.7B." -ForegroundColor Yellow
    }

    Wait-Qwen

    Write-Host "[2/4] Arrancando speech-to-speech serve..." -ForegroundColor Cyan
    $proc = Start-Self "speech"
    $Pids["speech"] = $proc.Id
    Wait-Port 8765 300 "speech-to-speech"

    Write-Host "[3/4] Arrancando Reachy Mini + MuJoCo..." -ForegroundColor Cyan
    $proc = Start-Self "mujoco"
    $Pids["mujoco"] = $proc.Id
    Wait-Port 8000 120 "Reachy daemon"

    Write-Host "[4/4] Arrancando Conversation App..." -ForegroundColor Cyan
    $proc = Start-Self "app"
    $Pids["app"] = $proc.Id
    Wait-Port 7860 120 "Conversation App"

    $Pids | ConvertTo-Json | Set-Content -Path $PidFile -Encoding UTF8
    Start-Process "http://127.0.0.1:7860/"

    Write-Host ""
    Write-Host "AHOOTSA LOCAL v8 ARRANCADO" -ForegroundColor Green
    Write-Host "LLM        $LlmRepo"
    Write-Host "Qwen       http://127.0.0.1:8080"
    Write-Host "Realtime   ws://127.0.0.1:8765/v1/realtime"
    Write-Host "Reachy     http://127.0.0.1:8000"
    Write-Host "App        http://127.0.0.1:7860"
}
