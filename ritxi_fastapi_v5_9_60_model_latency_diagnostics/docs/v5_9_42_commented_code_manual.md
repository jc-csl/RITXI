# v5.9.42 · Código comentado y manual técnico

## Cambios

Se añaden comentarios de arquitectura en los módulos principales del proyecto y se crea un manual técnico Markdown.

## Archivos comentados

- `app/main.py`
- `app/static/app.js`
- `app/audio/local_whisper.py`
- `app/llm/ollama_provider.py`
- `app/orchestration/action_scheduler.py`
- `app/robot/reachy_sdk.py`
- `app/core/config.py`

## Manual añadido

- `docs/MANUAL_CODIGO_RITXI.md`

## Contenido del manual

- estructura de carpetas;
- funciones principales;
- flujo de comunicaciones;
- flujo de conversación por texto;
- flujo de conversación por voz;
- STT local Whisper;
- Ollama;
- control Reachy/MuJoCo;
- acciones, tarjetas y ciclos;
- configuración editable;
- logs y diagnóstico.
