# v5.9.28 · Limpieza de scripts y requirements

## Objetivo

Simplificar la raíz del proyecto y separar la instalación de modelos de lenguaje de la instalación Python.

## Scripts visibles

- `0_INSTALAR_MODELOS_OLLAMA.cmd`
- `0_INSTALAR_MODELOS_OLLAMA.sh`
- `1_INSTALAR_RITXI.cmd`
- `2_INICIAR_DAEMON_RITXI.cmd`
- `2_INICIAR_DAEMON_RITXI.ps1`
- `3_RUN_RITXI.cmd`
- `3_RUN_RITXI.ps1`
- `4_SALIR_RITXI.cmd`

## Requirements

Antes había varios archivos:

- `requirements.txt`
- `requirements-dev.txt`
- `requirements-optional.txt`
- `requirements-stt-whisper.txt`

Ahora queda solo:

- `requirements.txt`

Incluye base, pruebas, Reachy/MuJoCo, audio y Whisper local.

## Modelos

Nuevo script:

- `0_INSTALAR_MODELOS_OLLAMA.cmd`
- `0_INSTALAR_MODELOS_OLLAMA.sh`

Modelos:

- `qwen3:0.6b`
- `gemma3:1b`
- `llama3.2:1b`
- `llama3.2:3b`
