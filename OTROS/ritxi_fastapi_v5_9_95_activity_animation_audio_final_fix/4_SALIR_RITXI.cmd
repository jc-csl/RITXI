@echo off
title 4 - SALIR RITXI
echo ============================================================
echo  4 - SALIR RITXI
echo ============================================================
echo Cerrando daemon Reachy y Ritxi/FastAPI...
echo.

taskkill /IM reachy-mini-daemon.exe /F >nul 2>nul

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
    echo Cerrando proceso en puerto 8080 PID %%a
    taskkill /PID %%a /F >nul 2>nul
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Cerrando proceso en puerto 8000 PID %%a
    taskkill /PID %%a /F >nul 2>nul
)

echo.
echo [OK] Ritxi y daemon cerrados si estaban abiertos.
pause
