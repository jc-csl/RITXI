# Arquitectura resumen 5.0.43

- Carpeta de control: `D:\RITXI\5_0_43_ahootsa_completa_ollama_estable`.
- Entorno Python real: `%LOCALAPPDATA%\Reachy Mini Control\apps_venv`.
- Paquete parcheado: `ahootsa_realtime_ollama_desktop_app`.
- Daemon: `reachy-mini-daemon.exe`, puerto `8000`.
- Interfaz web: puerto `7860`.
- IA local por defecto: Ollama `llama3.2:3b`.
- Cámara PC: WebView/navegador mediante `navigator.mediaDevices.getUserMedia` y subida a `/camera/upload`.
- Logs: `D:\RITXI\logs`, con timestamp por ejecución.

La versión no depende de carpetas antiguas. Aplica un bootstrap en `__init__.py` del paquete instalado para añadir endpoints y compatibilidad.
