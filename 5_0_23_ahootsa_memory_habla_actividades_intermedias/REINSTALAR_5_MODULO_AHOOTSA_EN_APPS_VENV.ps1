# REINSTALAR_5_MODULO_AHOOTSA_EN_APPS_VENV.ps1
# Corrige ModuleNotFoundError: No module named ahootsa_realtime_ollama_desktop_app

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
powershell -ExecutionPolicy Bypass -File (Join-Path $Root "INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1")
