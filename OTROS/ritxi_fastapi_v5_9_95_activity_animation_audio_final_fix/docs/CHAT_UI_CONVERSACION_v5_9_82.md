# Conversación y UI v5.9.82

## Problema

Con qwen3:0.6b el chat copiaba ejemplos del prompt y repetía el tema anterior. El log mostraba que respondía lo mismo incluso con mensajes como `hola` o `amor`.

## Corrección conversacional

- Sin historial en chat libre por defecto.
- Sin ejemplos concretos dentro del system prompt.
- Fallbacks de `vida` ya no contienen `pedir ayuda`.
- El contexto de actividad no se usa en chat normal.

## Corrección de interfaz

Los modos:

```text
Texto + IA
Texto + IA + Robot
Micro + IA + sonidos
Completo
```

ahora están dentro de `Chat con Ollama`, porque afectan al chat conversacional, no a fichas/actividades.
