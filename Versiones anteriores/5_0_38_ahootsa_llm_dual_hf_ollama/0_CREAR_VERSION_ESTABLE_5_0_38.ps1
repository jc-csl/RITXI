param(
    [string]$TargetRoot = "D:\RITXI\5_0_38_ahootsa_llm_dual_hf_ollama",
    [switch]$Force,
    [switch]$InstallMujoco,
    [ValidateSet("auto","hf_local","ollama")]
    [string]$Provider = "auto",
    [string]$HFModelPath = "",
    [string]$OllamaModel = "llama3.2:3b",
    [switch]$InstallHFDeps
)
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe"

Write-Host "============================================================"
Write-Host "Ahootsa 5.0.38 - version estable LLM dual HF local + Ollama"
Write-Host "============================================================"
Write-Host "Destino: $TargetRoot"
Write-Host "Provider: $Provider"
Write-Host "HFModelPath: $HFModelPath"
Write-Host "OllamaModel: $OllamaModel"

$Sources = @(
    "D:\RITXI\5_0_37_ahootsa_estable_ollama_auto_camara",
    "D:\RITXI\5_0_36_ahootsa_estable_ollama_camara",
    "D:\RITXI\5_0_35_ahootsa_completa_camara_pc",
    "D:\RITXI\5_0_34_ahootsa_completa_consolidada",
    "D:\RITXI\5_0_25_ahootsa_logs_simples_actividades_recuperadas"
)
$SourceRoot = $null
foreach ($s in $Sources) { if (Test-Path -LiteralPath $s) { $SourceRoot = $s; break } }
if (-not $SourceRoot) { throw "No encuentro base completa en D:\RITXI. Necesito 5.0.37/5.0.36/5.0.35/5.0.34 o 5.0.25." }
Write-Host "Base: $SourceRoot"

if (Test-Path -LiteralPath $TargetRoot) {
    if ($Force) { Remove-Item -LiteralPath $TargetRoot -Recurse -Force }
    else { throw "Ya existe $TargetRoot. Ejecuta con -Force para sustituirla." }
}
Copy-Item -LiteralPath $SourceRoot -Destination $TargetRoot -Recurse -Force

New-Item -ItemType Directory -Force -Path (Join-Path $TargetRoot "tools") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $TargetRoot "docs") | Out-Null
Copy-Item -LiteralPath (Join-Path $Here "tools\patch_5_0_38_llm_dual_hf_ollama.py") -Destination (Join-Path $TargetRoot "tools\patch_5_0_38_llm_dual_hf_ollama.py") -Force
Copy-Item -LiteralPath (Join-Path $Here "docs\AHOOTSA_5_0_38_LLM_DUAL_HF_OLLAMA.md") -Destination (Join-Path $TargetRoot "docs\AHOOTSA_5_0_38_LLM_DUAL_HF_OLLAMA.md") -Force
Copy-Item -LiteralPath (Join-Path $Here "README.md") -Destination (Join-Path $TargetRoot "README_5_0_38.md") -Force

if (-not (Test-Path -LiteralPath $Py)) { throw "No encuentro Python apps_venv: $Py" }
if ($InstallMujoco) { & $Py -m pip install mujoco }
if ($InstallHFDeps) {
    Write-Host "[INFO] Instalando dependencias Hugging Face en apps_venv. Puede tardar bastante."
    & $Py -m pip install --upgrade transformers accelerate safetensors sentencepiece
    Write-Host "[WARN] torch no se instala automáticamente aquí porque depende de CPU/GPU/CUDA. Si falta, instala la versión adecuada."
}

$env:AHOOTSA_LOG_ROOT = "D:\RITXI\logs"
$env:AHOOTSA_CAMERA_DIR = "D:\RITXI\logs\camera"
$env:AHOOTSA_LLM_PROVIDER = $Provider
$env:AHOOTSA_HF_MODEL_PATH = $HFModelPath
$env:AHOOTSA_OLLAMA_URL = "http://127.0.0.1:11434"
$env:AHOOTSA_OLLAMA_MODEL = $OllamaModel
$env:OLLAMA_MODEL = $OllamaModel
$env:AHOOTSA_OLLAMA_TIMEOUT = "18"
$env:AHOOTSA_HF_MAX_NEW_TOKENS = "120"
$env:AHOOTSA_AUDIO_UNICO = "1"
$env:AHOOTSA_DISABLE_WINDOWS_TTS = "1"
$env:AHOOTSA_DISABLE_WINDOWS_BEEP = "1"
$env:PYTTSX3_DISABLE = "1"

Write-Host "[INFO] Aplicando parche 5.0.38 en apps_venv..."
& $Py (Join-Path $TargetRoot "tools\patch_5_0_38_llm_dual_hf_ollama.py") --provider $Provider --hf-model-path $HFModelPath --ollama-model $OllamaModel
if ($LASTEXITCODE -ne 0) { throw "No se pudo aplicar el parche 5.0.38." }

$Launcher = @'
param(
    [ValidateSet("auto","hf_local","ollama")]
    [string]$Provider = "auto",
    [string]$HFModelPath = "",
    [string]$OllamaModel = "llama3.2:3b",
    [switch]$InstallMujoco,
    [switch]$InstallHFDeps
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe"

$env:AHOOTSA_LOG_ROOT = "D:\RITXI\logs"
$env:AHOOTSA_CAMERA_DIR = "D:\RITXI\logs\camera"
$env:AHOOTSA_LLM_PROVIDER = $Provider
$env:AHOOTSA_HF_MODEL_PATH = $HFModelPath
$env:AHOOTSA_OLLAMA_URL = "http://127.0.0.1:11434"
$env:AHOOTSA_OLLAMA_MODEL = $OllamaModel
$env:OLLAMA_MODEL = $OllamaModel
$env:AHOOTSA_OLLAMA_TIMEOUT = "18"
$env:AHOOTSA_HF_MAX_NEW_TOKENS = "120"
$env:AHOOTSA_AUDIO_UNICO = "1"
$env:AHOOTSA_DISABLE_WINDOWS_TTS = "1"
$env:AHOOTSA_DISABLE_WINDOWS_BEEP = "1"
$env:PYTTSX3_DISABLE = "1"

Write-Host "============================================================"
Write-Host "Ahootsa 5.0.38 - LLM dual HF local + Ollama"
Write-Host "============================================================"
Write-Host "Root:      $Root"
Write-Host "Provider:  $Provider"
Write-Host "HF local:  $HFModelPath"
Write-Host "Ollama:    $env:AHOOTSA_OLLAMA_URL modelo=$OllamaModel"
Write-Host "Camara:    http://127.0.0.1:7860/camera/page"

if ($InstallMujoco) { & $Py -m pip install mujoco }
if ($InstallHFDeps) {
    & $Py -m pip install --upgrade transformers accelerate safetensors sentencepiece
    Write-Host "[WARN] Si falta torch, instala la version adecuada para CPU/GPU."
}

if ($Provider -eq "hf_local" -or (($Provider -eq "auto") -and $HFModelPath)) {
    if (-not $HFModelPath) { Write-Host "[WARN] Provider HF local pedido pero HFModelPath está vacío." }
    elseif (-not (Test-Path -LiteralPath $HFModelPath)) { Write-Host "[WARN] No existe HFModelPath: $HFModelPath" }
    else { Write-Host "[OK] Modelo HF local encontrado: $HFModelPath" }
}

try {
    $tags = Invoke-RestMethod -Uri "$env:AHOOTSA_OLLAMA_URL/api/tags" -TimeoutSec 4
    $names = @($tags.models | ForEach-Object { $_.name })
    Write-Host "[OK] Ollama responde. Modelos: $($names -join ', ')"
    if (($Provider -eq "ollama" -or $Provider -eq "auto") -and ($names -notcontains $OllamaModel)) {
        Write-Host "[WARN] El modelo Ollama '$OllamaModel' no está en ollama list."
        if ($names -contains "llama3.2:3b") {
            $env:AHOOTSA_OLLAMA_MODEL = "llama3.2:3b"; $env:OLLAMA_MODEL = "llama3.2:3b"
            Write-Host "[INFO] Usando llama3.2:3b."
        }
    }
} catch {
    Write-Host "[WARN] Ollama no responde. Si usas Provider hf_local, esto no es grave. Si usas Ollama, ejecuta ollama serve."
}

& $Py (Join-Path $Root "tools\patch_5_0_38_llm_dual_hf_ollama.py") --provider $Provider --hf-model-path $HFModelPath --ollama-model $env:AHOOTSA_OLLAMA_MODEL

$Candidates = @(
    (Join-Path $Root "LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1"),
    (Join-Path $Root "LANZAR_AHOOTSA.ps1"),
    (Join-Path $Root "LANZAR_AHOOTSA_5_0_37.ps1"),
    (Join-Path $Root "LANZAR_AHOOTSA_5_0_36.ps1"),
    (Join-Path $Root "LANZAR_AHOOTSA_5_0_35.ps1")
)
$Launch = $Candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $Launch) { throw "No encuentro lanzador base dentro de $Root" }
Write-Host "[INFO] Lanzador base: $Launch"
& powershell -ExecutionPolicy Bypass -File $Launch
'@
Set-Content -LiteralPath (Join-Path $TargetRoot "LANZAR_AHOOTSA_5_0_38.ps1") -Value $Launcher -Encoding UTF8

$Check = @'
param(
    [ValidateSet("auto","hf_local","ollama")]
    [string]$Provider = "auto",
    [string]$HFModelPath = "",
    [string]$OllamaModel = "llama3.2:3b"
)
$ErrorActionPreference = "Continue"
Write-Host "=== Diagnostico Ahootsa 5.0.38 ==="
Write-Host "Provider: $Provider"
Write-Host "HFModelPath: $HFModelPath"
Write-Host "OllamaModel: $OllamaModel"
Write-Host "`n1) ollama list"
try { & ollama list } catch { Write-Host "ERROR ollama list: $($_.Exception.Message)" }
Write-Host "`n2) API Ollama /api/tags"
try { (Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 5).Content } catch { Write-Host "ERROR: $($_.Exception.Message)" }
Write-Host "`n3) HF local"
if($HFModelPath){ if(Test-Path -LiteralPath $HFModelPath){ Write-Host "OK existe $HFModelPath" } else { Write-Host "ERROR no existe $HFModelPath" } } else { Write-Host "HFModelPath vacio" }
Write-Host "`n4) Endpoints Ahootsa si la app está abierta"
foreach($u in @("http://127.0.0.1:7860/llm/status","http://127.0.0.1:7860/ollama/status","http://127.0.0.1:7860/camera/health","http://127.0.0.1:7860/camera/page")){
  Write-Host "--- $u"
  try { (Invoke-WebRequest -UseBasicParsing -Uri $u -TimeoutSec 6).Content.Substring(0,[Math]::Min(900,((Invoke-WebRequest -UseBasicParsing -Uri $u -TimeoutSec 6).Content.Length))) } catch { Write-Host "ERROR: $($_.Exception.Message)" }
}
Write-Host "`n5) Pregunta LLM si la app está abierta"
try {
  $body = @{ prompt="Di solo: OK Ahootsa"; provider=$Provider; model=$OllamaModel } | ConvertTo-Json -Depth 5
  (Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:7860/llm/ask" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 40).Content
} catch { Write-Host "ERROR ask: $($_.Exception.Message)" }
'@
Set-Content -LiteralPath (Join-Path $TargetRoot "1_COMPROBAR_LLM_CAMARA_5_0_38.ps1") -Value $Check -Encoding UTF8

$FindHF = @'
$roots = @(
  "D:\RITXI\models",
  "$env:USERPROFILE\.cache\huggingface\hub",
  "$env:LOCALAPPDATA\huggingface\hub"
)
Write-Host "Buscando posibles modelos Hugging Face locales..."
foreach($r in $roots){
  if(Test-Path -LiteralPath $r){
    Write-Host "`nROOT $r"
    Get-ChildItem -LiteralPath $r -Recurse -Filter config.json -ErrorAction SilentlyContinue | Select-Object -First 40 | ForEach-Object {
      Write-Host $_.DirectoryName
    }
  }
}
'@
Set-Content -LiteralPath (Join-Path $TargetRoot "2_BUSCAR_MODELOS_HF_LOCALES_5_0_38.ps1") -Value $FindHF -Encoding UTF8

$Summary = @'
param([string]$LogRoot="D:\RITXI\logs")
$ErrorActionPreference = "SilentlyContinue"
$patterns = "ERROR|WARN|Traceback|Exception|404|timeout|timed out|Ollama|ollama|HF|Hugging|transformers|torch|camera|camara|getUserMedia|NotAllowedError|NotFoundError|pyttsx3|winsound|pygame|connected=False|can_proceed=False|ahootsa-local|llama3.2|llm"
$out = Join-Path $LogRoot "ULTIMA_EJECUCION_AHOOTSA_5_0_38_RESUMEN.log"
"Resumen Ahootsa 5.0.38 generado: $(Get-Date -Format o)" | Set-Content -LiteralPath $out -Encoding UTF8
Get-ChildItem -LiteralPath $LogRoot -File | Sort-Object LastWriteTime -Descending | Select-Object -First 14 | ForEach-Object {
  "`n------------------------------------------------------------`nArchivo: $($_.FullName)`nLastWrite: $($_.LastWriteTime.ToString('o')) Size: $($_.Length)" | Add-Content -LiteralPath $out -Encoding UTF8
  $lines = Get-Content -LiteralPath $_.FullName -Tail 320
  $rel = $lines | Select-String -Pattern $patterns
  if($rel){ $rel | ForEach-Object { $_.Line } | Add-Content -LiteralPath $out -Encoding UTF8 } else { "Sin coincidencias relevantes." | Add-Content -LiteralPath $out -Encoding UTF8 }
}
Write-Host "Resumen: $out"
'@
Set-Content -LiteralPath (Join-Path $TargetRoot "3_RESUMIR_LOGS_5_0_38.ps1") -Value $Summary -Encoding UTF8

@"
Ahootsa 5.0.38
===============

Esta versión permite usar:
- Hugging Face local descargado en disco.
- Ollama con llama3.2:3b.

Lanzar con modo automático:
  cd $TargetRoot
  powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_38.ps1

Lanzar forzando Ollama:
  powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_38.ps1 -Provider ollama -OllamaModel llama3.2:3b

Lanzar forzando Hugging Face local:
  powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_38.ps1 -Provider hf_local -HFModelPath "D:\RITXI\models\TU_MODELO_HF"

Buscar modelos HF locales:
  powershell -ExecutionPolicy Bypass -File .\2_BUSCAR_MODELOS_HF_LOCALES_5_0_38.ps1

Probar cámara:
  http://127.0.0.1:7860/camera/page
"@ | Set-Content -LiteralPath (Join-Path $TargetRoot "instrucciones_5_0_38.txt") -Encoding UTF8

Write-Host "============================================================"
Write-Host "Version 5.0.38 creada"
Write-Host "============================================================"
Write-Host "cd $TargetRoot"
Write-Host "powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_38.ps1"
