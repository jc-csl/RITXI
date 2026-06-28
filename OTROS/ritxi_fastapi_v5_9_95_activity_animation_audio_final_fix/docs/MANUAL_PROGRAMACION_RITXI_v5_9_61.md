# Manual de programación de Ritxi v5.9.61

## 1. Objetivo del proyecto

Ritxi es una aplicación local para controlar un asistente conversacional con:

- interfaz web;
- texto escrito;
- micrófono y STT local;
- IA local mediante Ollama;
- TTS del navegador;
- movimientos/emociones de Reachy Mini o simulación;
- actividades de comunicación, lenguaje, juegos y apoyo emocional.

La versión **v5.9.61** toma como base funcional la **v5.9.60** y añade limpieza documental y comentarios de mantenimiento.

---

## 2. Arquitectura general

```text
Navegador
  └─ app/static/app.js
        ├─ /api/chat
        ├─ /api/audio/transcribe_file
        ├─ /api/robot/action
        ├─ /api/status
        └─ /api/config/file

FastAPI
  └─ app/main.py
        ├─ conversación / Ollama
        ├─ STT local Whisper
        ├─ robot / Reachy daemon
        ├─ configuración
        └─ logs

Servicios externos/locales
  ├─ Ollama: http://127.0.0.1:11434
  ├─ Reachy daemon / MuJoCo: http://127.0.0.1:8000
  └─ navegador: micrófono, TTS y UI
```

---

## 3. Estructura de carpetas

```text
app/
  main.py                     API FastAPI principal
  core/
    config.py                 Configuración central y variables RITXI_
    logging.py                Registro JSONL/log
  models/
    schemas.py                Modelos Pydantic de entrada/salida
  audio/
    local_whisper.py          STT local faster-whisper
    echo_guard.py             Protección básica contra eco
    tts_queue.py              Cola de TTS backend si se usa
  llm/
    ollama_provider.py        Proveedor Ollama
    mock_provider.py          Fallback/mock
    base.py                   Tipos comunes de LLM
  orchestration/
    conversation.py           Gestor de turnos conversacionales
    action_scheduler.py       Cola de acciones de robot/voz
  robot/
    reachy_sdk.py             Adaptador Reachy real/simulado
    motion_library.py         Posturas y movimientos
    recorded_emotions.py      Catálogo de emociones grabadas
  static/
    index.html                Interfaz
    styles.css                Estilos
    app.js                    Controlador frontend
  prompts/
    system_prompt.txt         Prompt general
  config/
    model_presets.json        Modelos visibles en la interfaz
    stt_vocabularies/         Vocabularios guiados
profiles/
  characters/                 Perfiles de carácter
docs/
  MANUAL_PROGRAMACION_RITXI_v5_9_61.md
  MANUAL_USUARIO_RITXI_v5_9_61.md
logs/
  session_*.jsonl             Logs estructurados
  session_*.log               Logs de texto
```

---

## 4. Scripts principales

```text
0_INSTALAR_MODELOS_OLLAMA.cmd   Instala/descarga modelos Ollama
1_INSTALAR_RITXI.cmd            Crea .venv e instala dependencias
2_INICIAR_DAEMON_RITXI.cmd      Inicia daemon Reachy/MuJoCo
3_RUN_RITXI.cmd                 Inicia FastAPI y abre panel
4_SALIR_RITXI.cmd               Cierra procesos
5_INSTALAR_E_INICIAR_DAEMON_RITXI.cmd
                                Ejecuta 1_ y 2_ seguidos
```

`1_INSTALAR_RITXI.cmd` acepta:

```text
RITXI_NO_PAUSE=1
```

para no detenerse cuando lo ejecuta el script `5_`.

---

## 5. Flujo de texto

```text
Usuario escribe
  ↓
app.js · sendTextNow()
  ↓
app.js · sendTurn()
  ↓
POST /api/chat
  ↓
app/main.py · chat()
  ↓
conversation manager
  ↓
OllamaProvider.chat()
  ↓
Ollama local
  ↓
respuesta JSON
  ↓
app.js muestra mensaje
```

Funciones clave en `app/static/app.js`:

- `sendTextNow()`: entrada robusta desde botón o Enter.
- `sendTurn()`: decide si responder localmente o llamar a Ollama.
- `enableTextInputAlways()`: evita que micro/STT bloquee la caja de texto.
- `enterTextPriorityMode()`: pausa micro/STT cuando el usuario escribe.
- `forceUnlockTurnState()`: desbloqueo ligero de turnos.

---

## 6. Flujo de voz

```text
Usuario activa micro
  ↓
startAlwaysOnMic()
  ↓
VAD detecta voz
  ↓
finishPersistentUtterance()
  ↓
WAV en navegador
  ↓
POST /api/audio/transcribe_file
  ↓
local_whisper.py
  ↓
texto transcrito
  ↓
sendTurn()
```

Funciones clave:

- `startAlwaysOnMic()`
- `finishPersistentUtterance()`
- `transcribeBlobWithServer()`
- `transcribe_audio_file()`
- `warmup_whisper_model()`

---

## 7. Modos de interacción

La zona superior del panel distingue:

```text
Texto + IA
Micro + IA
Completo
```

### Texto + IA

- texto ON;
- IA/Ollama ON;
- micro OFF;
- STT OFF;
- robot OFF;
- TTS OFF.

### Micro + IA

- texto ON;
- micro ON;
- STT ON;
- IA/Ollama ON;
- voz/TTS ON;
- robot OFF.

### Completo

- texto ON;
- micro ON;
- STT ON;
- IA/Ollama ON;
- voz/TTS ON;
- robot ON.

El modo seleccionado **no debe cambiar automáticamente**. El sistema puede avisar de lentitud, pero no debe cambiar modelo ni modo sin acción del usuario.

---

## 8. Actividades y contexto

Las tarjetas se definen principalmente en `app/static/app.js`.

Tipos principales:

```text
Solo reproduce        sin turno de usuario
Interacción corta     respuesta breve y cierre
Interacción larga     varios turnos con objetivo concreto
Máxima interacción    contexto creativo mantenido
```

Actividades de máxima interacción:

```text
historia_turnos
cuento_interactivo
final_historia
explicar_imagen
elegir_emocion
```

Funciones clave:

- `interactionLevelForActivity()`
- `activityNeedsMicroPrompt()`
- `vocabularyHintForActivity()`
- `buildActivityContext()`
- `rememberActivityContext()`
- `enrichUserTextWithActivityContext()`
- `fastActivityReply()`

`fastActivityReply()` solo debe usarse para actividades cerradas o muy simples. Las actividades abiertas deben pasar a Ollama para mantener coherencia.

---

## 9. Ollama y latencia

Proveedor:

```text
app/llm/ollama_provider.py
```

Funciones clave:

- `is_available()`
- `chat()`
- `chat_stream()`

Latencias importantes:

```text
first_token_ms      tiempo hasta primer token
total_ms            tiempo total de Ollama
turn_total_ms       tiempo total del turno en frontend/backend
output_total_ms     salida, TTS, robot, refrescos
```

Diagnóstico reciente:

- `gemma3:1b` es el modelo equilibrado recomendado.
- `qwen3:0.6b` es más rápido.
- `llama3.2:3b` puede ser lento en hardware limitado.

---

## 10. STT y vocabulario

Archivo:

```text
app/audio/local_whisper.py
```

Vocabularios:

```text
animal
yes_no
short
open_text
open_name
```

Regla importante:

```text
open_text y open_name no deben filtrarse como respuestas cerradas.
```

Funciones clave:

- `_apply_guided_vocabulary()`
- `_filter_repetition_hallucination()`
- `_load_model()`
- `_transcribe_sync()`
- `transcribe_audio_file()`

---

## 11. Robot y acciones

Archivos:

```text
app/orchestration/action_scheduler.py
app/robot/reachy_sdk.py
```

Flujo:

```text
tarjeta frontend
  ↓
/api/robot/action
  ↓
ActionScheduler.enqueue()
  ↓
ActionScheduler._worker()
  ↓
ReachySdkRobotClient.perform_emotion()
```

Regla importante:

El robot no debe bloquear el modo Texto + IA. Si no hay robot o daemon, el chat debe seguir funcionando.

---

## 12. Logs

Tipos:

```text
session_*.jsonl      diagnóstico estructurado
session_*.log        texto legible
lanzador_*.log       arranque
reachy_daemon_*.log  daemon/simulador
```

Eventos relevantes:

```text
client_log
turn_start
turn_end
llm_start
llm_end
stt_whisper_result
robot_action
```

---

## 13. Archivos comentados en v5.9.61

Se han reforzado comentarios y docstrings en:

```text
app/static/app.js
app/main.py
app/core/config.py
app/audio/local_whisper.py
app/llm/ollama_provider.py
app/orchestration/action_scheduler.py
app/robot/reachy_sdk.py
```

---

## 14. Normas de mantenimiento

1. No mezclar estado de micro con estado de texto.
2. El texto debe poder enviarse siempre.
3. No cambiar modelo ni modo automáticamente.
4. No usar respuesta rápida local en actividades abiertas.
5. Las actividades cerradas pueden responder localmente para ahorrar latencia.
6. Los errores JavaScript deben escribirse en logs, no fallar en silencio.
7. La documentación activa debe corresponder a la versión actual.


## Nota v5.9.62

En v5.9.62 se separan claramente tres conceptos:

```text
Texto + IA rápida  → conversación escrita con IA local, micro apagado
TTS                → lectura en voz alta del texto de la respuesta
Sonido emocional   → sonidos breves oficiales de Ritxi/emociones
```

Desactivar TTS no debe bloquear los sonidos emocionales de Ritxi.
El modo por defecto es Texto + IA rápida con modelo `qwen3:0.6b`.


## Nota v5.9.63

Se añade el modo `Texto + IA + Robot`.

La diferencia entre controles queda así:

```text
Texto + IA rápida   → texto + IA, micro apagado, sin lectura TTS, con sonidos emocionales.
Texto + IA + Robot  → igual que Texto + IA, pero también mueve el robot.
Micro + IA          → micro/STT + IA + voz, texto disponible, robot parado.
Completo            → texto + micro + IA + voz + robot.
```

`Sin sonido` en modo texto significa no leer en voz alta el texto completo de la respuesta.
No significa bloquear los sonidos breves de emociones de Ritxi.
