# 1. Navegar al directorio del proyecto
Set-Location -Path "D:\RITXI\pruebas_local_llm\reachy_mini_conversation_app_local"

# 2. Activar el entorno virtual de Python
.\.venv\Scripts\Activate.ps1

# 3. Definir la ruta al ejecutable del demonio de Reachy Mini
$Daemon = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv\Scripts\reachy-mini-daemon.exe"

# 4. Ejecutar el demonio con todos sus parámetros de simulación
& $Daemon --sim --fastapi-host 127.0.0.1 --fastapi-port 8000 --no-goto-sleep-on-stop --dataset-update-interval 0 --no-preload-datasets