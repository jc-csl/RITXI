# v5.3 · Daemon integrado en panel y scripts simplificados

La v5.3 añade un gestor ligero del daemon Reachy Mini.

## Límites técnicos

La escena MuJoCo se abre como ventana gráfica nativa de Windows. Por eso no se incrusta dentro del HTML del panel. El panel sí integra:

- Estado del puerto `127.0.0.1:8000`.
- Últimas líneas de terminal del daemon.
- Botón para iniciar el daemon desde el panel.
- Botón para refrescar salida.
- Botón para parar el daemon si fue lanzado por la app.

## Scripts finales

- `instalar_windows.cmd`: instala dependencias con `uv`.
- `ejecutar_windows.cmd`: arranca daemon si hace falta y lanza Ritxi.
- `instalar_y_ejecutar_windows.cmd`: instala y ejecuta.

Los scripts antiguos se han dejado solo como alias en `scripts/` para compatibilidad.
