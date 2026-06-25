# v5.8.7 · Kill automático del puerto 8000

Cambios:

- `2_INICIAR_DAEMON_RITXI.cmd` mata primero `reachy-mini-daemon.exe`.
- También mata cualquier PID que esté escuchando en el puerto 8000.
- Se añade `0_MATAR_DAEMON_Y_PUERTO_8000.cmd` para limpieza manual.
- Se evita el falso `NativeCommandError` al ejecutar el daemon mediante `cmd.exe /c`.
