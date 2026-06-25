@echo off
setlocal enabledelayedexpansion
title Lanzador Reachy Mini - Modo Modular Inteligente con Logs
cls

:: =====================================================================
::    0. GENERACIÓN DE MARCA DE TIEMPO Y GESTIÓN DE LOGS
:: =====================================================================
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set FECHA_HORA=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%-%datetime:~12,2%

if not exist logs mkdir logs

set LOG_LANZADOR=logs\lanzador_%FECHA_HORA%.log
set LOG_SERVER=logs\servidor_fastapi_%FECHA_HORA%.log

echo [%FECHA_HORA%] [INFO] Iniciando secuencia de validación del ecosistema... > %LOG_LANZADOR%

echo =====================================================================
echo    🤖 INICIANDO ECOSISTEMA MODULAR (Logs Activados)
echo =====================================================================
echo 📝 Log del Servidor: %LOG_SERVER%
echo 📝 Log del Lanzador: %LOG_LANZADOR%
echo ---------------------------------------------------------------------
echo.

echo [%FECHA_HORA%] [INFO] 1. LIBERANDO PUERTOS (8000 y 8080) >> %LOG_LANZADOR%
echo =====================================================================
echo    1. LIBERANDO PUERTOS (8000 y 8080)
echo =====================================================================
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo [%FECHA_HORA%] [WARN] Matando proceso zombie en puerto 8000 (PID: %%a) >> %LOG_LANZADOR%
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080 ^| findstr LISTENING') do (
    echo [%FECHA_HORA%] [WARN] Matando proceso zombie en puerto 8080 (PID: %%a) >> %LOG_LANZADOR%
    taskkill /f /pid %%a >nul 2>&1
)
echo [OK] Puertos limpios de residuos anteriores.
echo.

echo [%FECHA_HORA%] [INFO] 2. COMPROBACION DE ENTORNO VIRTUAL Y DEPENDENCIAS >> %LOG_LANZADOR%
echo =====================================================================
echo    2. COMPROBACION DE ENTORNO VIRTUAL Y DEPENDENCIAS CON UV
echo =====================================================================
where uv >nul 2>&1
if %errorlevel% neq 0 goto error_uv_missing

if not exist ".venv\Scripts\activate.bat" goto error_venv

echo [%FECHA_HORA%] [INFO] Activando entorno virtual... >> %LOG_LANZADOR%
call .venv\Scripts\activate.bat

echo [%FECHA_HORA%] [INFO] Validando librerías clave con Python... >> %LOG_LANZADOR%
python -c "import ollama, pyttsx3, pygame, fastapi, uvicorn" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Librerias de Python validadas correctamente.
    goto dependencias_listas
)

echo [ADVERTENCIA] Faltan modulos en tu entorno virtual.
echo Instalando dependencias necesarias a maxima velocidad utilizando UV...
echo [%FECHA_HORA%] [WARN] Faltan dependencias. Ejecutando uv pip install... >> %LOG_LANZADOR%
echo.

uv pip install ollama fastapi uvicorn pygame pydantic pyttsx3 numpy reachy-mini-daemon
timeout /t 1 /nobreak >nul

:dependencias_listas
echo [OK] Analisis de dependencias completado de forma eficiente.
echo.

echo [%FECHA_HORA%] [INFO] 3. EXTRACCION DINAMICA DEL MODELO >> %LOG_LANZADOR%
echo =====================================================================
echo    3. EXTRACCION DINAMICA DEL MODELO INTELIGENTE (config.py)
echo =====================================================================
set "MODELO_IA="
if not exist config.py goto error_config_missing
for /f "tokens=2 delims==" %%i in ('findstr /C:"OLLAMA_MODEL" config.py') do set "RAW_LINE=%%i"

set "RAW_LINE=%RAW_LINE: =%"
set "MODELO_IA=%RAW_LINE:"=%"
set "MODELO_IA=%MODELO_IA:'=%"

if "%MODELO_IA%"=="" goto error_config_parse
echo [CONFIG] El modelo configurado es: %MODELO_IA%
echo [%FECHA_HORA%] [CONFIG] Modelo detectado en config.py: %MODELO_IA% >> %LOG_LANZADOR%
echo.

echo [%FECHA_HORA%] [INFO] 4. VALIDACION DE REQUISITOS LOCALES (OLLAMA) >> %LOG_LANZADOR%
echo =====================================================================
echo    4. VALIDACION DE REQUISITOS LOCALES (SERVICIO OLLAMA)
echo =====================================================================
ollama list >nul 2>&1
if %errorlevel% neq 0 goto error_ollama_servicio

ollama list | findstr /I /C:"%MODELO_IA%" >nul
if %errorlevel% equ 0 goto ollama_listo

echo [ADVERTENCIA] El modelo '%MODELO_IA%' no se encuentra descargado en Ollama.
echo Descargando el modelo desde los servidores oficiales, por favor espera...
echo [%FECHA_HORA%] [WARN] Descargando modelo %MODELO_IA% vía ollama pull... >> %LOG_LANZADOR%
echo.
ollama pull %MODELO_IA%

ollama list | findstr /I /C:"%MODELO_IA%" >nul
if %errorlevel% neq 0 goto error_ollama_download

:ollama_listo
echo [OK] Modelo '%MODELO_IA%' verificado y listo en el sistema.
echo.

echo [%FECHA_HORA%] [INFO] 5. LANZAMIENTO DEL ECOSISTEMA REACHY MINI >> %LOG_LANZADOR%
echo =====================================================================
echo    5. LANZAMIENTO DEL ECOSISTEMA REACHY MINI (Modo Logs)
echo =====================================================================
echo [OK] Todo validado perfectamente. Abriendo simulador y servidor minimizados...

:: A. Lanzar Simulador minimizado
echo [%FECHA_HORA%] [INFO] Lanzando simulador reachy-mini-daemon --sim... >> %LOG_LANZADOR%
start /min "Simulador Reachy Mini" cmd /c "reachy-mini-daemon --sim"
timeout /t 6 /nobreak >nul

:: B. Lanzar Servidor Backend redirigiendo logs
echo [%FECHA_HORA%] [INFO] Lanzando Uvicorn puerto 8080 redirigiendo a %LOG_SERVER%... >> %LOG_LANZADOR%
echo 🖥️ El log del servidor FastAPI se esta escribiendo en: %LOG_SERVER%
start /min "Servidor Backend FastAPI" cmd /c "call .venv\Scripts\activate.bat && uvicorn main:app --reload --port 8080 > %LOG_SERVER% 2>&1"

echo [ESPERA] Dando 12 segundos para el despliegue de sockets y render...
timeout /t 12 /nobreak >nul

:: C. GENERACIÓN DEL SCRIPT DE POWERSHELL TEMPORAL (Línea por línea sin bloques rotos)
echo [%FECHA_HORA%] [INFO] Generando script temporal de Auto-Layout... >> %LOG_LANZADOR%
echo 📐 Organizando ventanas (Simulador Izquierda, Chrome Derecha)...

echo Add-Type -TypeDefinition 'Using System; Using System.Runtime.InteropServices; Public Class Win32 { [DllImport("user32.dll")] Public Shared extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint); [DllImport("user32.dll")] Public Shared extern bool SetForegroundWindow(IntPtr hWnd); }' > layout.ps1
echo $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds >> layout.ps1
echo $halfWidth = [int]($screen.Width / 2) >> layout.ps1
echo $height = [int]($screen.Height - 40) >> layout.ps1
echo $processMuJoCo = Get-Process ^| Where-Object { $_.MainWindowTitle -like '*MuJoCo*' -or $_.ProcessName -like '*mujoco*' } ^| Select-Object -First 1 >> layout.ps1
echo if ($processMuJoCo) { [Win32]::MoveWindow($processMuJoCo.MainWindowHandle, 0, 0, $halfWidth, $height, $true) } >> layout.ps1
echo $processChrome = Get-Process ^| Where-Object { $_.MainWindowTitle -like '*Panel Reachy Mini*' -or $_.MainWindowTitle -like '*127.0.0.1:8080*' } ^| Select-Object -First 1 >> layout.ps1
echo if ($processChrome) { [Win32]::MoveWindow($processChrome.MainWindowHandle, $halfWidth, 0, $halfWidth, $height, $true); [Win32]::SetForegroundWindow($processChrome.MainWindowHandle) } >> layout.ps1

:: D. Lanzar Chrome
echo [%FECHA_HORA%] [INFO] Lanzando Google Chrome... >> %LOG_LANZADOR%
echo [CHROME] Abriendo interfaz en Google Chrome para habilitar Web Speech API...
set "CHROME_PATH="
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" set "CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" set "CHROME_PATH=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"

if defined CHROME_PATH (
    start "" "!CHROME_PATH!" http://127.0.0.1:8080
) else (
    start http://127.0.0.1:8080
)

:: Esperar un instante a que Chrome dibuje la ventana y ejecutar el layout limpio
timeout /t 2 /nobreak >nul
powershell -ExecutionPolicy Bypass -File layout.ps1 >nul 2>&1

:: Limpiar el archivo temporal
if exist layout.ps1 del layout.ps1

echo [%FECHA_HORA%] [SUCCESS] Despliegue y Auto-Layout completados con éxito. >> %LOG_LANZADOR%
echo =====================================================================
echo ✅ [PROCESO TERMINADO] Ecosistema operativo y ventanas alineadas.
echo =====================================================================
timeout /t 2 >nul
exit

:: =====================================================================
:: BLOQUE DE ERRORES
:: =====================================================================
:error_uv_missing
color 0C
echo [ERROR CRITICO] 'uv' no esta instalado en tu sistema.
exit
:error_config_missing
color 0C
echo [ERROR CRITICO] No se encontro el archivo config.py.
exit
:error_config_parse
color 0C
echo [ERROR CRITICO] No se pudo leer la variable OLLAMA_MODEL en config.py.
exit
:error_ollama_servicio
color 0C
echo [ERROR CRITICO] El servicio de Ollama no se esta ejecutando.
exit
:error_ollama_download
color 0C
echo [ERROR] No se pudo obtener el modelo '%MODELO_IA%'.
exit
:error_venv
color 0C
echo [ERROR CRITICO] No se encontro la carpeta (.venv).
exit