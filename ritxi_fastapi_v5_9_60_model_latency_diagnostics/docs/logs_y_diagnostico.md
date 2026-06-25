# Logs de sesión y diagnóstico v4.1

Desde la v4.1, cada arranque de Ritxi crea automáticamente una carpeta local:

```text
logs/
```

Dentro se generan dos archivos por sesión:

```text
logs/session_YYYYMMDD_HHMMSS_pidXXXX.log
logs/session_YYYYMMDD_HHMMSS_pidXXXX.jsonl
```

El nombre contiene la fecha y hora exacta de inicio de la sesión y el PID del proceso Python.

## Archivo `.log`

Es el log humano completo. Sirve para leer de forma lineal qué ha pasado:

- arranque de FastAPI;
- configuración activa;
- conexión con Reachy o daemon simulado;
- disponibilidad de Ollama;
- eventos de micro y echo guard;
- turnos de conversación;
- cola de acciones;
- TTS;
- movimientos;
- errores y avisos.

## Archivo `.jsonl`

Es un log estructurado. Cada línea es un JSON independiente. Sirve para medir tiempos y filtrar eventos.

Eventos habituales:

```text
session_start
runtime_start
robot_connect_attempt
robot_connect_result
turn_start
micro_off
llm_start
ollama_request
ollama_first_token
ollama_response
llm_end
emotion_parsed
action_enqueue
action_start
tts_enqueue
tts_start
tts_end
action_end
micro_on
turn_end
client_log
robot_pose_sent
robot_pose_skipped
robot_pose_error
```

## Interpretar una incidencia típica

Si los botones de emoción o pose no mueven el robot, mira estos eventos:

```text
robot_connect_result
robot_pose_skipped
robot_pose_error
action_end
```

Si aparece `not_connected`, el daemon no estaba arrancado o Ritxi se inició antes de que el daemon estuviera preparado.

Orden correcto:

```powershell
# Terminal 1
scripts\run_reachy_sim_daemon.bat

# Esperar a ver: Uvicorn running on http://127.0.0.1:8000

# Terminal 2
scripts\run_v4_realtime_tutor_windows.bat
```

Si el micro no vuelve a escuchar, mira:

```text
micro_off
speaking_state
micro_on
micro_force_on
turn_end
```

En la interfaz hay un botón **Forzar micro ON** para desbloquear la escucha durante pruebas.

## Consejos para la conversación natural

1. Usa Chrome o Edge.
2. Selecciona `es-ES` en idioma de micro.
3. Pulsa **Tutor DI tiempo real**.
4. Pulsa **Activar conversación tiempo real**.
5. Habla con frases cortas y espera a que Ritxi termine.
6. Si no escucha de nuevo, pulsa **Forzar micro ON** y revisa el log.

La Web Speech API del navegador depende de Windows/Chrome/Edge y puede transcribir mal. Para producción offline conviene sustituirla por un STT persistente local como Whisper/Faster-Whisper.
