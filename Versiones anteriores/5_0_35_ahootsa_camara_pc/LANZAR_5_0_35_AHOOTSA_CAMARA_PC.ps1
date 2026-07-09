param(
    [switch]$InstallMujoco,
    [switch]$Force
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Create = Join-Path $Root "0_CREAR_VERSION_COMPLETA_5_0_35.ps1"
$argsList = @("-ExecutionPolicy", "Bypass", "-File", $Create)
if ($Force) { $argsList += "-Force" }
if ($InstallMujoco) { $argsList += "-InstallMujoco" }
& powershell @argsList
if ($LASTEXITCODE -ne 0) { throw "No se pudo crear/aplicar la version 5.0.35." }
cd "D:\RITXI\5_0_35_ahootsa_completa_camara_pc"
if ($InstallMujoco) {
    & powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_35.ps1 -InstallMujoco
} else {
    & powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_35.ps1
}
