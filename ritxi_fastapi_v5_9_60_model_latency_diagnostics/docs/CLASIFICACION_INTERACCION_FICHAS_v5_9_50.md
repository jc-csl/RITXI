# Clasificación visual de fichas · v5.9.50

## Niveles

| Nivel | Barra | Significado |
|---|---|---|
| Solo reproduce | Gris | Ritxi ejecuta audio/movimiento/texto sin esperar respuesta. |
| Interacción corta | Azul | Ritxi espera una respuesta breve y cierra la actividad. |
| Interacción larga | Morada | Ritxi puede mantener una conversación algo más larga, pero con objetivo concreto. |
| Máxima interacción | Dorada | Ritxi mantiene contexto creativo hasta que el usuario decida terminar. |

## Máxima interacción

Estas actividades se marcan como máxima interacción:

- `historia_turnos` · Historia por turnos
- `cuento_interactivo` · Cuento por turnos
- `final_historia` · Inventar final
- `explicar_imagen` · Describir imagen
- `elegir_emocion` · Elegir emoción

En estas actividades:
- no se usa respuesta local repetitiva;
- se mantiene el contexto;
- Ollama recibe instrucciones para continuar la misma actividad;
- el micro/texto vuelve a quedar disponible tras cada turno;
- la actividad se cierra si el usuario dice terminar, fin, parar, cambiar u otra actividad.
