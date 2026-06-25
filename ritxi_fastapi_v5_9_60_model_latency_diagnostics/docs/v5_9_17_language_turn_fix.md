# v5.9.17 · Actividades de lenguaje con turno

Problema:
- En actividades como `Sinónimos`, Ritxi decía la consigna, pero no pasaba claramente el turno al usuario.

Cambios:
- `Sinónimos`, `Opuestos`, `Buscar palabra`, `Completar frase`, `Describir imagen`, `Frase corta` e `Historia por turnos` pasan a tener `awaitUser=true`.
- Tras la consigna, se llama a `promptUserAfterActivity`.
- El micro se abre o permite responder por texto.
- Se añade `vocabularyHint='short'` para mejorar STT en palabras cortas.
