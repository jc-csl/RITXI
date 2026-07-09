# FORZAR_5_IDENTIDAD_CASTELLANO_AHOOTSA.ps1
# Ejecuta solo la parte de identidad/castellano sin lanzar MuJoCo.

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
powershell -ExecutionPolicy Bypass -File (Join-Path $Root "INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1")
