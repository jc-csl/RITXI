# v5.9.29 · Layout ampliado y desbloqueo

## Layout

- `dashboard-v591` cambia proporciones para dar más espacio al panel derecho.
- `actions-panel` aumenta altura útil.
- `bottom-layout` se compacta.
- La caja `Modo general` queda más baja y estrecha.
- Se añade indicador de modelo:
  - `modelLoadedPill`
  - `modelLoadedPillBottom`

## Bloqueos

- Nuevo botón `Desbloquear`.
- `sendTurn()` usa `AbortController` con timeout cliente.
- Si Ollama tarda demasiado:
  - se aborta el fetch;
  - se muestra mensaje en chat;
  - `realtimeSending=false`;
  - la interfaz vuelve a estado listo.

## Modelo visible

El modelo seleccionado en `modelSelect` se muestra en la UI y se registra en logs.
