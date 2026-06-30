# Cambios v0.4.35 - Official Emotions Library

Esta versión elimina la capa de sonidos WAV inventados de v0.4.35 y vuelve a la librería oficial:

`pollen-robotics/reachy-mini-emotions-library`

La librería oficial tiene pares:

- `nombre.json`: movimiento grabado del robot.
- `nombre.ogg`: audio oficial asociado.

Cambios principales:

- Nueva herramienta `play_official_performance`.
- `celebrate_user` usa actuaciones oficiales JSON+OGG.
- `sing_song` puede acompañar canciones originales con actuaciones oficiales.
- `show_performance_library` muestra diagnóstico de la librería oficial.
- Script `06_comprobar_libreria_oficial_emociones.ps1` para verificar `dance1.ogg`, `success1.ogg`, pares JSON/OGG y versión de `reachy-mini`.
- El instalador intenta actualizar `reachy-mini` a `>=1.8.4`, necesario para la librería oficial comprimida con movimiento 50 Hz y audio OGG/Opus.

Pruebas recomendadas:

- `baila`
- `baila con música`
- `celebra que lo he hecho bien`
- `saluda con sonido`
- `qué emociones y bailes oficiales puedes hacer`
