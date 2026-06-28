# v5.9.95: audio y cierre positivo de actividades

## Problema del log

En v5.9.94, las animaciones de actividad se lanzaban así:

```text
action_enqueue ... audio:false
recorded_move_played ... audio_path:null, audio_started:false
```

Por eso la animación inicial se veía pero no sonaba.

## Corrección

El inicio/final positivo ahora hace dos cosas:

```text
1. playOfficialRecordedAudio(emotion)
2. /api/robot/action con motion_enabled=true
```

## Configuración

Archivo:

```text
app/config/robot_motion_policy.json
```

Campos nuevos:

```json
{
  "play_audio_on_positive_start": true,
  "play_audio_on_positive_end": true,
  "positive_audio_force": true,
  "positive_audio_wait_until_end": false
}
```

## Diagnóstico esperado en logs

```text
Audio oficial positivo start solicitado
Audio oficial positivo end solicitado
Animación positiva FINAL lanzada
```
