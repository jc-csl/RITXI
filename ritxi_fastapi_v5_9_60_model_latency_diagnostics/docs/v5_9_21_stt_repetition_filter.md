# v5.9.21 · Filtro de repeticiones STT

Problema:
- Whisper puede generar bucles como:
  `la idea de que es la idea de que es...`
- Esto suele ocurrir con silencio, eco, ruido o audio largo con poca voz clara.

Cambios:
- Filtro backend en `local_whisper.py`.
- Filtro frontend antes de enviar a Ollama.
- Si se detecta repetición automática:
  - se descarta la transcripción;
  - no se envía a Ollama;
  - se muestra mensaje para repetir o escribir.
