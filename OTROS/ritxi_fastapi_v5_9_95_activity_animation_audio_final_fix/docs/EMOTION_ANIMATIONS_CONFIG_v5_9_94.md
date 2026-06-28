# v5.9.94: animaciones de emociones desde config

## Archivo

```text
app/config/robot_motion_policy.json
```

## Campos principales

```json
{
  "validated_visible_emotions": [
    "dance1",
    "dance2",
    "dance3",
    "cheerful1",
    "enthusiastic1",
    "amazed1",
    "electric1",
    "success1",
    "yes1",
    "no1",
    "attentive1",
    "thoughtful1"
  ],
  "emotion_positive": [
    "cheerful1",
    "enthusiastic1",
    "amazed1",
    "electric1",
    "success1",
    "yes1",
    "no1",
    "attentive1",
    "thoughtful1"
  ]
}
```

## Regla

Sí: si añades un movimiento válido desde Config, se usa sin tocar `app/static/app.js`.

No añadir:

```text
fiesta
```

porque en los logs aparece como no encontrado.
