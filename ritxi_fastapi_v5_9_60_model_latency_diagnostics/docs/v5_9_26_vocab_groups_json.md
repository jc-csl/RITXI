# v5.9.26 · Vocabularios JSON para STT guiado

Se añade:

`app/config/stt_vocabularies/`

Objetivo:
- Definir grupos de palabras esperadas por actividad.
- Reducir errores de Whisper en juegos cortos.
- Evitar que respuestas cerradas se traten como conversación abierta.

Archivos:
- `index.json`
- `activity_mapping.json`
- `common.json`
- `animals.json`
- `language.json`
- `social_communication.json`
- `emotions.json`
- `music_sounds.json`

Ejemplo:
- Actividad `opuestos` → grupo `opuestos_grande`.
- Actividad `animal_corto` → grupo `animales`.
- Actividad `pedir_ayuda` → grupo `pedir_ayuda`.

Nota:
Esta versión prepara la carpeta y los datos. La integración total del motor de matching JSON puede hacerse en la siguiente versión.
