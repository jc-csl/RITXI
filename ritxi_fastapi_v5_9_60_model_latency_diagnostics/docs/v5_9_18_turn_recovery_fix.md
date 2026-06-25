# v5.9.18 · Recuperación fuerte de turnos

Problema:
- En actividades como Opuestos, la app podía quedarse en `Abriendo micro...`.
- Después no respondía ni `Hablar ahora` ni `Enviar texto`.

Cambios:
- `Hablar ahora` ya no actúa como toggle: siempre cancela captura anterior y abre una nueva.
- `Parar micro` queda como único botón para parar.
- `Enviar texto` cancela cualquier STT/micro pendiente antes de enviar a Ollama.
- Nuevo `hardStopMicCapture()`.
- `app.js?v=5.9.18` para evitar caché.
