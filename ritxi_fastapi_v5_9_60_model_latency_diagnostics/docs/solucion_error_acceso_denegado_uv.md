# Solución: `error: failed to remove file ... Acceso denegado` con uv en Windows

## Qué significa

No es un error de código de Ritxi. En Windows aparece cuando `uv` intenta modificar paquetes dentro de `.venv` mientras otro proceso tiene cargada una DLL/PYD de Python.

Ejemplo típico:

```text
error: failed to remove file
D:\ritxi_fastapi_v3\.venv\Lib\site-packages\websockets/speedups.cp312-win_amd64.pyd
Acceso denegado. (os error 5)
```

Normalmente ocurre porque están abiertos:

- `reachy-mini-daemon --sim`
- `uvicorn` / FastAPI
- otro Python de Ritxi
- un terminal anterior que no se cerró bien

## Solución rápida

Cerrar las terminales que estén usando Ritxi. Si no basta, ejecutar:

```powershell
taskkill /F /IM python.exe
taskkill /F /IM uvicorn.exe
taskkill /F /IM reachy-mini-daemon.exe
```

Después:

```powershell
cd D:\ritxi_fastapi_v3
scripts\setup_uv_windows.bat
scripts\run_reachy_sim_daemon.bat
```

## Cambio aplicado en v3.2

Los scripts `run_*.bat` ya no usan `uv run`, porque `uv run` puede sincronizar dependencias antes de arrancar y provocar este bloqueo.

Ahora usan directamente:

```bat
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8080
```

`uv` queda reservado para instalación y actualización de dependencias.


## Nota adicional v3.3

Además, en Windows los scripts normales no usan `--reload`, para evitar reinicios cuando `pyttsx3/comtypes` genera archivos internos dentro de `.venv`. Usa `scripts\run_dev_reload_windows.bat` solo cuando estés desarrollando código y quieras autorecarga limitada.
