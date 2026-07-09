# 06 — Configuración, perfiles y variables

## 1. Perfil principal

Nombre del perfil Ahootsa:

```text
ahootsa_realtime_es
```

Rutas donde puede existir:

```text
src/ahootsa_realtime_ollama_desktop_app/profiles/ahootsa_realtime_es
%LOCALAPPDATA%\Reachy Mini Control\user_personalities\ahootsa_realtime_es
apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es
apps_venv\Lib\site-packages\reachy_talk_data\profiles\ahootsa_realtime_es
apps_venv\Lib\site-packages\ahootsa_realtime_ollama_desktop_app\profiles\ahootsa_realtime_es
```

## 2. Archivos principales del perfil

```text
instructions.txt  -> prompt, personalidad, reglas, uso de herramientas
tools.txt         -> lista de herramientas disponibles para el modelo
greeting.txt      -> instrucción de saludo inicial
voice.txt         -> voz preferida
```

## 3. `instructions.txt`

Debe definir:

```text
- nombre Ahootsa
- idioma castellano
- tono paciente, positivo y claro
- instrucciones para personas usuarias
- cuándo usar ask_ollama
- cómo guiar actividades
- cómo evitar llamar herramientas duplicadas
- cómo responder en Memory
```

Regla importante:

```text
No usar ask_ollama salvo que el usuario pida específicamente IA local, Ollama o consultar el modelo local.
```

## 4. `tools.txt`

Activa herramientas que el backend realtime puede invocar. Ejemplos:

```text
ask_ollama
start_memory_pairs_game
choose_memory_cards
play_emotion
play_panel_dance_activity
camera
remember
forget
move_head
dance
stop_dance
```

Cuantas más herramientas se exponen, más compleja puede ser la decisión del modelo. Para fluidez conviene no exponer herramientas innecesarias.

## 5. Variables de perfil e identidad

```text
REACHY_MINI_CUSTOM_PROFILE=ahootsa_realtime_es
REACHY_MINI_PROFILE=ahootsa_realtime_es
REACHY_MINI_PERSONALITY=ahootsa_realtime_es
REACHY_MINI_USER_PERSONALITY=ahootsa_realtime_es
AHOOTSA_NAME=Ahootsa
ASSISTANT_NAME=Ahootsa
ROBOT_NAME=Ahootsa
PROJECT_NAME=Ahootsa
```

## 6. Variables de idioma

```text
AHOOTSA_LANGUAGE=es
REACHY_MINI_LANGUAGE=es
APP_LANGUAGE=es
OUTPUT_LANGUAGE=es
SYSTEM_LANGUAGE=es
REALTIME_TRANSCRIPTION_LANGUAGE=es
TRANSCRIPTION_LANGUAGE=es
```

## 7. Variables de voz

```text
AHOOTSA_VOICE=Sohee
VOICE=Sohee
REACHY_MINI_VOICE=Sohee
OPENAI_REALTIME_VOICE=Sohee
REALTIME_VOICE=Sohee
TTS_VOICE=Sohee
AUDIO_VOICE=Sohee
```

Aunque el backend oficial sea Hugging Face, algunas variables conservan nombres históricos como `OPENAI_REALTIME_VOICE` porque la comunicación realtime es compatible con estructuras tipo OpenAI.

## 8. Variables Hugging Face

```text
HF_REALTIME_CONNECTION_MODE=deployed
HF_REALTIME_WS_URL=ws://127.0.0.1:8765/v1/realtime
HF_TOKEN=...
```

Interpretación:

```text
deployed -> usa backend Hugging Face online integrado
local    -> usa backend local externo por WebSocket
```

La variable `HF_REALTIME_SESSION_URL` se ignora deliberadamente en la app oficial moderna; se usa el proxy interno por defecto.

## 9. Variables Ollama

```text
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:3b
AHOOTSA_OLLAMA_TIMEOUT_SECONDS=25
```

Evitar:

```text
OLLAMA_MODEL=ahootsa-local:latest
```

salvo que se haya creado ese modelo/alias en Ollama.

## 10. Variables de logs

```text
AHOOTSA_LOG_DIR=D:\RITXI\logs
AHOOTSA_SESSION_ID=YYYYMMDD_HHMMSS
AHOOTSA_LOG_FILE_SCREEN=...
AHOOTSA_LOG_FILE_EVENTS=...
AHOOTSA_LOG_FILE_RUNTIME=...
```

## 11. Variables de actividades

```text
AHOOTSA_MEMORY_REACTION_ENABLED=1
AHOOTSA_DANCES_LIBRARY_DIR=D:\RITXI\reachy-mini-dances-library
AHOOTSA_DISABLE_EMOTION_AUDIO=0
AHOOTSA_ACTION_PLAY_DELAY_SECONDS=0
AHOOTSA_POST_PLAY_WAIT_SECONDS=3.0
```

Para reducir latencia durante pruebas:

```text
AHOOTSA_POST_PLAY_WAIT_SECONDS=0.25
AHOOTSA_DISABLE_EMOTION_AUDIO=1
```

## 12. Dónde mirar si algo no se aplica

Revisar en este orden:

```text
1. Variables que imprime el lanzador.
2. .env de la carpeta Ahootsa.
3. .env de %LOCALAPPDATA%\Reachy Mini Control.
4. .env dentro de paquetes instalados.
5. profiles/default si el perfil Ahootsa no se carga.
6. tools.txt activo.
7. logs JSONL de eventos.
```
