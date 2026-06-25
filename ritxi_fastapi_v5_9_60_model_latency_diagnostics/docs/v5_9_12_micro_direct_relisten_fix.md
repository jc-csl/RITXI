# v5.9.12 · Micro directo y reescucha automática

Cambios:
- El botón `Activar conversación / micro` abre el micro de forma inmediata.
- Tras cada respuesta hablada de Ritxi, el micro se reabre automáticamente si la conversación está activa.
- Menos espera:
  - `serverRecordMaxMs=3200`
  - `silenceSendMs=550`
  - `relistenDelayMs=350`
  - `serverVadThreshold=0.020`
- Evita que el segundo turno se quede parado después de `Ritxi terminó de hablar`.
