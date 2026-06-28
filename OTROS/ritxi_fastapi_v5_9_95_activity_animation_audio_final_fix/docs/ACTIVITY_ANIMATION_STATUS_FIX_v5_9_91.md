# v5.9.91: animaciones de actividad y estado robusto

## Problema visto en log

El log mostraba código antiguo/cacheado y errores repetidos:

```text
Ritxi v5.9.71 iniciado
Cannot set properties of null (setting 'textContent')
```

También se veía que el robot acababa conectando y podía enviar movimiento, por lo que el problema estaba en el frontend y en la regla de runtime de actividades.

## Corrección

```text
Chat Texto + IA → sin animación automática
Cualquier ficha/actividad/juego/emoción → animación inicio/final aunque el chat esté en Texto + IA
```

## Trazas nuevas

```text
Animación positiva INICIO solicitada
Animación positiva FINAL solicitada
```

## Elementos de estado

`refreshStatus()` es tolerante a elementos que ya no existen en pantalla.
