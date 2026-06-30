# v0.4.34 — Fix visual de cartas

Se corrige el problema por el que las cartas salían casi blancas o vacías.

## Resultado esperado

- dorso azul visible
- número blanco grande visible
- cartas grandes
- 4 parejas / 8 cartas
- si fallas, las cartas se mantienen 4 segundos

## Causa del problema

El HTML usaba elementos inline en la estructura 3D de la carta y el navegador no estaba renderizando bien el tamaño de las caras.

## Corrección aplicada

- estructura interna cambiada a `div`
- refuerzo de estilos `display:block` / `display:grid`
- actualización del HTML embebido en `memory_pairs_game_server.py`
