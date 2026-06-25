# v5.9.2 · Voz más precisa y respuestas más rápidas

Cambios aplicados:

## STT / micro
- `serverRecordMaxMs`: 7000 ms → 4500 ms
- `serverVadThreshold`: 0.018 → 0.035
- `silenceSendMs`: 1400 ms → 900 ms
- `relistenDelayMs`: 1000 ms → 700 ms
- Whisper local por defecto: `tiny` + `int8`

Objetivo:
- ignorar más ruido ambiental;
- evitar transcripciones vacías o palabras inventadas;
- cerrar antes el turno de voz;
- responder antes.

## Ollama / LLM
- `RITXI_LLM_MAX_TOKENS=55`
- `RITXI_LLM_TIMEOUT_S=25`
- `RITXI_OLLAMA_NUM_CTX=1024`
- temperatura visual por defecto: 0.25

Objetivo:
- respuestas más cortas;
- menos espera;
- menos divagación;
- más estabilidad como tutor.
