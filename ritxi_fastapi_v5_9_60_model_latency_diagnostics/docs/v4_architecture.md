# Arquitectura Ritxi FastAPI v4

## Objetivo

Mantener una conversación fluida con Ritxi usando micro y audio del PC, Ollama como LLM local y Reachy Mini en modo real o daemon simulado.

## Ciclo de turno

```text
1. escuchar micro PC
2. detectar frase final
3. mutear micro con echo guard
4. enviar texto a FastAPI
5. construir prompt con carácter activo
6. consultar LLM
7. extraer emoción
8. sintetizar voz por cola TTS
9. mover Reachy con emoción + movimiento reactivo de habla
10. cooldown
11. reactivar micro
```

## Módulos principales

```text
app/core/config.py                 configuración por variables RITXI_
app/services/character.py          perfiles de carácter y prompt dinámico
app/services/emotions.py           etiquetas e inferencia de emoción
app/orchestration/turn_manager.py  orquestador único del turno
app/orchestration/action_scheduler.py cola de acciones y prioridades
app/audio/tts_queue.py             cola única de voz
app/audio/echo_guard.py            bloqueo/cooldown de micro
app/audio/stt.py                   contrato para STT browser/mock/http
app/robot/reachy_sdk.py            adaptador Reachy Mini / daemon
app/robot/simulated.py             simulador interno
app/robot/motion_library.py        biblioteca de poses/emociones
```

## Prioridades del scheduler

```text
manual  → máxima prioridad
speech  → habla + movimiento reactivo
emotion → gesto principal
idle    → respiración/idle suave
```

## Perfil inicial

`profiles/characters/ritxi_tutor_comunicacion_di.json` define a Ritxi como tutor de comunicación para personas con discapacidad intelectual.

Reglas clave:

- una pregunta por turno;
- frases cortas;
- paciencia;
- refuerzo positivo;
- lenguaje fácil;
- sin infantilizar;
- actividades breves de comunicación.

## Límites actuales

- El micro PC usa Web Speech API de Chrome/Edge para pruebas rápidas.
- Para STT 100% local/offline hay que conectar un servidor Whisper/Faster-Whisper a `RITXI_STT_PROVIDER=http`.
- El robot real no se valida desde este entorno; la app está preparada para `reachy-mini-daemon --sim` y después Reachy real.
