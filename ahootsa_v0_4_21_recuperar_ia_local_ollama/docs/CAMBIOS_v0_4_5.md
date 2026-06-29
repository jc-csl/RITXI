# Cambios v0.4.6 - Safe Local Emotions Motion

- Corrige el error `HFValidationError` al pasar `D:\RITXI\reachy-mini-emotions-library` a `RecordedMoves`.
- Añade un shim local para que `RecordedMoves` resuelva el dataset oficial a la carpeta descargada.
- Reproduce el audio `.ogg` local asociado mediante `reachy_mini.media.play_sound()`.
- Mantiene el movimiento desde el `.json` oficial y el audio desde el `.ogg` oficial.
- Añade pruebas `07_probar_libreria_local_con_python.ps1` y `10_probar_audio_ogg_con_reachy.ps1`.
