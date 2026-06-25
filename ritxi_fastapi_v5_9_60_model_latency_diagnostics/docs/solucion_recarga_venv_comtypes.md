# Solución: Uvicorn se reinicia por cambios en `.venv` / `comtypes`

## Síntoma

Al arrancar en Windows aparece algo similar a:

```text
WatchFiles detected changes in '.venv\Lib\site-packages\comtypes\gen\...'. Reloading...
```

Esto puede ocurrir cuando `pyttsx3` inicializa voces de Windows. Internamente usa `comtypes`, que genera archivos Python dentro de `.venv\Lib\site-packages\comtypes\gen`. Si Uvicorn está arrancado con `--reload` vigilando todo el proyecto, detecta esos archivos nuevos y reinicia la app.

## Corrección aplicada

Los scripts normales de ejecución ya no usan `--reload`. Por tanto:

```text
scripts\run_reachy_sim_ollama_audio_windows.bat
scripts\run_ollama_windows.bat
scripts\run_mock_windows.bat
scripts\run_reachy_daemon_mode_windows.bat
```

arrancan Uvicorn sin autorecarga.

## Modo desarrollo

Si se quiere autorecarga para programar, usar:

```powershell
scripts\run_dev_reload_windows.bat
```

Ese script limita la vigilancia a carpetas de código/documentación concretas y evita vigilar `.venv`.
