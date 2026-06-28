@echo off
setlocal
cd /d "%~dp0"

title 5 - INSTALAR RITXI E INICIAR DAEMON

echo ============================================================
echo  5 - INSTALAR RITXI + INICIAR DAEMON
echo ============================================================
echo.
echo Ejecuta seguidos, sin pausa intermedia:
echo   1_INSTALAR_RITXI.cmd
echo   2_INICIAR_DAEMON_RITXI.cmd
echo.

if not exist "1_INSTALAR_RITXI.cmd" (
    echo [ERROR] No encuentro 1_INSTALAR_RITXI.cmd
    pause
    exit /b 1
)

if not exist "2_INICIAR_DAEMON_RITXI.cmd" (
    echo [ERROR] No encuentro 2_INICIAR_DAEMON_RITXI.cmd
    pause
    exit /b 1
)

echo [1/2] Instalando / actualizando Ritxi...
set RITXI_NO_PAUSE=1
call "1_INSTALAR_RITXI.cmd"
set RITXI_NO_PAUSE=
if errorlevel 1 (
    echo.
    echo [ERROR] Fallo 1_INSTALAR_RITXI.cmd
    pause
    exit /b 1
)

echo.
echo [2/2] Iniciando daemon Reachy / MuJoCo...
call "2_INICIAR_DAEMON_RITXI.cmd"
if errorlevel 1 (
    echo.
    echo [ERROR] Fallo 2_INICIAR_DAEMON_RITXI.cmd
    pause
    exit /b 1
)

echo.
echo [OK] Instalacion + daemon completados.
echo Ejecuta ahora:
echo   3_RUN_RITXI.cmd
echo.
pause
endlocal
