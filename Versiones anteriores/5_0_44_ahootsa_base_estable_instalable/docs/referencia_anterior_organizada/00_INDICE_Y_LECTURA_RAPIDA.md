# Ahootsa — documentación técnica organizada

**Versión documental:** 2026-07-09  
**Objetivo:** sustituir la carpeta de documentación dispersa por una estructura única, sin duplicados, orientada a instalación, configuración, arquitectura, flujos de comunicación, diagnóstico y modificación del código.

## Lectura recomendada

```text
00_INDICE_Y_LECTURA_RAPIDA.md
01_INSTALACION_EQUIPO_NUEVO.md
02_ARQUITECTURA_GENERAL.md
03_APP_OFICIAL_REACHY_Y_AHOOTSA.md
04_MODELO_CONVERSACIONAL_HUGGINGFACE_Y_OLLAMA.md
05_FLUJOS_COMUNICACION_Y_PUERTOS.md
06_CONFIGURACION_PERFILES_VARIABLES.md
07_HERRAMIENTAS_ACTIVIDADES_MEMORY_CAMARA_AUDIO.md
08_LOGS_DIAGNOSTICO_Y_DEPURACION.md
09_MODIFICAR_CODIGO_Y_MANTENIMIENTO.md
10_VERSIONES_LIMPIEZA_Y_MIGRACION.md
99_FUENTES_REVISADAS_Y_DUPLICADOS.md
assets/Reachy mini datasheet.pdf
```

## Resumen rápido

Ahootsa es una aplicación propia registrada en el ecosistema de Reachy Mini. La app que se lanza normalmente es:

```text
ahootsa_realtime_ollama_app
```

El lanzamiento se realiza a través del daemon oficial de Reachy Mini:

```text
POST http://127.0.0.1:8000/api/apps/start-app/ahootsa_realtime_ollama_app
```

La interfaz web de la app queda normalmente en:

```text
http://127.0.0.1:7860
```

La IA principal de conversación no es Ollama por defecto. En la arquitectura heredada de la app oficial, la conversación principal usa **Hugging Face Realtime**:

```text
HF_REALTIME_CONNECTION_MODE=deployed  -> backend Hugging Face online
HF_REALTIME_CONNECTION_MODE=local     -> backend Hugging Face local externo por WebSocket
```

Ollama se usa como **IA local auxiliar**, por ejemplo mediante una herramienta `ask_ollama` o endpoints añadidos por Ahootsa:

```text
http://127.0.0.1:11434/api/generate
modelo recomendado: llama3.2:3b
```

## Estado recomendado en un equipo estable

Para una instalación limpia actual se recomienda tener:

```text
D:\RITXI\5_0_43_ahootsa_completa_ollama_estable
D:\RITXI\logs
%LOCALAPPDATA%\Reachy Mini Control\apps_venv
Ollama instalado con llama3.2:3b
```

Las carpetas antiguas pueden archivarse solo después de comprobar que la versión completa actual arranca, conversa, ejecuta actividades y permite consultar Ollama.

## Qué se ha eliminado o fusionado

Se ha eliminado la duplicación entre documentos históricos de versión, documentos largos repetidos y ficheros vacíos. El contenido útil queda fusionado en documentos temáticos. El detalle de fuentes revisadas está en:

```text
99_FUENTES_REVISADAS_Y_DUPLICADOS.md
```
