# 10 — Audio de emociones v0.4.44

## Problema

Al pedir una emoción, el robot se movía pero no se escuchaba el audio asociado.

## Cambios

```text
- Se refuerza play_emotion.py.
- El audio usa pygame/SDL, no GStreamer.
- Se prueban varios drivers: directsound, wasapi, winmm y default.
- Se mantiene vivo el objeto Sound de pygame para evitar que el audio se corte.
- Se añade la herramienta play_emotion_with_audio.
```

## Herramienta recomendada

```text
play_emotion_with_audio
```

Uso esperado:

```text
saluda con emoción
celebra
ponte contento
haz una emoción
```

## Reparación

Con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_AUDIO_EMOCIONES_AHOOTSA.ps1
```

## Prueba directa

```powershell
powershell -ExecutionPolicy Bypass -File .\test\PROBAR_AUDIO_EMOCION_HERRAMIENTA.ps1
```

Debe sonar un OGG oficial por los altavoces de Windows.

## Variables relevantes

```text
AHOOTSA_EMOTION_AUDIO_BACKEND=pygame
AHOOTSA_PYGAME_AUDIO_DRIVERS=directsound,wasapi,winmm,default
AHOOTSA_EMOTION_AUDIO_VOLUME=1.0
```

## Log

```text
%LOCALAPPDATA%\Reachy Mini Control\ahootsa_logs\play_emotion_audio.log
```
