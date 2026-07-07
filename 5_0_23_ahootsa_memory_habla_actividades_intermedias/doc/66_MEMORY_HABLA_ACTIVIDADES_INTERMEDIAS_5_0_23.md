# Ahootsa 5.0.23 — Memory hablado y actividades intermedias

Cambios principales:

- El Memory ya no debe quedarse solo en efectos.
- `choose_memory_cards` ahora marca `needs_response=True`.
- La reacción de Memory se ejecuta primero y después se devuelve `robot_say` para que Ahootsa hable.
- El texto de cada jugada confirma acierto o fallo y vuelve a pedir dos números del 1 al 8.
- Al finalizar se usa `dance3` como celebración y se pregunta si quiere volver a jugar o salir.
- La ventana visual de Memory incluye fallback de voz del navegador y recordatorio cada 10 segundos.
- Las actividades de comunicación se ofrecen como: fácil, intermedia y avanzada.
- Se evita llamar "normal" al nivel intermedio en mensajes visibles.

Prueba sugerida:

1. Iniciar Ahootsa 5.0.23.
2. Pedir: "Quiero jugar al memory de animales".
3. Decir dos números.
4. Verificar que hay efecto y después frase hablada.
5. Esperar 10 segundos sin hacer nada: debe recordar que hay que elegir dos números del 1 al 8.
6. Completar el juego: debe bailar `dance3` y preguntar si quiere volver a jugar o salir.
