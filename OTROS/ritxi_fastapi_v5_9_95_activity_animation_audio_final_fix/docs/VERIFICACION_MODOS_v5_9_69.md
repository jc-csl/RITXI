# Verificación v5.9.69

## Error corregido

`payloadFlags` se usaba antes de declararse dentro de `sendTurn()`.

## Matriz de comportamiento

| Zona | Afecta a | Observación |
|---|---|---|
| Texto + IA rápida | Chat conversacional | Texto + IA, sin robot conversacional |
| Texto + IA + Robot | Chat conversacional | Texto primero, luego emoción/robot |
| Micro + IA | Chat conversacional | Micro + IA, texto disponible |
| Completo | Chat conversacional | Texto + micro + IA + voz + robot |
| Fichas | Acción directa | Imponen su propio audio/robot/turno con `cardRuntime(item)` |
| Actividades con turno | Acción directa | Pueden pedir micro aunque el chat esté en modo texto; si no, texto |

## Checks estáticos

```json
{
  "payloadFlags_defined_before_log": true,
  "no_duplicate_payload_const_after_try": true,
  "chatFlags_function_exists": true,
  "cardRuntime_exists": true,
  "selfcheck_exists": true,
  "prompt_activity_micro_independent": true,
  "node_compile_target": true
}
```
