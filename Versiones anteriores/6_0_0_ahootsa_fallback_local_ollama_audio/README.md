# Ahootsa 6.0.0 — Fallback local con audio + Ollama

Versión limpia. No incluye los scripts antiguos de la rama 5.x que dependían de Hugging Face realtime.

## Qué hace

- Interfaz local en navegador.
- Entrada por voz usando el micrófono del navegador.
- Respuesta con Ollama local (`ahootsa-local:latest` por defecto).
- Voz de salida con síntesis de voz del navegador.
- Actividades básicas de comunicación.
- Juego Memory básico.
- Logs en `D:\RITXI\logs`.

## Qué NO usa

- No usa Hugging Face realtime.
- No usa la app oficial `reachy_mini_conversation_app`.
- No arranca ni mata `reachy-mini-daemon`.
- No usa los scripts de voz Sohee antiguos.
- No usa watchers de voz.

## Requisitos

- Windows.
- Python 3.10+.
- Ollama arrancado en `http://127.0.0.1:11434`.
- Modelo `ahootsa-local:latest`.
- Chrome o Edge para usar micrófono desde el navegador.

## Instalación

```powershell
cd D:\RITXI\6_0_0_ahootsa_fallback_local_ollama_audio
powershell -ExecutionPolicy Bypass -File .\INSTALAR_6_FALLBACK_LOCAL.ps1
```

## Lanzar

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_6_FALLBACK_LOCAL.ps1
```

Abre:

```text
http://127.0.0.1:8090
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_6_FALLBACK_LOCAL.ps1
```

## Crear modelo si no existe

Si ya tienes `ahootsa-local:latest`, no hace falta.

Si no existe y tienes `llama3.2:3b`:

```powershell
ollama create ahootsa-local -f .\Modelfile.ahootsa-local.example
```

## Prueba recomendada

1. Pulsa `Hablar`.
2. Di: `Hola Ahootsa`.
3. Di: `Qué sabes hacer`.
4. Di: `Quiero una actividad de comunicación`.
5. Elige `Iniciación`.

## Nota importante sobre STT

La entrada por sonido usa la API de reconocimiento de voz del navegador. Evita Hugging Face, pero el comportamiento exacto depende de Chrome/Edge y del sistema Windows.
