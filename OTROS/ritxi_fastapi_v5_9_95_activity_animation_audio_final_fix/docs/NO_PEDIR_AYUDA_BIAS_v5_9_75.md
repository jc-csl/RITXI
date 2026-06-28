# Corrección v5.9.75: sesgo hacia “pedir ayuda”

## Problema

El chat tendía a responder con ejemplos de pedir ayuda incluso cuando el usuario preguntaba otra cosa.

Causas corregidas:

- textarea inicial con texto fijo sobre pedir ayuda;
- prompt del sistema demasiado centrado en ese ejemplo;
- posible historial de sesión `demo`;
- fallbacks con ejemplos de ayuda.

## Cambios

- textarea inicial vacío;
- sesión nueva por arranque si era `demo`;
- system prompt con prioridad de tema actual;
- fallback para `vida`, `gato`, `perro`, etc.;
- instrucciones a Ollama para no cambiar de tema.
