# Manual de código de Ritxi

Versión de documentación: **v5.9.42**

Este documento describe la estructura interna del proyecto Ritxi, el flujo de comunicaciones y la función principal de cada carpeta y archivo relevante.

---

## 1. Resumen general

Ritxi es una aplicación local para controlar un asistente con interfaz web, conversación con Ollama, reconocimiento de voz local, síntesis de voz del navegador y control del robot Reachy Mini / MuJoCo.

La arquitectura se divide en cuatro capas:

```text
Navegador / Panel web
        ↓ HTTP / fetch / Web APIs
FastAPI local
        ↓ servicios Python
Ollama + STT Whisper + TTS navegador + Reachy daemon
        ↓
Reachy Mini real o simulación MuJoCo
```

---

## 2. Componentes principales

### 2.1 Navegador

Archivos principales:

```text
app/static/index.html
app/static/styles.css
app/static/app.js
```

Responsabilidades:

- Mostrar el chat.
- Gestionar botones, pestañas y tarjetas.
- Abrir y cerrar micrófono.
- Grabar audio del navegador.
- Enviar audio a FastAPI para STT.
- Enviar texto a FastAPI para Ollama.
- Reproducir TTS con el navegador.
- Pedir acciones de robot a FastAPI.
- Mostrar logs, estado y errores.

### 2.2 Backend FastAPI

Archivo principal:

```text
app/main.py
```

Responsabilidades:

- Crear la aplicación FastAPI.
- Servir la interfaz web.
- Exponer endpoints `/api/...`.
- Coordinar runtime, LLM, STT, robot y configuración.
- Guardar logs de sesión.
- Permitir editar archivos desde la pestaña Configuración.

### 2.3 LLM local con Ollama

Archivos principales:

```text
app/llm/ollama_provider.py
app/prompts/system_prompt.txt
app/config/model_presets.json
```

Responsabilidades:

- Enviar prompts a Ollama.
- Usar modelos como:
  - `qwen3:0.6b`
  - `gemma3:1b`
  - `llama3.2:1b`
  - `llama3.2:3b`
- Controlar tokens, contexto, temperatura y timeout.
- Mantener respuestas cortas y adecuadas para comunicación/lenguaje.

### 2.4 STT local

Archivo principal:

```text
app/audio/local_whisper.py
```

Responsabilidades:

- Cargar Whisper local.
- Transcribir audio WAV.
- Aplicar vocabulario guiado cuando procede.
- Evitar falsos positivos y repeticiones.
- Distinguir actividades cerradas de preguntas abiertas.

### 2.5 Robot Reachy Mini / MuJoCo

Archivos principales:

```text
app/robot/reachy_sdk.py
app/orchestration/action_scheduler.py
```

Responsabilidades:

- Conectar con daemon Reachy/MuJoCo.
- Ejecutar movimientos/emociones.
- Evitar solapes de movimientos.
- Coordinar acción + voz + retorno a posición neutra.

---

## 3. Estructura de carpetas

```text
ritxi_fastapi/
│
├─ app/
│  ├─ main.py
│  ├─ core/
│  │  └─ config.py
│  ├─ audio/
│  │  └─ local_whisper.py
│  ├─ llm/
│  │  └─ ollama_provider.py
│  ├─ robot/
│  │  └─ reachy_sdk.py
│  ├─ orchestration/
│  │  └─ action_scheduler.py
│  ├─ prompts/
│  │  └─ system_prompt.txt
│  ├─ config/
│  │  ├─ model_presets.json
│  │  └─ stt_vocabularies/
│  └─ static/
│     ├─ index.html
│     ├─ styles.css
│     └─ app.js
│
├─ profiles/
│  └─ characters/
│     └─ ritxi_tutor_comunicacion_di.json
│
├─ logs/
│
├─ docs/
│  └─ MANUAL_CODIGO_RITXI.md
│
├─ 0_INSTALAR_MODELOS_OLLAMA.cmd
├─ 1_INSTALAR_RITXI.cmd
├─ 2_INICIAR_DAEMON_RITXI.cmd
├─ 3_RUN_RITXI.cmd
└─ 4_SALIR_RITXI.cmd
```

---

## 4. Flujo de arranque

### 4.1 Instalar modelos

```text
0_INSTALAR_MODELOS_OLLAMA.cmd
```

Instala o prepara modelos Ollama:

```text
qwen3:0.6b
gemma3:1b
llama3.2:1b
llama3.2:3b
```

### 4.2 Instalar proyecto

```text
1_INSTALAR_RITXI.cmd
```

Crea entorno `.venv` e instala dependencias de Python.

### 4.3 Iniciar daemon

```text
2_INICIAR_DAEMON_RITXI.cmd
```

Arranca Reachy Mini daemon / MuJoCo.

### 4.4 Iniciar panel

```text
3_RUN_RITXI.cmd
```

Arranca FastAPI y abre el panel web.

### 4.5 Cerrar

```text
4_SALIR_RITXI.cmd
```

Cierra procesos asociados.

---

## 5. Flujo de conversación por texto

```text
Usuario escribe mensaje
        ↓
app/static/app.js · sendTurn()
        ↓
POST /api/chat
        ↓
app/main.py
        ↓
OllamaProvider
        ↓
Ollama local
        ↓
Respuesta generada
        ↓
app.js muestra respuesta y la reproduce con TTS navegador
```

Función clave en frontend:

```text
sendTurn()
```

Endpoint clave:

```text
POST /api/chat
```

---

## 6. Flujo de conversación por voz

```text
Usuario pulsa Activar micro
        ↓
app.js abre getUserMedia()
        ↓
VAD detecta voz
        ↓
finishPersistentUtterance()
        ↓
se genera WAV
        ↓
POST /api/audio/transcribe_file
        ↓
local_whisper.py
        ↓
texto transcrito
        ↓
sendTurn()
        ↓
Ollama responde
```

Funciones clave:

```text
startAlwaysOnMic()
handlePersistentAudioProcess()
finishPersistentUtterance()
transcribeBlobWithServer()
sendTurn()
```

---

## 7. Tipos de actividades STT

Hay dos tipos principales de actividades.

### 7.1 Actividades cerradas

Esperan una palabra o conjunto pequeño de respuestas.

Ejemplos:

```text
animal_corto        → animal
animal_perro        → animal
si_corto            → yes_no
no_corto            → yes_no
sinonimos           → short
opuestos            → short
buscar_palabra      → short
```

Estas actividades pueden usar vocabulario guiado para corregir errores de Whisper.

### 7.2 Actividades abiertas

No deben usar listas cerradas porque la respuesta puede ser natural.

Ejemplos:

```text
preguntar_nombre    → open_name
presentacion        → open_text
escuchar            → open_text
vamos_hablar        → open_text
frase_corta         → open_text
historia_turnos     → open_text
cuento_interactivo  → open_text
validar_emocion     → open_text
pedir_descanso      → open_text
```

Para estas actividades, `app.js` evita enviar un `vocabulary_hint` cerrado al backend.

---

## 8. Flujo de acciones y tarjetas

Las tarjetas se definen en `app/static/app.js`.

Grupos principales:

```text
ACTION_GROUPS
SHORT_ACTIVITY_GROUPS
DIRECT_ACTION_GROUPS
GAME_ACTION_GROUPS
TUTOR_ACTION_GROUPS
```

Cada tarjeta puede tener:

```text
id
title
icon
emotion
text
subtitle
recordedAudio
sound
steps
vocabularyHint
```

Flujo al pulsar una tarjeta:

```text
click en tarjeta
        ↓
executeAction(item)
        ↓
acción robot / voz / audio / pasos
        ↓
si requiere respuesta:
    promptUserAfterActivity()
        ↓
    micro activo o texto
```

Función clave:

```text
executeAction()
```

---

## 9. Ciclo con turnos

En versiones recientes se elimina el ciclo automático para evitar confusión.

El ciclo con turnos funciona así:

```text
Ritxi ejecuta actividad corta
        ↓
Ritxi espera respuesta del usuario
        ↓
usuario habla o pulsa Siguiente
        ↓
Ritxi pasa a la siguiente actividad
```

Funciones principales:

```text
runShortCycle()
waitForNextShortCycle()
stopShortCycle()
```

---

## 10. Pestañas principales del panel

### 10.1 Emociones

Contiene gestos, emociones y movimientos expresivos.

### 10.2 Actividades

Contiene actividades de comunicación, lenguaje y habilidades sociales.

### 10.3 Juegos / canciones / bailes

Contiene:

```text
bailes
ritmo
palmas
animales
sonidos
cuentos
chistes
imitación
```

### 10.4 Tutor / apoyo

Contiene:

```text
regulación
apoyo emocional
pedir ayuda
pedir descanso
semáforo emocional
frase segura
refuerzo positivo
```

### 10.5 Configuración

Permite editar archivos importantes:

```text
app/prompts/system_prompt.txt
app/core/config.py
app/config/model_presets.json
profiles/characters/ritxi_tutor_comunicacion_di.json
.env.example
app/config/stt_vocabularies/*.json
```

---

## 11. Endpoints principales

Los endpoints se definen en:

```text
app/main.py
```

Endpoints típicos:

```text
GET  /
GET  /api/status
POST /api/chat
POST /api/audio/transcribe_file
POST /api/audio/warmup_whisper
POST /api/robot/action
POST /api/config/file
GET  /api/config/files
GET  /api/config/file
POST /api/exit_all
```

---

## 12. Comunicación entre módulos

```text
app.js
  ├─ /api/chat --------------------> main.py -> OllamaProvider -> Ollama
  ├─ /api/audio/transcribe_file ----> main.py -> local_whisper.py
  ├─ /api/robot/action -------------> main.py -> ActionScheduler -> ReachySDK
  ├─ /api/status -------------------> main.py -> Runtime state
  └─ /api/config/file --------------> main.py -> archivos del proyecto
```

---

## 13. Archivos de configuración importantes

### `app/core/config.py`

Constantes y variables de entorno:

```text
modelo LLM
timeouts
tokens
proveedores activos
STT
TTS
robot
```

### `app/prompts/system_prompt.txt`

Instrucciones generales del comportamiento de Ritxi.

### `app/config/model_presets.json`

Modelos disponibles para el selector de Ollama.

### `profiles/characters/*.json`

Perfiles de carácter.

### `app/config/stt_vocabularies/*.json`

Grupos de palabras esperadas por actividad.

---

## 14. Logs

Los logs se guardan en:

```text
logs/
```

Tipos de logs habituales:

```text
session_*.jsonl
session_*.log
reachy_daemon_*.log
lanzador_*.log
```

Se usan para diagnosticar:

```text
fallos STT
fallos Ollama
estado de micrófono
movimientos del robot
errores de daemon
bloqueos de interfaz
```

---

## 15. Puntos delicados del código

### 15.1 STT y vocabulario cerrado

No se debe aplicar `yes_no`, `animal` o `short` a preguntas abiertas.

Ejemplo incorrecto:

```text
Pregunta: ¿Cómo te llamas?
Usuario: Me llamo Juanita
vocabulary_hint: yes_no
Resultado: texto rechazado
```

Solución:

```text
preguntar_nombre → open_name
conversación natural → open_text
```

### 15.2 Movimiento del robot

No enviar movimientos simultáneos al daemon.

El código debe evitar:

```text
play_move() activo
        +
set_body_yaw()
        +
neutral()
```

porque puede provocar errores de movimiento o colisión.

### 15.3 Caché del navegador

Cada versión cambia:

```text
/static/app.js?v=...
/static/styles.css?v=...
```

Si la interfaz parece antigua, recargar con caché limpia.

---

## 16. Funciones principales comentadas

En esta versión se han añadido comentarios en:

```text
app/main.py
app/static/app.js
app/audio/local_whisper.py
app/llm/ollama_provider.py
app/orchestration/action_scheduler.py
app/robot/reachy_sdk.py
app/core/config.py
```

Y en `app.js`, especialmente alrededor de:

```text
sendTurn()
startAlwaysOnMic()
finishPersistentUtterance()
vocabularyHintForActivity()
renderActionGroups()
executeAction()
runShortCycle()
setModulePreset()
playOfficialRecordedAudio()
transcribeBlobWithServer()
```

---

## 17. Resumen rápido para mantenimiento

Si algo falla:

1. Revisar primero `logs/session_*.jsonl`.
2. Confirmar versión cargada de `app.js`.
3. Ver si el error es:
   - STT;
   - Ollama;
   - robot/daemon;
   - interfaz/cache.
4. Verificar si la actividad usa vocabulario abierto o cerrado.
5. Probar en modo `Solo texto` para separar IA de robot/micro.
6. Probar en modo `Voz + robot` para separar robot/audio de Ollama.
7. Probar `Tutor completo` cuando todo esté estable.
