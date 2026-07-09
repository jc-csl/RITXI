# 04 — Modelo conversacional: Hugging Face principal y Ollama auxiliar

## 1. Conclusión principal

La conversación principal de la app oficial y de Ahootsa 5.0.25 se realiza mediante **Hugging Face Realtime**. Ollama no es el cerebro principal por defecto.

```text
Conversación natural principal -> Hugging Face Realtime
Pregunta explícita a IA local  -> Ollama local
```

## 2. Hugging Face en modo deployed

Por defecto, la app oficial usa:

```text
HF_REALTIME_CONNECTION_MODE=deployed
```

El servidor de sesión integrado es:

```text
https://pollen-robotics-reachy-mini-realtime-url.hf.space/session
```

Eso significa:

```text
App local
  ↓
servicio Hugging Face / Pollen
  ↓
backend realtime remoto
  ↓
modelo conversacional remoto
```

El modelo exacto puede no aparecer en el código local, porque lo decide el backend remoto.

## 3. Hugging Face en modo local

También se puede configurar:

```text
HF_REALTIME_CONNECTION_MODE=local
HF_REALTIME_WS_URL=ws://127.0.0.1:8765/v1/realtime
```

Este modo no significa que la app cargue directamente un modelo Hugging Face con `transformers`. Significa que la app se conectará a un servidor local compatible con Realtime.

Arquitectura:

```text
Ahootsa / app oficial
  ↓
ws://127.0.0.1:8765/v1/realtime
  ↓
backend HF local externo
  ↓
modelo local cargado por ese backend
```

Por tanto, si no existe ese backend local, el modo `local` no funcionará.

## 4. Variables antiguas que pueden confundir

La app oficial actual ignora variables antiguas como:

```text
BACKEND_PROVIDER
MODEL_NAME
```

Aunque Ahootsa 5.0.25 configuraba:

```text
BACKEND_PROVIDER=huggingface
```

la app oficial moderna no usa esa variable como selector real. El selector válido es:

```text
HF_REALTIME_CONNECTION_MODE
HF_REALTIME_WS_URL
```

## 5. Transcripción y voz

La app oficial configura sesión realtime con audio y transcripción. `REALTIME_TRANSCRIPTION_LANGUAGE=es` fuerza el idioma de transcripción.

Las voces se gestionan con nombres como:

```text
Sohee
Aiden
...
```

En Ahootsa se fuerza normalmente:

```text
VOICE=Sohee
AHOOTSA_VOICE=Sohee
REACHY_MINI_VOICE=Sohee
```

## 6. Ollama como IA local auxiliar

Ollama vive en:

```text
http://127.0.0.1:11434
```

Endpoint de generación:

```text
POST http://127.0.0.1:11434/api/generate
```

Modelo conversacional recomendado en el equipo actual:

```text
llama3.2:3b
```

Comprobar:

```powershell
ollama list
```

Probar:

```powershell
ollama run llama3.2:3b
```

## 7. Error histórico: modelo inexistente

En 5.0.25 se configuraba:

```text
OLLAMA_MODEL=ahootsa-local:latest
```

Si `ollama list` no muestra ese modelo, la llamada a Ollama falla. La solución es:

```text
OLLAMA_MODEL=llama3.2:3b
```

o crear explícitamente un alias si se desea mantener el nombre antiguo.

## 8. Cómo debe responder “Preguntar IA local”

El flujo correcto es:

```text
Usuario pulsa o pide “Preguntar IA local”
  ↓
herramienta ask_ollama o endpoint /ollama/ask
  ↓
http://127.0.0.1:11434/api/generate
  ↓
modelo llama3.2:3b
  ↓
respuesta devuelta a Ahootsa
```

No debe depender del backend principal Hugging Face.

## 9. Cuándo usar cada IA

```text
Hugging Face principal:
  conversación natural, voz, interacción fluida y herramientas oficiales.

Ollama auxiliar:
  preguntas puntuales, tareas locales, pruebas sin Internet, privacidad local.

Hugging Face local:
  solo si se instala un servidor realtime compatible aparte.
```

## 10. Diagnóstico de modelo real

Al arrancar, los logs deberían mostrar:

```text
HF_REALTIME_CONNECTION_MODE=deployed/local
HF_REALTIME_WS_URL=...
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:3b
modelos Ollama disponibles=...
```

Si no aparece esta información, añadirla al lanzador PowerShell y al log de eventos.
