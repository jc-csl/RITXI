# v5.9.90: actividades no bloqueadas por robot

## Error corregido

```text
launchPositiveOpeningRobotAnimation()
→ usaba phase sin definir
```

Eso podía provocar que al hacer clic en actividades no se iniciara nada.

## Corrección

```text
if(!shouldUseRobotAnimationForInteraction(itemOrContext, 'start'))
```

## Cambio funcional

Las animaciones positivas de inicio y cierre se lanzan en segundo plano:

```text
firePositiveOpeningRobotAnimation()
firePositiveClosingRobotAnimation()
```

Por tanto:

```text
actividad → arranca siempre
robot lento/fallando → no bloquea la actividad
logs → siguen registrando el aviso
```
