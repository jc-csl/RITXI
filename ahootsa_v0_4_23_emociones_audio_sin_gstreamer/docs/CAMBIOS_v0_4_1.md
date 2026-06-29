# Cambios v0.4.2 - Ahootsa Performance Audio Library

Esta versión parte de `Ahootsa Realtime Ollama v0.4.0` y mantiene la app original de conversación:

- micrófono;
- voz realtime;
- perfiles;
- emociones;
- movimientos;
- bailes;
- herramienta `ask_ollama`.

## Añadido

### Nuevas herramientas de perfil

- `celebrate_user`: celebra aciertos, esfuerzo o momentos felices combinando emoción, baile opcional y texto hablado.
- `sing_song`: genera canciones cortas originales y las dice/canta usando la voz realtime; puede acompañar con emoción y baile.
- `show_performance_library`: resume lo que Ahootsa puede hacer con emociones, bailes y canciones.

### Reglas nuevas del perfil

Ahootsa debe usar emociones, bailes o canciones cuando:

- el usuario lo pide explícitamente;
- Ahootsa está contento;
- el usuario acierta;
- el usuario termina una tarea;
- se quiere reforzar positivamente el esfuerzo.

## Nota sobre canciones

No se incorporan canciones comerciales ni letras con copyright. Las canciones son frases cortas originales que se reproducen mediante la voz realtime del backend actual.
