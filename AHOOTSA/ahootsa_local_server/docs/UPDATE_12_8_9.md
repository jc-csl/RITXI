# Update 12.8.9 — Baile inmediato y sin duplicados

## Incidencia de la sesión 25

El retraso no estaba en la carga del audio o del movimiento.

Para `Baile 2`, Aocha dijo «Vamos a bailar» a las 14:55:07, pero la llamada
real a `play_ahootsa_dance` no llegó hasta las 14:55:39, después de que la
persona dijera «Uh».

Al repetir el mismo baile, Aocha volvió a anunciarlo a las 14:56:07, pero la
llamada no llegó hasta las 14:56:48, después de «Uno, dos, tres».

Una nueva intervención provocó además una segunda llamada al mismo baile y
reinició el que ya estaba ejecutándose.

## Corrección

- Selección clara → llamada inmediata en el mismo turno.
- La herramienta se llama antes de pronunciar «Vamos a bailar».
- No se espera una nueva intervención.
- Exactamente una llamada por petición.
- Quejas, conteos y sonidos no generan llamadas duplicadas.
- La herramienta ignora una segunda llamada al mismo baile activo.
- `diagnostico.json` registra llamadas retrasadas y duplicadas.

## Herramienta

```text
ahootsa_dances.py 1.5
```
