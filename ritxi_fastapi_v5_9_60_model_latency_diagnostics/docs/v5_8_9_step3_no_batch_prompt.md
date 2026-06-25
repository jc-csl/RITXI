# v5.8.9 · Paso 3 sin pregunta S/N

El paso `3_RUN_RITXI.cmd` deja de crear un `.cmd` temporal para arrancar FastAPI.

Soluciona el mensaje:

`¿Desea terminar el trabajo por lotes (S/N)?`

FastAPI se lanza directamente con PowerShell `Start-Process` y se redirige a logs:

- `logs\ritxi_fastapi_YYYYMMDD_HHMMSS.out.log`
- `logs\ritxi_fastapi_YYYYMMDD_HHMMSS.err.log`
