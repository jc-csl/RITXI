param(
    [string]$TargetRoot = "D:\RITXI\5_0_40_ahootsa_estable_llm_camara",
    [string]$OllamaModel = "llama3.2:3b",
    [switch]$Force,
    [switch]$InstallMujoco
)
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path

# IMPORTANTE: no usar -Force:$Force ni -InstallMujoco:$InstallMujoco al invocar otro powershell.
# En Windows PowerShell 5.1 puede transformar el switch en texto y fallar.
$createArgs = @(
    "-ExecutionPolicy", "Bypass",
    "-File", (Join-Path $Here "0_CREAR_VERSION_COMPLETA_5_0_40.ps1"),
    "-TargetRoot", $TargetRoot,
    "-Provider", "ollama",
    "-OllamaModel", $OllamaModel
)
if ($Force.IsPresent) { $createArgs += "-Force" }
if ($InstallMujoco.IsPresent) { $createArgs += "-InstallMujoco" }

& powershell @createArgs
if ($LASTEXITCODE -ne 0) { throw "No se pudo crear/actualizar la 5.0.40." }

Set-Location -LiteralPath $TargetRoot
& powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_40.ps1 -Provider ollama -OllamaModel $OllamaModel
