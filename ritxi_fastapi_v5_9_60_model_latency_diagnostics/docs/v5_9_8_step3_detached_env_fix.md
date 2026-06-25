# v5.9.8 · Paso 3 corregido

Cambios:
- `3_RUN_RITXI.cmd` abre PowerShell en nueva ventana y sale.
- Evita el mensaje `¿Desea terminar el trabajo por lotes (S/N)?`.
- Añade `3B_DEBUG_FASTAPI_CON_ENV.cmd` para depuración manual con entorno correcto.
- FastAPI arranca con:
  - `RITXI_MODE=reachy_daemon`
  - `RITXI_LLM_PROVIDER=ollama`
  - `RITXI_TTS_PROVIDER=browser`
