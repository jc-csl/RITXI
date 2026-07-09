@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0LANZAR_AHOOTSA_5_0_42.ps1" -Provider ollama -OllamaModel llama3.2:3b
