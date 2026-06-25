@echo off
setlocal
cd /d "%~dp0"
set UV_LINK_MODE=copy

echo ============================================================
echo  1 - INSTALAR RITXI
echo ============================================================
echo Carpeta: %CD%
echo.

where uv >nul 2>nul
if errorlevel 1 (
    echo [ERROR] uv no esta instalado o no esta en PATH.
    echo Instala uv con:
    echo   winget install --id=astral-sh.uv -e
    pause
    exit /b 1
)

echo [1/3] Creando entorno virtual .venv...
uv venv .venv
if errorlevel 1 goto ERROR

echo [2/3] Instalando dependencias unificadas...
uv pip install --python ".venv\Scripts\python.exe" -r requirements.txt
if errorlevel 1 goto ERROR

echo [3/3] Preparando carpetas...
if not exist logs mkdir logs
if not exist profiles mkdir profiles

echo.
echo [OK] Ritxi instalado.
echo.
echo IMPORTANTE:
echo   Los modelos de lenguaje se instalan aparte con:
echo   0_INSTALAR_MODELOS_OLLAMA.cmd
echo.
echo Despues ejecuta:
echo   2_INICIAR_DAEMON_RITXI.cmd
echo   3_RUN_RITXI.cmd
echo.
if "%RITXI_NO_PAUSE%"=="1" exit /b 0
pause
exit /b 0

:ERROR
echo.
echo [ERROR] Instalacion interrumpida.
if "%RITXI_NO_PAUSE%"=="1" exit /b 1
pause
exit /b 1
