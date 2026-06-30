# 04 — Configuración importante

## Perfil principal

```text
src/ahootsa_realtime_ollama_desktop_app/profiles/ahootsa_realtime_es/
```

Aquí se configura casi todo el comportamiento de Ahootsa.

## `instructions.txt`

Define la identidad, idioma, estilo, herramientas y reglas.

Uso principal:

```text
- hablar en castellano;
- presentarse como Ahootsa;
- usar lenguaje sencillo;
- controlar el orden del juego Memory;
- usar herramientas concretas;
- no mezclar habla, giro de cartas y reacción.
```

## `greeting.txt`

Define el saludo inicial.

Contenido actual resumido:

```text
¡Hola! Soy Ahootsa. Estoy lista para ayudarte. ¿Qué quieres hacer?
```

## `voice.txt`

Define la voz preferida del perfil.

Contenido actual:

```text
Sohee
```

Si no se respeta, ejecutar:

```powershell
powershell -ExecutionPolicy Bypass -File .\FORZAR_INICIO_CASTELLANO_SOHEE.ps1
powershell -ExecutionPolicy Bypass -File .\test\VER_VOZ_AHOOTSA.ps1
```

## `tools.txt`

Lista de herramientas que puede usar el perfil.

Contenido actual:

```text
dance
stop_dance
play_emotion
stop_emotion
camera
camera_pc
idle_do_nothing
move_head
sweep_look
remember
forget
ask_ollama
start_memory_pairs_game
choose_memory_cards
reset_memory_pairs_game
memory_pairs_game_status
list_memory_pairs_games
hint_memory_pairs_game
```

## `ask_ollama.py`

Herramienta para consultar Ollama local.

Parámetros habituales a revisar dentro del archivo:

```text
modelo: ahootsa-local:latest
URL Ollama: http://127.0.0.1:11434
instrucciones de respuesta breve y sencilla
```

## `memory_pairs_game_server.py`

Motor del juego Memory.

Configura:

```text
puerto: 7870
juegos JSON disponibles
cartas visibles al fallar: 4 segundos
estado de cartas
reset del juego
pistas
```

Parámetro importante:

```python
REVEAL_SECONDS = 4
```

## `choose_memory_cards.py`

Controla la secuencia de una jugada.

Configura:

```text
pausa antes de girar cartas
pausa antes de reaccionar
reacción única
reset tras terminar
pregunta final
```

## JSON de juegos

```text
animales.json
ciudades.json
alimentos.json
```

Cada JSON contiene 4 parejas.

Formato básico:

```json
{
  "id": "animales",
  "title": "Memory de animales",
  "pairs": [
    {
      "id": "frog",
      "left": "rana",
      "left_icon": "🐸",
      "right": "anfibio",
      "right_icon": "💧",
      "hint": "La rana vive entre agua y tierra."
    }
  ]
}
```

## `pyproject.toml`

Define cómo se instala el paquete Python en el entorno de Reachy Mini Desktop.

No suele editarse salvo cambio de versión, nombre del paquete o datos incluidos.
