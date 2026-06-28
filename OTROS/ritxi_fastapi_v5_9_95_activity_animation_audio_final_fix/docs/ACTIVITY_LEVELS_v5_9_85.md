# Clasificación de fichas v5.9.85

## Niveles

```text
Respuesta local simple → cian
Interacción corta      → azul
Interacción larga      → morado/fucsia
Máxima interacción     → dorado/naranja
Solo reproduce         → gris
```

## Escucha activa

`escucha_activa` y `escuchar` son interacción larga.

Regla funcional:

```text
clic en Escucha activa
→ Ritxi inicia escucha
→ usuario responde
→ Ritxi contesta
→ la actividad continúa
→ solo termina si el usuario dice terminar / fin / parar / cambiar / otra actividad
```

## Corrección técnica

Antes solo se mantenía contexto si era `MAX_CREATIVE_ACTIVITY_IDS`.  
Ahora también se mantiene si:

```js
isLongInteractionActivityContext(activeContextForTurn)
```
