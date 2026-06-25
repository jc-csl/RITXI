# v5.9.14 · Botón Hablar ahora

Problema:
- Si el usuario perdía el turno o Ritxi no entendía la voz, el botón principal no abría claramente el micro.

Cambio:
- El botón pasa a comportarse como `Hablar ahora`.
- Si el micro no está escuchando, al pulsar intenta abrirlo inmediatamente.
- Si el micro ya está escuchando, al pulsar lo para.
- Si no se entiende la voz, se mantiene el turno recuperable y el botón vuelve a quedar disponible.
