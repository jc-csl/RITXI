@echo off
setlocal
title 0 - INSTALAR MODELOS OLLAMA PARA RITXI

cd /d "%~dp0"

echo.
echo ============================================================
echo  RITXI - INSTALADOR DE OLLAMA Y MODELOS DE LENGUAJE
echo ============================================================
echo.
echo Modelos recomendados:
echo   Rapido        - qwen3:0.6b
echo   Equilibrado   - gemma3:1b
echo   Llama rapido  - llama3.2:1b
echo   Calidad       - llama3.2:3b
echo.

where ollama >nul 2>nul
if errorlevel 1 (
    echo [Ritxi] Ollama no esta disponible en PATH.
    echo [Ritxi] Intentando instalar Ollama con WSL/Git Bash si existe...
    echo.

    where wsl >nul 2>nul
    if not errorlevel 1 (
        echo [Ritxi] Ejecutando instalador oficial desde WSL:
        echo curl -fsSL https://ollama.com/install.sh ^| sh
        wsl sh -lc "curl -fsSL https://ollama.com/install.sh | sh"
    ) else (
        where bash >nul 2>nul
        if not errorlevel 1 (
            echo [Ritxi] Ejecutando instalador oficial desde bash:
            bash -lc "curl -fsSL https://ollama.com/install.sh | sh"
        ) else (
            echo [AVISO] No se ha encontrado ollama, wsl ni bash.
            echo Descarga Ollama manualmente desde:
            echo https://ollama.com/download
            echo.
            pause
            exit /b 1
        )
    )
) else (
    echo [Ritxi] Ollama encontrado.
)

echo.
echo [Ritxi] Comprobando modelos instalados...
ollama list

echo.
echo [Ritxi] Instalando modelos recomendados...
echo.

echo [1/4] Rapido: qwen3:0.6b
ollama pull qwen3:0.6b

echo.
echo [2/4] Equilibrado: gemma3:1b
ollama pull gemma3:1b

echo.
echo [3/4] Llama rapido: llama3.2:1b
ollama pull llama3.2:1b

echo.
echo [4/4] Calidad: llama3.2:3b
ollama pull llama3.2:3b

echo.
echo ============================================================
echo  Modelos instalados / disponibles
echo ============================================================
ollama list

echo.
echo [Ritxi] Recomendado por defecto para Ritxi: gemma3:1b
echo.
pause
endlocal
