# v5.9.46 · Coherencia de actividades y velocidad

## Problemas detectados en logs

- Gemma 3 1B llegó a responder en ~1.6-2.0 s, pero el turno total subía a 14-32 s.
- La mayor parte del tiempo no era siempre el modelo:
  - movimientos de robot;
  - TTS navegador con timeout de seguridad;
  - espera de turnos;
  - fallback mock por timeout cliente de 24 s;
  - respuestas que no conservaban contexto de actividad.
- Qwen 0.6B llegó a tardar ~9.6 s y devolvió texto vacío en un turno.

## Cambios

- Se añade contexto de actividad en frontend.
- Se añade respuesta rápida local para actividades cerradas/lúdicas.
- Se mantiene coherencia en historias/cuentos enviando contexto enriquecido a Ollama.
- Se compactan pestañas superiores.
