# v5.9.16 · STT con vocabulario guiado

Problema:
- En juegos de animales o palabras cortas, Whisper puede transcribir palabras parecidas o frases raras.

Cambios:
- Nuevo parámetro `vocabulary_hint` en `/api/audio/transcribe_file`.
- Para actividades de animales se usa una lista cerrada:
  - perro, gato, vaca, oveja, caballo, león, mono, rana, pato, etc.
- Se aplican alias y corrección fuzzy solo en transcripciones cortas.
- La corrección se registra en logs como `stt_vocabulary_corrected`.
