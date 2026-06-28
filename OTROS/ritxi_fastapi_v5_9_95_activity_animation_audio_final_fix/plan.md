# plan.md · Ritxi v5

## Objetivo

Construir un panel profesional para Ritxi, inspirado visualmente en Reachy Mini Desktop, pero centrado en operación real:

- chat con Ollama;
- micro/audio para conversación;
- acciones directas con tarjetas;
- movimiento + audio al hacer clic;
- configuración secundaria;
- diagnóstico con logs.

## Decisiones de diseño

- Panel oscuro, profesional y compacto.
- Tres columnas: robot/estado, chat/logs, acciones.
- Los controles manuales de bajo nivel no dominan la pantalla.
- Las acciones preprogramadas son el foco.
- Checkboxes permiten aislar funcionalidad.

## Funcionalidad mínima de v5

- Arrancar con FastAPI.
- Conectar a daemon simulado o usar simulación interna.
- Enviar chat a Ollama/mock.
- Ejecutar tarjetas de acción.
- Reproducir voz en navegador.
- Encolar movimiento en robot/simulación.
- Registrar eventos en logs.
