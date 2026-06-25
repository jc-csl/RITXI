# Prueba de conversación en tiempo real — Ritxi FastAPI v3

Esta prueba está pensada para validar a fondo el ciclo:

```text
micro PC → texto navegador → FastAPI → Ollama → TTS PC → movimiento Reachy simulado → cooldown → volver a escuchar
```

## 1. Preparación

Instala una vez con `uv`:

```powershell
cd D:\ritxi_fastapi_v3
scripts\setup_uv_windows.bat
```

Comprueba Ollama:

```powershell
ollama pull gemma3:1b
ollama pull qwen3:0.6b
ollama pull llama3.2:3b
ollama list
```

## 2. Modo completo: Reachy daemon simulado + Ollama + audio/micro PC

Terminal 1:

```powershell
cd D:\ritxi_fastapi_v3
scripts\run_reachy_sim_daemon.bat
```

Terminal 2:

```powershell
cd D:\ritxi_fastapi_v3
scripts\run_realtime_lab_ollama_windows.bat
```

Abre en Chrome o Edge:

```text
http://127.0.0.1:8080
```

En el panel, pulsa **Tiempo real completo** y después **Activar conversación tiempo real**.

## 3. Modo mock rápido

Sirve para comprobar panel, TTS, scheduler y echo guard sin Ollama ni daemon.

```powershell
cd D:\ritxi_fastapi_v3
scripts\run_realtime_lab_mock_windows.bat
```

## 4. Modo latencia mínima

Sirve para medir principalmente Ollama y el flujo de turno, sin TTS ni movimiento por defecto.

```powershell
cd D:\ritxi_fastapi_v3
scripts\run_realtime_lab_low_latency_windows.bat
```

En el panel, usa **Medir latencia 5 turnos**.

## 5. Qué probar

### Preset: Tiempo real completo

Activa:

- entrada micro;
- salida texto;
- salida audio / TTS;
- movimientos robot;
- etiquetas emoción;
- streaming;
- sincronizar turno;
- debug.

Es el modo más parecido a conversación natural.

### Preset: Latencia mínima

Desactiva audio, movimientos y emociones. Mantiene streaming. Sirve para ver el coste real de LLM.

### Preset: Robot expresivo

Activa voz, movimiento y emociones. Sirve para revisar sincronización entre TTS y gestos.

### Preset: Stress cola

Desactiva sincronización de turno. Sirve para ver si se acumulan acciones en la cola.

### Preset: Solo texto/debug

Prueba prompts y etiquetas de emoción sin tocar audio ni robot.

## 6. Métricas importantes

En el panel mira:

- `llm_first_token_ms`: primera respuesta del modelo;
- `llm_total_ms`: generación completa;
- `turn_total_ms`: turno completo incluyendo salida;
- `scheduler.queue_size`: cola pendiente;
- `scheduler.busy`: robot/TTS ocupados;
- `echo_guard.microphone_enabled`: si el micro puede volver a escuchar;
- `tts.speaking`: si el TTS está hablando.

## 7. Problemas frecuentes

### El navegador no escucha

Usa Chrome o Edge. El botón de micro usa Web Speech API del navegador.

### Ritxi se escucha a sí mismo

Aumenta en el script:

```bat
set RITXI_ECHO_COOLDOWN_S=1.3
```

### Mucha latencia

Prueba:

```bat
set RITXI_LLM_MAX_TOKENS=80
set RITXI_LLM_TEMPERATURE=0.2
```

También puedes activar el preset **Latencia mínima** para aislar el problema.

### Se acumulan acciones

Mira `scheduler.queue_size`. Si sube mucho, activa **Sincronizar turno** o desactiva `idle`.

## 8. Recomendación de prueba completa

1. Arranca modo completo.
2. Pulsa **Tiempo real completo**.
3. Pulsa **Activar conversación tiempo real**.
4. Haz frases cortas: “Hola Ritxi”, “¿Qué puedes hacer?”, “Haz una pregunta sencilla”.
5. Ejecuta **Medir latencia 5 turnos**.
6. Ejecuta **Probar emociones**.
7. Activa/desactiva TTS, movimientos y streaming para comparar.
