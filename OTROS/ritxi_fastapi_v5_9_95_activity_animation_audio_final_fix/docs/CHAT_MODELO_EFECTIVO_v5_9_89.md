# v5.9.89: modelo efectivo en chat libre

## Problema

En v5.9.88, si `qwen3:0.6b` quedaba seleccionado, el chat libre usaba respuesta segura local genérica:

```text
Entendido. Dime el tema y te respondo con una frase corta.
```

Esto evitaba el error, pero no respondía bien.

## Corrección

```text
qwen3:0.6b seleccionado + chat libre → modelo efectivo gemma3:1b
```

Las actividades con contexto pueden seguir usando el modelo seleccionado si procede.

## Fallbacks mejorados

Se añaden respuestas mínimas para:

```text
hola
naturaleza
bosque
mar
amor
jugar
```

## Funciones relevantes

```text
ensureRecommendedModelSelected()
effectiveModelForChat()
fallbackFromConversationPolicy()
safeBotText()
```
