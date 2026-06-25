# Ritxi v5.8.2 · Corrección de arranque Windows

Cambios aplicados:

- `instalar_y_ejecutar_windows.cmd` llama primero a `instalar_windows.cmd` y después a `ejecutar_windows.cmd`.
- Se corrige la llamada al daemon. La forma correcta desde la raíz es:
  `call "%~dp0arrancar_daemon_windows.cmd"`
- Se evita la ruta problemática:
  `call "%~dp0..\arrancar_daemon_windows.cmd"`
- El navegador no se abre inmediatamente. Primero:
  1. se comprueba/arranca `reachy-mini-daemon --sim`;
  2. se espera hasta 120 segundos a `127.0.0.1:8000`;
  3. se arranca FastAPI;
  4. se espera a `/api/health`;
  5. se añaden 10 segundos extra;
  6. se abre `http://127.0.0.1:8080`.

Logs principales:

- `logs\reachy_daemon_current.log`
- `logs\ritxi_fastapi_current.log`
