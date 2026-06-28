# Configuración externa v5.9.71

## Archivos nuevos

```text
app/config/interaction_policy.json
app/config/ritxi_constants.py
```

## interaction_policy.json

Define qué fichas pueden responder localmente y cuáles deben usar Ollama.

- `local_activity_ids`: solo actividades muy cerradas, cortas y fáciles.
- `ollama_activity_ids`: actividades abiertas, explicativas o conversacionales.
- `defaults`: modelo, temperatura y timeout.

## Creatividad

El slider `Creatividad` se lee con `creativityValue()` y se envía al backend como:

```json
{"temperature": 0.25}
```

El backend lo aplica en `OllamaProvider` como `temperature_override`.

## Colores de fichas

Las fichas locales simples se marcan como:

```text
Respuesta local simple
```

con color azul/cian.
