# Instalación con uv — Ritxi FastAPI v3.3

## Objetivo

Probar Ritxi con:

```text
Reachy Mini daemon en simulación + Ollama + micro PC + audio PC
```

## 1. Instalar uv

```powershell
winget install --id=astral-sh.uv -e
uv --version
```

## 2. Instalar dependencias del proyecto

```powershell
cd D:\ritxi_fastapi_v3
scripts\setup_uv_windows.bat
```

El script ejecuta:

```powershell
uv venv .venv
uv pip install -r requirements.txt
uv pip install -r requirements-optional.txt
uv pip install -r requirements-dev.txt
```

## 3. Terminal 1: daemon Reachy simulado

```powershell
cd D:\ritxi_fastapi_v3
scripts\run_reachy_sim_daemon.bat
```

Si no funciona, prueba:

```powershell
.\.venv\Scripts\reachy-mini-daemon.exe --sim
```

## 4. Terminal 2: Ollama

```powershell
ollama pull gemma3:1b
ollama pull qwen3:0.6b
ollama pull llama3.2:3b
ollama list
```

## 5. Terminal 3: Ritxi

```powershell
cd D:\ritxi_fastapi_v3
scripts\run_reachy_sim_ollama_audio_windows.bat
```

Abre:

```text
http://127.0.0.1:8080
```

## 6. Prueba de funcionamiento

En la interfaz:

1. Activa micro, audio, movimiento y streaming.
2. Pulsa `Dictar con micro PC`.
3. Habla.
4. Revisa el texto.
5. Pulsa `Enviar turno`.

Flujo esperado:

```text
micro PC → texto → FastAPI → Ollama → pyttsx3 → Reachy sim → cooldown
```


## Nota sobre `--reload` en Windows

Los scripts normales no usan `--reload`. Esto evita que Uvicorn se reinicie cuando `pyttsx3/comtypes` crea archivos internos en `.venv`.

Para programar con autorecarga, usa:

```powershell
scripts\run_dev_reload_windows.bat
```
