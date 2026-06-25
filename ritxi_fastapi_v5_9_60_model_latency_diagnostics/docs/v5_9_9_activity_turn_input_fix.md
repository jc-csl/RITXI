# v5.9.9 · Entrada en actividades

- `promptUserAfterActivity`: activa turno de usuario tras una actividad corta.
- El micro se intenta abrir automáticamente cuando el estado lo permite.
- Si el micro no se abre, se indica escribir en el chat y pulsar enviar.
- En ciclo con turnos se espera a:
  - respuesta enviada al chat;
  - botón `Siguiente`;
  - timeout.
