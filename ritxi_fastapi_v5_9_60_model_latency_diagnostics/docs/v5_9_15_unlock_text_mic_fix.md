# v5.9.15 · Desbloqueo de texto y micro

Problema:
- Tras una respuesta de Ritxi o una acción anterior, la interfaz podía quedar con `realtimeSending` o `browserSpeaking` enganchado.
- Entonces `Enviar` no hacía nada y `Activar conversación / micro` tampoco recuperaba el turno.

Cambios:
- Nuevo `forceUnlockTurnState()`.
- `Enviar texto` desbloquea el estado si detecta que hay un bloqueo previo.
- `Hablar ahora / activar micro` desbloquea y abre el micro directamente.
- `Reset` también limpia estados cliente, no solo reinicia la sesión.
- `app.js` se sirve con `?v=5.9.15` para evitar caché del navegador.
