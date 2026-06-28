# Política de conversación v5.9.76

## Archivo editable

```text
app/config/conversation_policy.json
```

## Qué controla

- Limitaciones conocidas del modo conversacional.
- Filtro anti-repetición.
- Prioridad del último mensaje del usuario.
- Respuestas de fallback por tema.

## Por qué se repite

El modelo `qwen3:0.6b` es muy rápido, pero pequeño. Puede repetir la respuesta anterior cuando:

- el historial reciente arrastra un tema;
- la creatividad está baja;
- el mensaje del usuario es muy corto;
- Ollama devuelve una respuesta pobre o vacía.

## Dónde se configura

Desde la pestaña:

```text
Config. → Política conversación / repetición
```

También se puede abrir en `Todos los archivos editables`.
