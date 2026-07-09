# 04 — Modelo conversacional: Hugging Face principal y Ollama auxiliar

## 1. Conclusión

La conversación principal de Ahootsa usa el núcleo oficial de Reachy Mini Conversation App y, por tanto, **Hugging Face Realtime**.

```text
Conversación por voz principal → Hugging Face Realtime
Consulta local auxiliar        → Ollama
```

Ollama no decide por defecto las acciones del robot durante la conversación principal.

## 2. Modo deployed

Configuración habitual:

```text
HF_REALTIME_CONNECTION_MODE=deployed
HF_REALTIME_WS_URL=
```

El backend remoto se negocia desde la infraestructura de Pollen/Hugging Face. La app local no muestra necesariamente el modelo exacto del backend remoto.

## 3. Modo local opcional

La app oficial permite modo local si existe un backend realtime compatible:

```text
HF_REALTIME_CONNECTION_MODE=local
HF_REALTIME_WS_URL=ws://127.0.0.1:8765/v1/realtime
```

Esto no equivale a Ollama automáticamente. Sería necesario un servidor realtime local compatible con el protocolo esperado.

## 4. Ollama en Ahootsa

Ollama se usa como apoyo:

```text
ask_ollama
panel de texto Ollama
consultas explícitas a IA local
```

Modelo local de chat recomendado en el equipo actual:

```text
llama3.2:3b
```

Modelo de embeddings presente:

```text
nomic-embed-text:latest
```

`nomic-embed-text` no debe usarse como modelo conversacional.

## 5. Diagnóstico del comportamiento por voz

Cuando los recursos existen y los botones del panel funcionan, pero por voz no se ejecuta una herramienta, el fallo probable está en la selección de herramienta por Hugging Face.

Para comprobarlo:

```powershell
powershell -ExecutionPolicy Bypass -File .\TRAZAR_PRUEBA_VOZ_AHOOTSA_7_0_19.ps1 -Seconds 120
```

Durante la traza decir:

```text
lista de bailes
haz baile dos
haz baile tres
haz un saludo
abre juego de parejas
```

Resultado esperado en logs de herramienta:

```text
list_panel_dances_activities
play_panel_dance_activity
start_memory_pairs_game
choose_memory_cards
```
