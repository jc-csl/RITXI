# Actividades autónomas y robot positivo v5.9.87

## Regla principal

Las actividades y fichas tienen runtime propio.

```text
Modo del chat ≠ modo de actividad
```

El chat puede estar en `Texto + IA`, pero una actividad puede activar robot, sonido y micro si lo necesita.

## Inicio y final con robot positivo

Si una actividad contiene robot:

```text
inicio → animación positiva aleatoria
actividad → ejecución normal
final → animación positiva aleatoria
```

## Bailes incluidos

```text
dance1
dance2
dance3
baile
calma
```

También se incluyen animaciones positivas como:

```text
cheerful1
enthusiastic1
yes1
hello1
amazed1
electric1
aplauso
celebracion
saludo
```

## Interacciones largas

No terminan al primer turno. Solo lanzan cierre positivo cuando el usuario pide cerrar.
