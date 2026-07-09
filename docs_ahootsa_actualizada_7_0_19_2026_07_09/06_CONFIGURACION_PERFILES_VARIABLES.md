# 06 — Configuración, perfiles y variables

## 1. Perfil principal actual

```text
ahootsa7_realtime_es
```

Ubicación instalada esperada:

```text
apps_venv\Lib\site-packages\ahootsa_realtime_ollama_desktop_app\profiles\ahootsa7_realtime_es
```

Archivos clave:

```text
instructions.txt
 tools.txt
 greeting.txt
 voice.txt
 play_emotion.py
```

## 2. Tools del perfil

Lista actual aproximada:

```text
ask_ollama
camera_pc
explore_image
start_memory_pairs_game
choose_memory_cards
reset_memory_pairs_game
memory_pairs_game_status
list_memory_pairs_games
hint_memory_pairs_game
list_communication_activity_levels
list_communication_activities
start_communication_activity
list_emotions
play_emotion
stop_emotion
list_panel_dances_activities
play_panel_dance_activity
list_community_dances
play_community_dance
move_head
task_status
task_cancel
```

## 3. Variables relevantes

```text
REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY
REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY
HF_REALTIME_CONNECTION_MODE
HF_REALTIME_WS_URL
OLLAMA_BASE_URL
OLLAMA_MODEL
AHOOTSA_PROFILE
AHOOTSA_INSTALLED_VERSION
AHOOTSA_PHOTOS_DIR
AHOOTSA_LOGS_DIR
```

Valores habituales:

```text
AHOOTSA_PROFILE=ahootsa7_realtime_es
HF_REALTIME_CONNECTION_MODE=deployed
OLLAMA_MODEL=llama3.2:3b
AHOOTSA_PHOTOS_DIR=D:\RITXI\fotos
AHOOTSA_LOGS_DIR=D:\RITXI\logs
```

## 4. Configuración editable desde panel

Panel:

```text
http://127.0.0.1:7860/ahootsa
```

Sección:

```text
CONFIGURACIÓN DEL SISTEMA
```

Archivos habituales:

```text
profiles/ahootsa7_realtime_es/instructions.txt
profiles/ahootsa7_realtime_es/tools.txt
tools/memory_timing_config.json
tools/resources_bailes_emociones_es.json
```

## 5. Tiempo del juego Memory

Archivo:

```text
tools/memory_timing_config.json
```

Ejemplo:

```json
{
  "reveal_seconds": 8.0,
  "flip_delay_seconds": 0.0,
  "refresh_interval_ms": 700,
  "iframe_height_px": 620
}
```

`reveal_seconds` controla cuánto tiempo permanecen visibles las cartas al elegir dos.

## 6. Alias de bailes/emociones

Archivo:

```text
tools/resources_bailes_emociones_es.json
```

Debe mapear nombres naturales en español a identificadores técnicos:

```text
baile uno       → dance1
baile dos       → dance2
baile tres      → dance3
saludo          → welcoming2
celebración     → success1
calma           → calming1
eléctrico       → electric1
play / olay     → dance1
play dos        → dance2
olay tres       → dance3
```

Las versiones recientes también reparan textos mal codificados como:

```text
elÃ©ctrico
celebraciÃ³n
nÃºmero
```
