   @echo off
title Lanzador Automatico Reachy Mini + FastAPI
cls

echo =====================================================================
echo    LIBERANDO PUERTOS (8000 y 8080)
echo =====================================================================
echo.

:: --- Limpieza Puerto 8000 ---
echo Examinando puerto 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo [PROCESO DETECTADO] Cerrando PID %%a en puerto 8000...
    taskkill /f /pid %%a >nul 2>&1
)

:: --- Limpieza Puerto 8080 ---
echo Examinando puerto 8080...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080 ^| findstr LISTENING') do (
    echo [PROCESO DETECTADO] Cerrando PID %%a en puerto 8080...
    taskkill /f /pid %%a >nul 2>&1
)

echo [OK] Puertos limpios y listos para usar.
echo.

echo =====================================================================
echo    COMPROBANDO ENTORNO VIRTUAL (.venv)
echo =====================================================================
echo.

:: Comprobación física de la ruta usando saltos directos sin paréntesis
if exist ".venv\Scripts\activate.bat" goto :entorno_ok

:entorno_error
color 0C
echo [ERROR CRITICO] No se encontro la carpeta del entorno virtual (.venv).
echo Asegurate de estar ejecutando este script desde la raiz de 'reachy_final_app'.
echo.
pause
exit

:entorno_ok
echo [OK] Carpeta .venv localizada. Validando activacion...

:: Activar el entorno de forma segura
call ".venv\Scripts\activate.bat"

:: Verificar la variable de entorno de forma plana
if "%VIRTUAL_ENV%"=="" goto :sin_variable
echo [OK] Entorno Virtual detectado y activo.
goto :continuar

:sin_variable
color 0E
echo [ADVERTENCIA] El entorno no se pudo registrar globalmente, se forzara la ruta.

:continuar
echo.
echo =====================================================================
echo    INICIANDO ECOSISTEMA REACHY MINI (MODO SIMULACION)
echo =====================================================================
echo.

:: 1. Lanzar el simulador en una ventana independiente
echo [PASO 1] Iniciando el motor grafico MuJoCo (reachy-mini-daemon)...
start "Simulador Reachy Mini" cmd /k "reachy-mini-daemon --sim"

:: 2. Pausa de seguridad para que cargue la ventana 3D por completo
echo.
echo [ESPERA] Dando 12 segundos para que la ventana 3D cargue por completo...
timeout /t 12 /nobreak

echo.
:: 3. Lanzar el servidor de FastAPI asegurando la activacion del entorno local
echo [PASO 2] Levantando servidor FastAPI en puerto 8080...
start "Servidor Backend FastAPI" cmd /k "call .venv\Scripts\activate.bat && uv run uvicorn main:app --reload --port 8080"

:: 4. Espera corta a que Uvicorn asigne el socket
timeout /t 6 /nobreak

echo.
:: 5. Abrir automáticamente el panel de control en tu navegador
echo [PASO 3] Abriendo el Panel Web en tu navegador...
start http://127.0.0.1:8080

echo.
echo =====================================================================
echo    ¡TODO LISTO! Monitorea las ventanas de fondo si es necesario.
echo =====================================================================
pause