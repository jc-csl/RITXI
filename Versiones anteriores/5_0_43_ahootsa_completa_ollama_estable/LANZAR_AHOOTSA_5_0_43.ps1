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
"session=$Session`nroot=$Root`npantalla=$PantallaLog`nruntime=$RuntimeLog`neventos=$EventosLog`nversion=5.0.43" | Set-Content -Encoding UTF8 -LiteralPath $InfoFile
function LogLine([string]$s) { Write-Host $s; try { Add-Content -LiteralPath $PantallaLog -Encoding UTF8 -Value $s } catch { } }
function Event([string]$name, $data=@{}) { try { ([ordered]@{ts=(Get-Date).ToString('o');event=$name;session_id=$Session;data=$data} | ConvertTo-Json -Compress -Depth 8) | Add-Content -LiteralPath $EventosLog -Encoding UTF8 } catch { } }
function Test-OllamaModel([string]$Model) {
    try {
        $tags = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 5
        $names = @($tags.models | ForEach-Object { $_.name })
        LogLine "[INFO] Modelos Ollama: $($names -join ', ')"
        if ($names -notcontains $Model) {
            LogLine "[WARN] El modelo solicitado '$Model' no existe. Se usara fallback si hay modelos disponibles."
            if ($names -contains 'llama3.2:3b') { return 'llama3.2:3b' }
            if ($names.Count -gt 0) { return $names[0] }
        }
        return $Model
    } catch { throw "Ollama no responde en http://127.0.0.1:11434. Abre Ollama o ejecuta 'ollama serve'. Detalle: $($_.Exception.Message)" }
}
function Test-OllamaGenerate([string]$Model) {
    $body = @{ model=$Model; prompt='Responde solo: OK'; stream=$false; options=@{num_predict=8;temperature=0.1} } | ConvertTo-Json -Compress -Depth 5
    try {
        $res = Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:11434/api/generate" -Body $body -ContentType "application/json" -TimeoutSec 20
        LogLine "[OK] Prueba Ollama /api/generate modelo=$Model respuesta=$($res.response)"
    } catch { throw "Ollama responde, pero /api/generate falla con modelo '$Model'. Detalle: $($_.Exception.Message)" }
}
Start-Transcript -LiteralPath $PantallaLog -Append | Out-Null
try {
    LogLine "============================================================"
    LogLine "Ahootsa 5.0.43 - version completa autonoma estable"
    LogLine "============================================================"
    LogLine "Root:       $Root"
    LogLine "Session:    $Session"
    LogLine "Provider:   $Provider"
    LogLine "OllamaModel:$OllamaModel"
    LogLine "Logs:       $LogRoot"
    LogLine "CameraDir:  $CameraDir"
    $Py = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv\Scripts\python.exe"
    $Daemon = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv\Scripts\reachy-mini-daemon.exe"
    if (!(Test-Path $Py)) { throw "No existe Python apps_venv: $Py. Instala/abre Reachy Mini Control antes de usar Ahootsa." }
    if (!(Test-Path $Daemon)) { throw "No existe reachy-mini-daemon: $Daemon. Instala Reachy Mini Control." }
    LogLine "Python:     $Py"
    LogLine "Daemon:     $Daemon"
    if ($InstallMujoco.ToUpperInvariant() -eq "SI") { LogLine "[INFO] Instalando mujoco..."; & $Py -m pip install -U mujoco | Tee-Object -FilePath $RuntimeLog -Append }
    $mujocoOut = & $Py -c "import mujoco; print('MUJOCO_OK', mujoco.__version__)" 2>&1
    if ($LASTEXITCODE -ne 0) { throw "MuJoCo no esta instalado. Ejecuta con -InstallMujoco SI. Detalle: $mujocoOut" }
    LogLine $mujocoOut
    if ($InstallHFDeps.ToUpperInvariant() -eq "SI") { LogLine "[INFO] Instalando dependencias HF..."; & $Py -m pip install -U transformers accelerate sentencepiece safetensors | Tee-Object -FilePath $RuntimeLog -Append }
    if ($Provider.ToLowerInvariant() -eq "ollama") { $OllamaModel = Test-OllamaModel $OllamaModel; Test-OllamaGenerate $OllamaModel }

    $env:AHOOTSA_VERSION="5.0.43"
    $env:AHOOTSA_LOG_ROOT=$LogRoot
    $env:AHOOTSA_CAMERA_DIR=$CameraDir
    $env:AHOOTSA_LLM_PROVIDER=$Provider
    $env:AHOOTSA_OLLAMA_MODEL=$OllamaModel
    $env:AHOOTSA_OLLAMA_BASE_URL="http://127.0.0.1:11434"
    $env:AHOOTSA_OLLAMA_TIMEOUT="$OllamaTimeout"
    $env:AHOOTSA_VOICE=$Voice
    $env:VOICE=$Voice
    $env:REACHY_MINI_VOICE=$Voice
    $env:OPENAI_REALTIME_VOICE=$Voice
    $env:REALTIME_VOICE=$Voice
    $env:TTS_VOICE=$Voice
    $env:AUDIO_VOICE=$Voice
    if ($HFModelPath -ne "") { $env:AHOOTSA_HF_MODEL_PATH=$HFModelPath }
    $Patch = Join-Path $Root "tools\patch_ahootsa_5_0_43.py"
    if (!(Test-Path $Patch)) { throw "No existe parche: $Patch" }
    LogLine "[INFO] Aplicando parche completo 5.0.43 al paquete instalado..."
    & $Py $Patch 2>&1 | Tee-Object -FilePath $RuntimeLog -Append
    if ($LASTEXITCODE -ne 0) { throw "El parche 5.0.43 no se pudo aplicar." }

    LogLine "[INFO] Arrancando daemon MuJoCo..."
    $Tmp = Join-Path $Root ".tmp"; New-Item -ItemType Directory -Force -Path $Tmp | Out-Null
    $DaemonScript = Join-Path $Tmp "start_daemon_mujoco_${Session}.ps1"
    @"
`$env:AHOOTSA_VERSION='5.0.43'
`$env:AHOOTSA_LOG_ROOT='$LogRoot'
`$env:AHOOTSA_CAMERA_DIR='$CameraDir'
`$env:AHOOTSA_LLM_PROVIDER='$Provider'
`$env:AHOOTSA_OLLAMA_MODEL='$OllamaModel'
`$env:AHOOTSA_OLLAMA_BASE_URL='http://127.0.0.1:11434'
`$env:AHOOTSA_OLLAMA_TIMEOUT='$OllamaTimeout'
`$env:AHOOTSA_VOICE='$Voice'
`$env:VOICE='$Voice'
`$env:REACHY_MINI_VOICE='$Voice'
`$env:OPENAI_REALTIME_VOICE='$Voice'
`$env:REALTIME_VOICE='$Voice'
`$env:TTS_VOICE='$Voice'
`$env:AUDIO_VOICE='$Voice'
if ('$HFModelPath' -ne '') { `$env:AHOOTSA_HF_MODEL_PATH='$HFModelPath' }
' START_DAEMON ' + (Get-Date -Format o) | Add-Content -LiteralPath '$RuntimeLog'
& '$Daemon' --sim --fastapi-host 127.0.0.1 --fastapi-port $DaemonPort --no-goto-sleep-on-stop --dataset-update-interval 0 --no-preload-datasets --log-file '$RuntimeLog'
"@ | Set-Content -LiteralPath $DaemonScript -Encoding UTF8
    Start-Process powershell -ArgumentList @('-ExecutionPolicy','Bypass','-File',$DaemonScript) -WindowStyle Minimized | Out-Null
    for ($i=1; $i -le 20; $i++) {
        Start-Sleep -Seconds 1
        try { Invoke-RestMethod "http://127.0.0.1:$DaemonPort/api/daemon/status" -TimeoutSec 2 | Out-Null; LogLine "[OK] Daemon disponible en http://127.0.0.1:$DaemonPort"; break } catch { LogLine "Esperando daemon... $i" }
        if ($i -eq 20) { throw "El daemon no ha quedado disponible en puerto $DaemonPort" }
    }
    LogLine "[INFO] Arrancando app Ahootsa..."
    try { Invoke-RestMethod -Method POST "http://127.0.0.1:$DaemonPort/api/apps/start-app/ahootsa_realtime_ollama_app" -TimeoutSec 10 | Out-Null } catch { LogLine "[WARN] start-app devolvio: $($_.Exception.Message)" }
    LogLine "[INFO] Esperando interfaz en http://127.0.0.1:$AppPort/status ..."
    for ($i=1; $i -le 30; $i++) {
        Start-Sleep -Seconds 1
        try { $st = Invoke-RestMethod "http://127.0.0.1:$AppPort/status" -TimeoutSec 2; LogLine "[OK] /status http=200 version=$($st.version_patch)"; break } catch { LogLine "Esperando app... $i" }
        if ($i -eq 30) { throw "La app no ha quedado disponible en puerto $AppPort" }
    }
    try { $os = Invoke-RestMethod "http://127.0.0.1:$AppPort/ollama/status" -TimeoutSec 5; LogLine "[OK] /ollama/status model=$($os.model) available=$($os.model_available)" } catch { LogLine "[WARN] No se pudo consultar /ollama/status: $($_.Exception.Message)" }
    try { $askBody = @{ prompt='Di hola en una frase breve.' } | ConvertTo-Json -Compress; $ar = Invoke-RestMethod -Method POST "http://127.0.0.1:$AppPort/ollama/ask" -Body $askBody -ContentType "application/json" -TimeoutSec 35; LogLine "[OK] /ollama/ask respuesta=$($ar.answer)" } catch { LogLine "[WARN] Prueba /ollama/ask fallo: $($_.Exception.Message)" }
    if ($OpenBrowser.ToUpperInvariant() -eq "SI") { Start-Process "http://127.0.0.1:$AppPort" }
    LogLine "[OK] Interfaz: http://127.0.0.1:$AppPort"
    LogLine "[OK] Camara PC: http://127.0.0.1:$AppPort/camera/page"
    Event "launcher.end" @{ ok=$true }
} catch {
    LogLine "[ERROR] $($_.Exception.Message)"
    Event "launcher.error" @{ error=$_.Exception.Message }
    throw
} finally { try { Stop-Transcript | Out-Null } catch { } }
