# v5.9.92: animaciones visibles

## Diagnóstico

En el log de v5.9.91 se veía que las animaciones sí se solicitaban y se encolaban:

```text
Animación positiva INICIO solicitada
Inicio positivo aleatorio...
action_enqueue...
robot_emotion_start...
```

También se veía que el cierre eligió `fiesta`, pero la librería no lo encontró:

```text
recorded_move_not_found: fiesta
```

## Corrección

Se retiran ids no válidos de la lista positiva y se deja una pausa de visibilidad tras el inicio positivo.

## Lista positiva validada

```text
cheerful1
amazed1
yes1
success1
dance1
dance2
dance3
```
