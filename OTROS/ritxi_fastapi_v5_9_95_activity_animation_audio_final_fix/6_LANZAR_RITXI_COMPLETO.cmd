@echo off
setlocal
cd /d "%~dp0"

title 6 - LANZAR RITXI COMPLETO

echo ============================================================
echo  6 - LANZAR RITXI COMPLETO
echo ============================================================
echo.
echo Ejecuta el flujo completo:
echo   1_INSTALAR_RITXI.cmd
echo   2_INICIAR_DAEMON_RITXI.cmd
echo   espera aprox. 45 segundos / puerto 8000
echo   3_RUN_RITXI.cmd
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp06_LANZAR_RITXI_COMPLETO.ps1"
endlocal
