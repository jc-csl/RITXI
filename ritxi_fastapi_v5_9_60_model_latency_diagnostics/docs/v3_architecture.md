# Arquitectura Ritxi v3

## Núcleo

La v3 separa responsabilidades:

- `llm/`: proveedores de lenguaje.
- `audio/`: STT persistente, TTS por cola y echo guard.
- `robot/`: simulador interno, cliente Reachy y biblioteca de movimientos.
- `orchestration/`: scheduler, memoria y turn manager.
- `static/`: panel de arquitectura.

## Sincronización

El `TurnManager` es el punto único de control del turno:

1. Desactiva lógicamente el micro mediante `EchoGuard`.
2. Encola gesto de pensamiento si procede.
3. Llama al LLM en modo normal o streaming.
4. Si streaming está activo, puede mandar la primera frase al TTS antes de terminar la generación.
5. Parsea etiqueta emocional.
6. Encola voz y movimiento en `ActionScheduler`.
7. Espera a finalizar si `synchronize_turn=true`.
8. Aplica cooldown y reactiva micro.

## Prioridades

El scheduler usa prioridad:

1. `manual`
2. `speech`
3. `emotion`
4. `idle`

Así los movimientos de idle no pisan la voz ni las acciones manuales.

## Nota sobre simulación oficial

Para usar el daemon simulado oficial de Reachy:

```bash
reachy-mini-daemon --sim
```

Después arrancar Ritxi con:

```bash
RITXI_MODE=reachy_daemon
```
