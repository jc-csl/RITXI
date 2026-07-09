# Ahootsa 5.0.38 — LLM dual: Hugging Face local + Ollama

Esta versión recupera el enfoque anterior de usar un **modelo Hugging Face descargado en local**, sin perder la opción rápida de **Ollama**.

## Por qué aparece este cambio

En los logs de la 5.0.35/5.0.36 aparecía que la app llamaba a:

```text
model = ahootsa-local:latest
```

pero en el equipo solo estaban instalados en Ollama:

```text
llama3.2:3b
nomic-embed-text:latest
```

Por eso Ahootsa quedaba en “preguntando...” o devolvía 404.

## Proveedores soportados

La 5.0.38 permite tres modos:

```text
auto      -> usa Hugging Face local si se ha indicado ruta; si no, usa Ollama.
hf_local  -> fuerza modelo Hugging Face local.
ollama    -> fuerza Ollama.
```

Variables principales:

```text
AHOOTSA_LLM_PROVIDER=auto|hf_local|ollama
AHOOTSA_HF_MODEL_PATH=D:\RITXI\models\mi_modelo_hf
AHOOTSA_OLLAMA_MODEL=llama3.2:3b
AHOOTSA_OLLAMA_URL=http://127.0.0.1:11434
```

## Endpoints añadidos

```text
GET  /llm/status
POST /llm/ask
GET  /ollama/status      compatibilidad
POST /ollama/ask         compatibilidad
GET  /camera/page
GET  /camera/health
POST /camera/upload
```

## Notas de rendimiento

Para conversación más natural y ágil:

- Ollama con `llama3.2:3b` suele ser más fácil y rápido en CPU/GPU doméstica.
- Hugging Face local puede ser más lento si carga `transformers` + `torch` en CPU.
- Conviene limitar `max_new_tokens` a 80–160.
- Conviene responder con frases cortas y una sola pregunta por turno.
- Evitar animaciones automáticas en chat simple reduce latencia.

## Cámara PC

La cámara PC no es la cámara MuJoCo. Se prueba en:

```text
http://127.0.0.1:7860/camera/page
```

Debe aceptarse el permiso de cámara en Windows/navegador/Desktop Control.
