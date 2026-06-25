# Ritxi v5 · Panel profesional

La versión 5 reorganiza la aplicación alrededor de tres objetivos:

1. Operación directa mediante tarjetas de acción.
2. Conversación con Ollama visible y diagnosticable.
3. Pruebas modulares mediante checkboxes para aislar errores.

## Acciones, no solo configuración

Las tarjetas de la pestaña **Emociones** y **Acciones** ejecutan directamente una acción:

- movimiento en Reachy, si `Movimiento Reachy` está activado;
- voz por navegador, si `TTS`, `Audio salida` y `Respuesta por voz automática` están activados;
- mensaje visible en el chat, si `Mover + hablar + generar texto al mismo tiempo` está activado;
- registro en logs.

## Checkboxes de prueba

Los módulos se pueden activar/desactivar para diagnosticar:

- Micrófono
- STT
- Ollama / LLM
- TTS
- Audio salida
- Texto salida
- Movimiento Reachy
- Mover mientras habla
- Cámara / visión
- Logs detallados
- Guardar sesión
- Modo simulación

## Comportamiento

- `Espera activa`: activa idle/movimiento suave mientras Ritxi espera.
- `Mover + hablar + generar texto al mismo tiempo`: al ejecutar una acción o respuesta, actualiza chat, reproduce audio y mueve el robot de forma coordinada.
- `Respuesta por voz automática`: reproduce la respuesta del chat mediante Web Speech Synthesis.
- `Envío automático tras STT`: envía el turno cuando el STT detecta una frase.
- `Echo guard`: bloquea el micro durante la voz para evitar eco.
- `Modo tutor DI`: orienta el uso a interacción paciente, amable y de comunicación sencilla.
