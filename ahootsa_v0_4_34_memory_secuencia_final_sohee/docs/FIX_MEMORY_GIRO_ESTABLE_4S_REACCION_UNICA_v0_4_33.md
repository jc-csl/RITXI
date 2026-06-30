# v0.4.34 — Giro estable 4 segundos y reacción única

## Problemas corregidos

```text
- Las cartas falladas parpadeaban.
- No daba tiempo a verlas bien.
- El robot podía reaccionar dos veces ante el mismo fallo.
```

## Corrección

```text
- Las cartas falladas permanecen visibles 4 segundos.
- Se elimina la animación de parpadeo/sacudida.
- El frontend no reconstruye las cartas si el estado visual no cambia.
- El servidor detecta repetición de la misma pareja fallada mientras está visible.
- choose_memory_cards no lanza una segunda emoción para el mismo movimiento.
```

## Resultado esperado

```text
1. Usuario dice: 1 y 5.
2. Se giran las dos cartas.
3. Si no son pareja, quedan quietas y visibles 4 segundos.
4. El robot anima una sola vez.
5. Después se ocultan solas.
```
