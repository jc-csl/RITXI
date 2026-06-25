# v5.9.20 · Micro directo sin bloqueo por echo_guard

Revisión profunda:
- El micro ya no depende de `canListenNow()` ni de `echo_guard` del backend para abrirse.
- La apertura del micro se controla localmente en el navegador.
- El micro solo se pausa por estados locales:
  - Ritxi hablando (`browserSpeaking`);
  - transcripción en curso;
  - envío a Ollama en curso.
- Las actividades con turno abren el micro directamente.
- Al terminar la voz de Ritxi, se reanuda o abre el micro directamente.
- Se baja el umbral VAD a `0.015`.
- Se aumenta la grabación máxima a `5000 ms` para no cortar palabras.
