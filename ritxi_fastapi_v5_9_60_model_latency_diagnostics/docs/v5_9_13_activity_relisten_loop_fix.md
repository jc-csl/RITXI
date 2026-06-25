# v5.9.13 · Reescucha en juegos de turnos

Problema corregido:
- En juegos/actividades con turnos, el micro se abría solo una vez.
- Después de que Ritxi contestaba con voz, no se reabría para el usuario.

Cambios:
- Se añade `activityAutoListenAfterBot`.
- Los turnos provenientes de actividades reabren el micro después de la respuesta de Ritxi.
- El ciclo con turnos espera a que termine la respuesta de Ritxi, no solo a que el usuario haya hablado.
- `Detener` y `Reset` desactivan este modo para que no quede escuchando.
