# v5.9.88: Script 6, animaciones y layout

## Script 6

```text
6_LANZAR_RITXI_COMPLETO.cmd
6_LANZAR_RITXI_COMPLETO.ps1
```

Flujo:

```text
1_INSTALAR_RITXI.cmd
2_INICIAR_DAEMON_RITXI.cmd en nueva terminal
espera hasta 45 s / puerto 8000
3_RUN_RITXI.cmd en nueva terminal
```

## Error corregido

```text
shouldUseSafeLocalForExperimentalModel is not defined
```

Se añaden las funciones:

```text
isExperimentalConversationModel()
shouldUseSafeLocalForExperimentalModel()
respondExperimentalModelSafely()
```

## Regla de animación

```text
Chat Texto + IA → solo texto, sin animación automática
Todo lo demás → puede usar animación positiva inicio/final
```

Incluye:

```text
emociones
actividades
juegos
interacciones con micro
chat con robot
chat completo
```

## Layout

Los paneles principales se igualan en altura y las fichas ganan altura vertical.
