
param(
    [Parameter(Mandatory=$true)]
    [string]$HFModelPath,
    [string]$TargetRoot = "D:\RITXI\5_0_39_ahootsa_estable_llm_camara",
    [switch]$Force,
    [switch]$InstallHFDeps,
    [switch]$InstallMujoco
)
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
& powershell -ExecutionPolicy Bypass -File (Join-Path $Here "0_CREAR_VERSION_COMPLETA_5_0_39.ps1") -TargetRoot $TargetRoot -Provider hf_local -HFModelPath $HFModelPath -Force:$Force -InstallHFDeps:$InstallHFDeps -InstallMujoco:$InstallMujoco
if ($LASTEXITCODE -ne 0) { throw "No se pudo crear/actualizar la 5.0.39." }
Set-Location -LiteralPath $TargetRoot
& powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_39.ps1 -Provider hf_local -HFModelPath $HFModelPath
