# v5.8.5 · Logs siempre creados y FastAPI visible

Esta versión corrige el caso en el que el lanzador decía que revisaras logs pero los archivos no existían.

Ahora se crean siempre al inicio:

- `logs\lanzador_current.log`
- `logs\reachy_daemon_current.log`
- `logs\ritxi_fastapi_current.log`

FastAPI se abre en una ventana PowerShell visible. Si se cierra o falla, el error se ve en esa ventana y en el log.
