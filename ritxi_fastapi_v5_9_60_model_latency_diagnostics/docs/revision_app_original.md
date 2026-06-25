# Revisión de la app original

Problemas detectados en el ZIP recibido:

1. `main.py` mezcla API, Ollama, control de robot, TTS, parsing de emociones y gestión de hilos.
2. `historial_mensajes` es global: todos los usuarios/sesiones comparten conversación.
3. Se crea un `threading.Thread` por interacción, por lo que varias respuestas pueden solaparse.
4. `GestorAnimaciones.ocupado` y `permitir_idle` son booleanos compartidos sin lock ni cola.
5. El bucle idle puede competir con movimientos emocionales si hay timing desfavorable.
6. `pyttsx3.runAndWait()` es bloqueante y puede causar desincronización si se lanza en varios hilos.
7. El parsing de etiquetas usa reemplazos globales y puede borrar texto válido.
8. El endpoint `/api/shutdown` mata procesos de Windows de forma agresiva; es peligroso para pruebas.
9. Los sliders de telemetría en la UI no enviaban pose al backend.
10. No había endpoint `/api/health` para diagnosticar Ollama, robot y estado de la cola.

Solución aplicada en v2:

- Cola única `ActionScheduler`.
- Cliente robot simulado por defecto.
- Adaptador opcional para Reachy SDK.
- TTS opcional y serializado.
- Sesiones separadas.
- Parsing robusto de etiquetas.
- UI con texto manual, micro, checkboxes, health, reset, idle, gestos y pose manual.
