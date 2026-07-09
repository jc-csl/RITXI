param(
    [ValidateSet("ollama","hf_local","auto")]
    [string]$Provider = "ollama",
    [string]$OllamaModel = "llama3.2:3b",
    [string]$HFModelPath = "",
    [switch]$InstallMujoco,
    [switch]$InstallHFDeps
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe"
$env:AHOOTSA_LOG_ROOT = "D:\RITXI\logs"
$env:AHOOTSA_CAMERA_DIR = "D:\RITXI\logs\camera"
$env:AHOOTSA_LLM_PROVIDER = $Provider
$env:AHOOTSA_OLLAMA_MODEL = $OllamaModel
$env:OLLAMA_MODEL = $OllamaModel
$env:AHOOTSA_OLLAMA_URL = "http://127.0.0.1:11434"
$env:AHOOTSA_OLLAMA_TIMEOUT = "18"
$env:AHOOTSA_HF_MODEL_PATH = $HFModelPath
$env:AHOOTSA_DISABLE_WINDOWS_TTS = "1"
$env:AHOOTSA_DISABLE_WINDOWS_BEEP = "1"
$env:PYTTSX3_DISABLE = "1"
$env:AHOOTSA_AUDIO_UNICO = "1"

Write-Host "============================================================"
Write-Host "Ahootsa 5.0.40 - estable LLM/camara"
Write-Host "============================================================"
Write-Host "Root:     $Root"
Write-Host "Provider: $Provider"
Write-Host "Ollama:   $OllamaModel"
Write-Host "HF:       $HFModelPath"

if ($InstallMujoco) { & $Py -m pip install mujoco }
if ($InstallHFDeps) { & $Py -m pip install --upgrade transformers accelerate safetensors sentencepiece huggingface_hub }

& $Py (Join-Path $Root "tools\patch_5_0_40_modelo_audio.py") --provider $Provider --ollama-model $OllamaModel --hf-model-path $HFModelPath

if ($Provider -eq "ollama" -or $Provider -eq "auto") {
    try {
        $tags = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 5
        $names = @($tags.models | ForEach-Object { $_.name })
        Write-Host "[OK] Ollama responde. Modelos: $($names -join ', ')"
        if ($names -notcontains $OllamaModel) {
            Write-Host "[WARN] No existe $OllamaModel en ollama list. Modelos disponibles: $($names -join ', ')"
        }
    } catch {
        Write-Host "[WARN] Ollama no responde en 127.0.0.1:11434. Abre Ollama o ejecuta: ollama serve"
    }
}

$Candidates = @(
    (Join-Path $Root "LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1"),
    (Join-Path $Root "LANZAR_AHOOTSA.ps1"),
    (Join-Path $Root "LANZAR_AHOOTSA_5_0_35.ps1")
)
$Launch = $Candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $Launch) { throw "No encuentro lanzador base dentro de $Root" }
Write-Host "[INFO] Lanzador base: $Launch"
& powershell -ExecutionPolicy Bypass -File $Launch
