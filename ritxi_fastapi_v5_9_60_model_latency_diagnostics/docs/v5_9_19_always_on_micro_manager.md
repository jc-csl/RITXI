# v5.9.19 · Gestor de micro continuo

Cambio de enfoque:
- Se abandona la lógica de capturas sueltas de micro.
- El micro se mantiene abierto en conversación/actividades con turno.
- Se pausa mientras Ritxi habla.
- Se reanuda automáticamente cuando Ritxi termina.
- `Parar micro` es el único botón para anular el micro.
- Al seleccionar una acción sin turno, el micro se desconecta.
- Al seleccionar actividad con turno, se activa el micro continuo.

Objetivo:
- Evitar bloqueos en `Abriendo micro...`.
- Evitar tener que reabrir getUserMedia cada turno.
- Mejorar juegos como animales, opuestos, sinónimos y pedir ayuda.
