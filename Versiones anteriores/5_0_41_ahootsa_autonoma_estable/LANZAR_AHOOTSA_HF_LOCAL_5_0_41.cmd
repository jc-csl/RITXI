@echo off
if "%~1"=="" (
  echo Uso: LANZAR_AHOOTSA_HF_LOCAL_5_0_41.cmd D:\RITXI\models\TU_MODELO_HF
  exit /b 1
)
powershell -ExecutionPolicy Bypass -File "%~dp0LANZAR_AHOOTSA_5_0_41.ps1" -Provider hf_local -HFModelPath "%~1"
