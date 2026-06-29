# v0.4.22 — Emociones con sonido y movimiento

## Objetivo

Cuando Ahootsa usa `play_emotion`, ahora intenta reproducir:

```text
1. Movimiento oficial de la emoción.
2. Audio OGG oficial asociado.
```

Esto busca parecerse más al panel de control de Reachy Mini, donde las emociones pueden tener movimiento y sonido.

## Importante

No se modifica el código original de `reachy_mini_conversation_app`.

La corrección se hace solo en el perfil Ahootsa:

```text
profiles/ahootsa_realtime_es/play_emotion.py
```

Ese archivo sustituye la herramienta `play_emotion` solo para el perfil Ahootsa.

## Si no suena

Si el movimiento sale pero no hay sonido, revisar:

```text
%LOCALAPPDATA%\Reachy Mini Control\ahootsa_logs\play_emotion_audio.log
```

y comprobar que Windows tiene una salida de audio estable.

El error habitual sería de GStreamer/WASAPI, por ejemplo si Windows no puede escribir en el dispositivo de audio.

## Diagnóstico

Con Desktop cerrado o abierto:

```powershell
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_EMOCIONES_AUDIO.ps1
```

## Pruebas por voz

```text
saluda con sonido
celebra con una emoción
haz una emoción con sonido
ponte contento
piensa
```

## Resultado esperado

```text
Movimiento: sí.
Sonido: sí, si el dispositivo de audio de Windows y el OGG oficial están disponibles.
```
