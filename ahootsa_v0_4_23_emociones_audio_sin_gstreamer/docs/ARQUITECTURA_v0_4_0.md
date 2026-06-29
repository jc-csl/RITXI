# Arquitectura v0.4.2

```text
Usuario habla
  ↓
App original Reachy Mini Conversation
  ↓
Backend realtime de voz, por defecto Hugging Face Hosted
  ↓
Modelo realtime decide respuesta o herramienta
  ↓
Herramientas originales:
  - dance
  - play_emotion
  - move_head
  - camera
  - remember
  - forget
  - etc.
  ↓
Nueva herramienta:
  - ask_ollama
      ↓
      Ollama local http://127.0.0.1:11434
      modelo ahootsa-local:latest
```

Esta versión no intenta convertir Ollama en backend realtime de audio. Eso requeriría STT local, TTS local y un orquestador distinto.
