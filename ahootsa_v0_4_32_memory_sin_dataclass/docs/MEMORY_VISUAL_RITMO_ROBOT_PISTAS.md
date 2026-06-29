# v0.4.30 — Memory visual con ritmo del robot y pistas

## Cambios visuales

```text
- Cartas grandes.
- Dorso azul.
- Número blanco grande en el dorso.
- Solo cartas en pantalla.
- 4 parejas / 8 cartas.
```

## Mecánica

```text
- El usuario dice dos números.
- Las dos cartas se giran.
- Si son pareja, quedan visibles.
- Si no son pareja, se mantienen giradas 3 segundos.
- Después se ocultan solas.
```

## Robot

El robot lleva el ritmo:

```text
- da instrucciones;
- anima si falla;
- celebra si acierta;
- controla el final;
- puede dar pistas si el usuario se atasca.
```

## Nueva herramienta

```text
hint_memory_pairs_game
```

Se usa con frases como:

```text
dame una pista
ayuda
no sé
estoy atascado
```

## Prueba

```powershell
powershell -ExecutionPolicy Bypass -File .\PROBAR_JUEGOS_PAREJAS_JSON.ps1
```
