# v5.8.4 · Lanzador Windows simple

Problema corregido: el lanzador anterior podía cerrar la ventana o quedarse esperando sin mostrar el error real de FastAPI.

Nuevos scripts:

- `INSTALAR_RITXI.cmd`
- `INICIAR_RITXI.cmd`
- `INSTALAR_Y_EJECUTAR_RITXI.cmd`
- `INICIAR_DAEMON_REACHY.cmd`
- `INICIAR_FASTAPI_VISIBLE.cmd`

FastAPI se abre en una ventana visible y escribe en:

- `logs\ritxi_fastapi_current.log`

Daemon Reachy escribe en:

- `logs\reachy_daemon_current.log`
