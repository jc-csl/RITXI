# Ollama local en Ahootsa v0.3.2

## Modelo usado

```text
hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest
```

El script crea un modelo derivado llamado:

```text
ahootsa-local
```

## Flujo

```text
Reachy Mini Desktop
  -> Start Ahootsa Ollama Local
  -> panel http://127.0.0.1:7860
  -> API Ollama http://127.0.0.1:11434/api/chat
  -> modelo ahootsa-local
```

## Por qué no se usa Hugging Face Local localhost:11434

`localhost:11434` es la API de Ollama. La opción `Hugging Face Local` de la app oficial espera un backend realtime compatible, no `/api/chat`.
