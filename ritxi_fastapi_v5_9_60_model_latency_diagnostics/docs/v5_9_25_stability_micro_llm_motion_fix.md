# v5.9.25 · Estabilidad: micro, STT, Ollama, movimiento y audio HF

Correcciones aplicadas a partir de los logs del 2026-06-24:

## Micro / STT
- Se sube el umbral de voz:
  - `serverVadThreshold=0.028`
- Se reduce la grabación máxima:
  - `serverRecordMaxMs=3500`
- Se aumenta la pausa de silencio:
  - `silenceSendMs=850`
- Se añade ruido de fondo dinámico en el micro continuo.
- Se descartan capturas antes de Whisper si la señal es demasiado baja.
- Se endurece el filtro de repeticiones tipo:
  - `la idea de que es la idea de que es...`
  - `los que los que los que...`

## Vocabulario guiado
- `yes_no` deja de extraer `sí/no` desde frases largas.
- Si la respuesta de sí/no tiene más de 4 palabras, se rechaza y se pide repetir.
- Animal/short solo corrigen frases cortas.

## Ollama
- Menos tokens y contexto para bajar latencia:
  - `RITXI_LLM_MAX_TOKENS=45`
  - `RITXI_LLM_TIMEOUT_S=18`
  - `RITXI_OLLAMA_NUM_CTX=768`
  - `top_k=20`
  - `top_p=0.85`
  - `repeat_penalty=1.15`
- Defaults de configuración ajustados:
  - `llm_temperature=0.25`
  - `max_history_messages=6`
  - `stt_whisper_model_size=tiny`

## Movimiento Reachy
- Se añade espera antisolape en frontend.
- El backend espera tras `robot.play_move(move)` para no mandar neutral/poses durante movimientos oficiales.
- `ActionScheduler` deja de lanzar movimiento y TTS en paralelo en acciones normales.
- El retorno a neutral espera una pequeña pausa.

## Audio oficial Hugging Face
- El backend ya no intenta inicializar audio oficial.
- El audio oficial se reproduce desde navegador con `/api/audio/recorded/...`.
- Esto evita errores de tipo `Audio system is not initialized`.

## Versión
- Cache bust:
  - `/static/app.js?v=5.9.25`
