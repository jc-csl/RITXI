# 1. Navegar al directorio del proyecto
Set-Location -Path "D:\RITXI\pruebas_local_llm\reachy_mini_conversation_app_local"

# 2. Activar el entorno virtual de Python
.\.venv\Scripts\Activate.ps1

# 3. Lanzar la aplicación de conversación con la interfaz de Gradio y sin cámara
reachy-mini-conversation-app --gradio --no-camera