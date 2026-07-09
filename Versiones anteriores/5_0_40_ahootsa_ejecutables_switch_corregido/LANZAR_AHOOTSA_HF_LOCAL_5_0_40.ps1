param(
    [string]$TargetRoot = "D:\RITXI\5_0_40_ahootsa_estable_llm_camara",
    [Parameter(Mandatory=$true)]
    [string]$HFModelPath,
    [switch]$Force,
    [switch]$InstallMujoco,
    [switch]$InstallHFDeps
)
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path

$createArgs = @(
    "-ExecutionPolicy", "Bypass",
    "-File", (Join-Path $Here "0_CREAR_VERSION_COMPLETA_5_0_40.ps1"),
    "-TargetRoot", $TargetRoot,
    "-Provider", "hf_local",
    "-HFModelPath", $HFModelPath
)
if ($Force.IsPresent) { $createArgs += "-Force" }
if ($InstallMujoco.IsPresent) { $createArgs += "-InstallMujoco" }
if ($InstallHFDeps.IsPresent) { $createArgs += "-InstallHFDeps" }

& powershell @createArgs
if ($LASTEXITCODE -ne 0) { throw "No se pudo crear/actualizar la 5.0.40." }

Set-Location -LiteralPath $TargetRoot
& powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_40.ps1 -Provider hf_local -HFModelPath $HFModelPath
