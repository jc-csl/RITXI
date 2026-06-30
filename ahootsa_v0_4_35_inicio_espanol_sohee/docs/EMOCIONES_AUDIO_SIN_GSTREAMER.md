# v0.4.35 — Emociones con audio sin GStreamer

## Problema detectado

El log muestra:

```text
reachy_mini.media.audio_gstreamer
GstWasapi2Sink
Failed to write to device
```

Esto significa que el audio falla en la capa GStreamer/WASAPI de Windows.

## Solución aplicada

Esta versión evita usar `reachy_mini.media.play_sound` para los sonidos de emociones de Ahootsa.

En su lugar:

```text
Movimiento oficial → RecordedMoves / EmotionQueueMove
Sonido oficial OGG → pygame / SDL
```

Así se mantiene el movimiento oficial y el sonido oficial, pero se evita el pipeline GStreamer de Reachy Mini para esa parte.

## Importante

No se modifica:

```text
reachy_mini_conversation_app
reachy_mini.media.audio_gstreamer
la app oficial
```

Solo se cambia el `play_emotion.py` dentro del perfil Ahootsa.

## Instalación

Con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```

También puedes instalar solo el soporte de audio:

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AUDIO_EMOCIONES_PYGAME.ps1
```

## Prueba rápida sin Reachy

```powershell
powershell -ExecutionPolicy Bypass -File .\PROBAR_AUDIO_EMOCION_PYGAME.ps1
```

Debe sonar un OGG oficial por los altavoces de Windows.

## Prueba desde Ahootsa

```text
usa la herramienta play_emotion con emotion greeting y sonido true
```

o:

```text
saluda con sonido
```

## Log

```powershell
Get-Content "$env:LOCALAPPDATA\Reachy Mini Control\ahootsa_logs\play_emotion_audio.log" -Encoding UTF8 -Tail 40
```

Resultado esperado:

```text
"audio": {"ok": true, "backend": "pygame", ...}
```
