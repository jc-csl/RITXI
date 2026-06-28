# Audio oficial OGG/WAV v5.9.80

## Problema detectado en logs

Los logs mostraban errores tipo:

```text
cheerful1.wav: 404 Entry Not Found
NotSupportedError: Failed to load because no supported source was found.
```

El movimiento sí se ejecutaba, pero el audio no cargaba porque se pedían `.wav`.

## Corrección

```text
1. Probar <emotion>.ogg
2. Si no existe, probar <emotion>.wav
3. Servir media_type correcto: audio/ogg o audio/wav
```

## Archivos modificados

```text
app/robot/recorded_emotions.py
app/main.py
app/static/app.js
```
