# 05 — Flujos de comunicación y puertos

## 1. Flujo de arranque

```text
LANZAR_AHOOTSA_5_0_xx.ps1
  ↓
localiza apps_venv
  ↓
comprueba Python, MuJoCo y Ollama
  ↓
aplica instalación/parche Ahootsa
  ↓
arranca reachy-mini-daemon.exe
  ↓
espera http://127.0.0.1:8000/api/daemon/status
  ↓
POST /api/apps/start-app/ahootsa_realtime_ollama_app
  ↓
espera http://127.0.0.1:7860/status
  ↓
abre interfaz web
```

## 2. Puertos

```text
8000  reachy-mini-daemon.exe
7860  app web Ahootsa
7870  juego Memory, según versión
11434 Ollama local
8765  backend Hugging Face realtime local, si existe
```

## 3. Flujo de conversación principal

```text
Usuario habla o escribe
  ↓
Interfaz Ahootsa
  ↓
reachy_mini_conversation_app.main.run()
  ↓
Hugging Face Realtime
  ↓
respuesta de audio/texto/herramienta
  ↓
Ahootsa / robot / interfaz
```

En modo deployed:

```text
Ahootsa -> HF session proxy online -> backend realtime remoto
```

En modo local:

```text
Ahootsa -> ws://127.0.0.1:8765/v1/realtime -> backend local
```

## 4. Flujo de Ollama auxiliar

```text
Usuario pide IA local / Ollama
  ↓
modelo principal decide usar herramienta ask_ollama
  o el frontend llama a /ollama/ask
  ↓
Ahootsa envía prompt a http://127.0.0.1:11434/api/generate
  ↓
Ollama ejecuta llama3.2:3b
  ↓
respuesta vuelve a Ahootsa
```

Endpoints que se han añadido para compatibilidad en versiones recientes:

```text
/ollama/status
/ollama/models
/ollama/ask
/ask_ollama
/ask-ollama
/api/ollama/ask
/api/ask_ollama
/api/local-ai/ask
/local-ai/ask
/llm/ask
/ask
/chat
```

## 5. Flujo de Memory

```text
Usuario pide juego de parejas
  ↓
start_memory_pairs_game
  ↓
servidor Memory en puerto 7870
  ↓
interfaz del juego
  ↓
usuario elige dos cartas
  ↓
choose_memory_cards
  ↓
resultado match/miss/duplicate
  ↓
feedback hablado y/o emoción
```

En los logs aparecen eventos como:

```text
tool_start: start_memory_pairs_game
memory_reset
tool_start: choose_memory_cards
memory_choose_result
tool_result
```

## 6. Flujo de movimiento/emoción

```text
Usuario pide baile/emoción
  ↓
herramienta play_panel_dance_activity o play_emotion
  ↓
cola de movimiento / EmotionQueueMove
  ↓
Reachy Mini real o MuJoCo
```

Si el audio de la emoción falla por `pygame`, el movimiento puede seguir funcionando aunque no suene el `.ogg`.

## 7. Flujo de cámara oficial

```text
herramienta oficial camera
  ↓
deps.reachy_mini.media.get_frame()
  ↓
frame desde cámara Reachy/MuJoCo
  ↓
backend realtime analiza o usa imagen
```

Esta cámara no es necesariamente la webcam del portátil.

## 8. Flujo de cámara PC

```text
Usuario abre /camera/page
  ↓
navegador solicita permiso de webcam
  ↓
getUserMedia({video:true,audio:false})
  ↓
canvas captura imagen
  ↓
POST /camera/upload
  ↓
D:\RITXI\logs\camera
```

## 9. Flujo de logs

```text
pantalla.log  -> salida PowerShell visible
runtime.log   -> daemon y llamadas internas
eventos.jsonl -> eventos estructurados por sesión
camera/       -> capturas de cámara PC
```

Cada ejecución debe crear su propio timestamp:

```text
ahootsa5_YYYYMMDD_HHMMSS_pantalla.log
ahootsa5_YYYYMMDD_HHMMSS_runtime.log
ahootsa5_YYYYMMDD_HHMMSS_eventos.jsonl
```
