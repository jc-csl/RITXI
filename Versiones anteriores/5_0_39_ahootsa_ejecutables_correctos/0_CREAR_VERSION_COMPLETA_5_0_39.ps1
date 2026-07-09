
param(
    [string]$TargetRoot = "D:\RITXI\5_0_39_ahootsa_estable_llm_camara",
    [ValidateSet("ollama","hf_local","auto")]
    [string]$Provider = "ollama",
    [string]$OllamaModel = "llama3.2:3b",
    [string]$HFModelPath = "",
    [switch]$Force,
    [switch]$InstallMujoco,
    [switch]$InstallHFDeps
)
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe"

Write-Host "============================================================"
Write-Host "Ahootsa 5.0.39 - crear version completa estable"
Write-Host "============================================================"
Write-Host "Script:    $Here"
Write-Host "Destino:   $TargetRoot"
Write-Host "Provider:  $Provider"
Write-Host "Ollama:    $OllamaModel"
Write-Host "HF local:  $HFModelPath"

if (-not (Test-Path -LiteralPath $Py)) { throw "No encuentro Python apps_venv: $Py" }

$HereFull = [System.IO.Path]::GetFullPath($Here).TrimEnd('\')
$TargetFull = [System.IO.Path]::GetFullPath($TargetRoot).TrimEnd('\')
if ($HereFull -ieq $TargetFull) {
    throw "No ejecutes el creador usando como TargetRoot la misma carpeta del ZIP. Usa el destino por defecto D:\RITXI\5_0_39_ahootsa_estable_llm_camara o cambia -TargetRoot."
}

$Sources = @(
    "D:\RITXI\5_0_37_ahootsa_estable_ollama_auto_camara",
    "D:\RITXI\5_0_36_ahootsa_estable_ollama_camara",
    "D:\RITXI\5_0_35_ahootsa_completa_camara_pc",
    "D:\RITXI\5_0_34_ahootsa_completa_consolidada",
    "D:\RITXI\5_0_25_ahootsa_logs_simples_actividades_recuperadas"
)
$SourceRoot = $null
foreach ($s in $Sources) { if (Test-Path -LiteralPath $s) { $SourceRoot = $s; break } }
if (-not $SourceRoot) { throw "No encuentro base completa en D:\RITXI. Necesito 5.0.35, 5.0.34 o 5.0.25." }
Write-Host "Base:      $SourceRoot"

if (Test-Path -LiteralPath $TargetRoot) {
    if ($Force) {
        Write-Host "[INFO] Sustituyendo destino existente: $TargetRoot"
        Remove-Item -LiteralPath $TargetRoot -Recurse -Force
    } else {
        Write-Host "[INFO] El destino ya existe. No se borra. Se actualizarán scripts y parches encima. Usa -Force si quieres recrearlo limpio."
    }
}
if (-not (Test-Path -LiteralPath $TargetRoot)) {
    Copy-Item -LiteralPath $SourceRoot -Destination $TargetRoot -Recurse -Force
}

New-Item -ItemType Directory -Force -Path (Join-Path $TargetRoot "tools") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $TargetRoot "docs") | Out-Null
Copy-Item -LiteralPath (Join-Path $Here "tools\patch_5_0_39_modelo_audio.py") -Destination (Join-Path $TargetRoot "tools\patch_5_0_39_modelo_audio.py") -Force
Copy-Item -LiteralPath (Join-Path $Here "README.md") -Destination (Join-Path $TargetRoot "README_5_0_39.md") -Force

if ($InstallMujoco) { & $Py -m pip install mujoco }
if ($InstallHFDeps) { & $Py -m pip install --upgrade transformers accelerate safetensors sentencepiece huggingface_hub }

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

Write-Host "[INFO] Aplicando parche modelo/audio 5.0.39 en apps_venv..."
& $Py (Join-Path $TargetRoot "tools\patch_5_0_39_modelo_audio.py") --provider $Provider --ollama-model $OllamaModel --hf-model-path $HFModelPath
if ($LASTEXITCODE -ne 0) { throw "No se pudo aplicar el parche 5.0.39." }

$launcher = @'
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
Write-Host "Ahootsa 5.0.39 - estable LLM/camara"
Write-Host "============================================================"
Write-Host "Root:     $Root"
Write-Host "Provider: $Provider"
Write-Host "Ollama:   $OllamaModel"
Write-Host "HF:       $HFModelPath"

if ($InstallMujoco) { & $Py -m pip install mujoco }
if ($InstallHFDeps) { & $Py -m pip install --upgrade transformers accelerate safetensors sentencepiece huggingface_hub }

& $Py (Join-Path $Root "tools\patch_5_0_39_modelo_audio.py") --provider $Provider --ollama-model $OllamaModel --hf-model-path $HFModelPath

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
'@
Set-Content -LiteralPath (Join-Path $TargetRoot "LANZAR_AHOOTSA_5_0_39.ps1") -Value $launcher -Encoding UTF8

Write-Host "============================================================"
Write-Host "Version completa creada/actualizada"
Write-Host "============================================================"
Write-Host "Destino: $TargetRoot"
Write-Host "Ejecuta: cd $TargetRoot"
Write-Host "         powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_39.ps1"
