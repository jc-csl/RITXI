# Arquitectura resumida 5.0.42

- Carpeta local de control: `D:\RITXI\5_0_42_ahootsa_autonoma_estable`.
- Entorno Python real: `%LOCALAPPDATA%\Reachy Mini Control\apps_venv`.
- Paquete Ahootsa instalado: `ahootsa_realtime_ollama_desktop_app`.
- Daemon Reachy: `reachy-mini-daemon.exe` en puerto `8000`.
- Interfaz Ahootsa: puerto `7860`.
- LLM local:
  - `ollama` con modelo `llama3.2:3b`, o
  - `hf_local` con ruta a modelo Hugging Face descargado.
- Cámara PC: navegador/WebView con `navigator.mediaDevices.getUserMedia`, guardando por `/camera/upload`.
- Logs: `D:\RITXI\logs`, un conjunto por ejecución con timestamp.

La 5.0.42 no necesita carpetas antiguas porque no copia de ellas. Parchea directamente el paquete instalado en `apps_venv` y lanza desde su propia carpeta.
