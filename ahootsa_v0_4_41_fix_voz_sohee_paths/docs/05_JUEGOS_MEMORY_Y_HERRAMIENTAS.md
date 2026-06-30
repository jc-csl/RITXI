# 05 — Juegos Memory y herramientas

## Juegos incluidos

```text
animales
ciudades
alimentos
```

Cada juego tiene:

```text
4 parejas
8 cartas
dorso azul
número blanco grande
```

## Herramientas principales

### `start_memory_pairs_game`

Abre el juego en:

```text
http://localhost:7870/
```

Ejemplos de intención:

```text
quiero el juego de animales
quiero el juego de ciudades
quiero el juego de alimentos
```

### `choose_memory_cards`

Levanta dos cartas.

Ejemplo:

```text
uno y siete
```

Secuencia deseada:

```text
1. Reachy dice: "Vamos a ver la uno y la siete".
2. La herramienta espera.
3. Se giran las cartas.
4. La herramienta espera.
5. Reachy reacciona una sola vez.
```

### `hint_memory_pairs_game`

Da una pista.

Ejemplos:

```text
dame una pista
ayuda
no sé
estoy atascado
```

### `reset_memory_pairs_game`

Reinicia el juego.

### `memory_pairs_game_status`

Consulta estado interno del juego.

### `list_memory_pairs_games`

Lista juegos disponibles.

## Final de partida

Cuando se encuentran todas las parejas:

```text
- Reachy felicita.
- Espera unos segundos.
- El juego se reinicia.
- Pregunta si se quiere jugar otra vez o realizar otra actividad.
```

## Archivos implicados

```text
memory_pairs_game_server.py
start_memory_pairs_game.py
choose_memory_cards.py
hint_memory_pairs_game.py
reset_memory_pairs_game.py
memory_pairs_game_status.py
list_memory_pairs_games.py
memory_pairs_generic.html
animales.json
ciudades.json
alimentos.json
```


## Bailes y actividades del panel

```text
list_panel_dances_activities
play_panel_dance_activity
```
