# 16 — Memory estable sin bloqueo de audio v0.4.45

## Problema

El juego Memory podía quedarse parado y dejar de responder al audio.

## Evidencia

En el log se veía que el wrapper intentaba copiar perfiles mientras la app estaba en marcha y algunos archivos estaban bloqueados por Windows. También se veía que el arranque usaba el perfil desde la carpeta del proyecto editable.

## Corrección

```text
- Ya no se copian perfiles durante el arranque de la app.
- La copia de perfiles se hace solo con scripts de instalación/reparación.
- choose_memory_cards ya no ejecuta movimiento ni audio interno.
- Memory queda en modo visual + voz normal para no bloquear el micrófono.
- Se mantiene protección anti-duplicado.
```

## Reparación directa

Con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_MEMORY_ESTABLE_SIN_BLOQUEO.ps1
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_MEMORY_NO_BLOQUEO.ps1
```

Debe mostrar:

```text
sin await emotion = True
sin play_emotion interno = True
visual_only_no_blocking_audio = True
```

## Secuencia esperada

```text
Usuario: uno y tres
1. Las cartas se giran.
2. Ahootsa habla la frase.
3. El micrófono sigue activo.
4. No se lanza movimiento ni sonido interno desde la jugada.
```

Las emociones y bailes siguen disponibles fuera del juego.
