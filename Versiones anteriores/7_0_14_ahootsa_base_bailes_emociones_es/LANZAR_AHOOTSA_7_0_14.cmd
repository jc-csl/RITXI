@echo off
setlocal
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File ".\LANZAR_AHOOTSA_7_0_14.ps1" %*
