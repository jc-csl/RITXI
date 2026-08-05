# Pruebas funcionales de Ahootsa 0.12.8.6

## Prueba A — Persona sin intereses

1. Crear o seleccionar una persona sin contenido en `Intereses`.
2. Elegir actividad y nivel.
3. Pulsar `Preparar`.
4. Revisar `ahootsa_session/greeting.txt`.
5. Iniciar la conversación.

Resultado: Aocha dice el nombre y utiliza el saludo de la actividad.

## Prueba B — Persona con intereses

1. Editar `Intereses`, por ejemplo: `sudokus y música`.
2. Guardar.
3. Preparar una sesión nueva.
4. Iniciar la conversación.

Resultado esperado aproximado:

```text
Hola, Ana. Soy Aocha. Entre las cosas que te gustan tengo anotado:
sudokus y música. ¿Te apetece hablar de eso o prefieres empezar con
expresar preferencias?
```

## Prueba C — Final de Thriller

1. Pedir el baile Thriller.
2. No hablar durante el baile.
3. Esperar a que terminen movimiento y música.

Resultado:

- movimiento y audio se detienen;
- el micrófono sigue disponible;
- Aocha habla automáticamente;
- formula una sola pregunta sencilla.

El log debe contener:

```text
Ahootsa local dance completed and auto-stopped
"status": "completed"
```
