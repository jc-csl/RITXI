# STT vocabularies

Carpeta de grupos de palabras esperadas para mejorar el reconocimiento de voz por actividad.

## Archivos

- `index.json`: índice y estrategia de matching.
- `activity_mapping.json`: asigna cada actividad/tarjeta a uno o varios grupos.
- `common.json`: sí/no, saludos, despedidas, cortesía y muletillas.
- `animals.json`: animales y sonidos.
- `language.json`: sinónimos, opuestos, completar frase, frases cortas.
- `social_communication.json`: pedir ayuda, pedir turno, presentación y escucha.
- `emotions.json`: emociones y regulación.
- `music_sounds.json`: ritmo, sonidos e imitación.

## Uso previsto

Cuando una actividad pide una respuesta corta, se debe pasar su `activity_id`.
El sistema consulta `activity_mapping.json`, carga los grupos asociados y compara la transcripción con esas palabras esperadas.

Ejemplo:

```json
{
  "activity_id": "opuestos",
  "groups": ["opuestos_grande"]
}
```

Si Whisper oye `pequeñito`, se puede normalizar a `pequeño`.

Si oye una frase larga repetitiva o fuera del grupo, debe descartarse y pedir repetir.
