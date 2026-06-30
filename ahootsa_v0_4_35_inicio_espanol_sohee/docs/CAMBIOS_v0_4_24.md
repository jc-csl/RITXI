# v0.4.35 — Juego de parejas de animales

## Objetivo

Añadir una actividad educativa guiada por el robot:

```text
Juego de parejas de animales
```

El usuario busca parejas formadas por:

```text
animal + grupo
```

Ejemplos:

```text
rana → anfibio
águila → ave
delfín → mamífero
```

## Diseño del juego

```text
- 8 parejas.
- 16 cartas.
- Cartas numeradas del 1 al 16.
- El usuario puede decir al robot: "1 y 5".
- HTML + CSS + JavaScript autocontenido.
- Temporizador.
- Contador de movimientos.
- Animaciones divertidas al acertar.
- Pantalla final con datos breves sobre cada grupo animal.
```

Los iconos de los grupos no son iguales a los iconos de los animales.

## Puerto local

Por defecto el juego se sirve en:

```text
http://localhost:7870
```

Se puede cambiar con la variable:

```text
AHOOTSA_MEMORY_GAME_PORT
```

## Herramientas añadidas al perfil Ahootsa

```text
start_memory_pairs_game
choose_memory_cards
reset_memory_pairs_game
memory_pairs_game_status
```

## Cómo lo controla el robot

Cuando el usuario dice:

```text
quiero el juego de parejas
```

Ahootsa llama a:

```text
start_memory_pairs_game
```

Después el robot pide:

```text
Dime dos números.
```

Cuando el usuario dice:

```text
1 y 5
```

Ahootsa llama a:

```text
choose_memory_cards(first_card=1, second_card=5)
```

Si acierta:

```text
- celebra;
- anima al usuario;
- pide otra pareja.
```

Si falla:

```text
- anima;
- dice que casi;
- pide otra pareja.
```

Al final:

```text
- celebra el resultado;
- resume movimientos y tiempo;
- pregunta si quiere jugar otra vez.
```

## Prueba sin Desktop

```powershell
powershell -ExecutionPolicy Bypass -File .\PROBAR_JUEGO_PAREJAS_ANIMALES.ps1
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_JUEGO_PAREJAS_ANIMALES.ps1
```

## Prueba por voz

Con Ahootsa arrancado:

```text
quiero el juego de parejas de animales
```

Luego:

```text
levanta la 1 y la 5
```

o simplemente:

```text
1 y 5
```
