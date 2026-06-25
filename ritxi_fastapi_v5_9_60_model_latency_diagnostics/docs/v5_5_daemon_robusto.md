# v5.5 — Corrección de arranque del daemon en Windows

En versiones anteriores el script podía quedarse esperando el puerto `8000` porque el comando `start cmd /c ...` tenía comillas anidadas frágiles. En Windows eso puede impedir que el daemon arranque realmente aunque el script empiece a esperar.

La v5.5 separa el arranque en un script auxiliar:

```text
scripts\daemon_sim_to_log_windows.cmd
```

El script principal llama a ese auxiliar de forma más robusta:

```cmd
start "Ritxi Reachy daemon sim" /min "%ComSpec%" /c call "scripts\daemon_sim_to_log_windows.cmd"
```

Además:

- espera hasta 90 segundos;
- usa un test TCP silencioso y rápido, no `Test-NetConnection` verboso;
- guarda toda la salida del daemon en `logs\reachy_daemon_current.log`;
- añade `arrancar_daemon_windows.cmd` para diagnosticar el daemon por separado.

La ventana gráfica de MuJoCo sigue siendo una ventana nativa de Windows y no se puede incrustar de forma fiable dentro del navegador, pero la salida de terminal del daemon sí se integra en el panel mediante el log.
