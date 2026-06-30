# Cambios v0.4.35 - Safe Local Emotions Motion

- Se desactiva cualquier llamada automática a `reachy_mini.media.play_sound()`.
- Motivo: en la prueba real apareció `No Reachy Mini Audio USB device found` y GStreamer/pygobject terminó con crash.
- Se restaura el movimiento local usando `D:\RITXI
eachy-mini-emotions-library` y el shim de `RecordedMoves`.
- La herramienta `play_official_performance` ahora mueve con el JSON local y devuelve la ruta del OGG como diagnóstico.
- El script 10 ya no reproduce audio: solo comprueba que el OGG existe y explica por qué no se llama a media.
