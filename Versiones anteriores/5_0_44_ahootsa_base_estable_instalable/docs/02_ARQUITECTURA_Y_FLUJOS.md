# Arquitectura y flujos

```text
LANZAR_AHOOTSA_5_0_44.ps1
  → reachy-mini-daemon.exe (8000)
  → POST /api/apps/start-app/ahootsa_realtime_ollama_app
  → ahootsa_realtime_ollama_desktop_app.main
  → reachy_mini_conversation_app.main.run()
  → Hugging Face Realtime oficial
```

Ollama directo:

```text
/ahootsa panel → /ollama/ask → http://127.0.0.1:11434/api/chat → llama3.2:3b
```

Cámara PC:

```text
/camera_pc/page → getUserMedia → /camera_pc/upload → D:\RITXI\logs\camera_pc
```
