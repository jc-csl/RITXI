# agents.local.md · Ritxi FastAPI v5

Proyecto Ritxi v5 para Reachy Mini.

Reglas locales:

- Usar `uv` para instalación.
- No usar `pip` directo en documentación de instalación.
- Mantener el panel principal orientado a acciones, no a edición de configuración.
- Las tarjetas de emociones/acciones deben ejecutar movimiento + audio cuando los módulos correspondientes estén activos.
- Mantener checkboxes para probar módulos por separado.
- Priorizar STT local Whisper si Web Speech API transcribe mal.
- Mantener logs por sesión en `logs/`.
- Mantener modo simulado de Reachy con `reachy-mini-daemon --sim`.
