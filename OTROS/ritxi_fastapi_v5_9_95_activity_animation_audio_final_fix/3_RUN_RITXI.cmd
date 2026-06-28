set RITXI_LLM_PROVIDER=ollama
set RITXI_LLM_TIMEOUT_S=60
@echo off
title 3 - RUN RITXI
cd /d "%~dp0"
start "3 - RUN RITXI" powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp03_RUN_RITXI.ps1"
exit /b 0
