# 03 — Flujos de datos

## Flujo general de conversación

```text
Usuario habla
  ↓
Reachy Mini Desktop / app oficial de conversación
  ↓
Perfil Ahootsa: instructions.txt + greeting.txt + voice.txt + tools.txt
  ↓
Herramientas Ahootsa
  ├─ ask_ollama.py → Ollama local
  ├─ camera_pc.py → webcam del PC en simulación
  ├─ play_emotion.py → emociones/movimiento/sonido
  └─ herramientas Memory → juego de parejas
```

## Flujo con Ollama

```text
Usuario pregunta algo
  ↓
Modelo decide usar ask_ollama
  ↓
ask_ollama.py llama a Ollama local
  ↓
Ollama responde usando el modelo ahootsa-local:latest
  ↓
Reachy habla la respuesta
```

Configuración relacionada:

```text
ask_ollama.py
instructions.txt
RECREAR_MODELO_OLLAMA_AHOOTSA.ps1
```

## Flujo del juego Memory

```text
Usuario: "quiero el juego de animales"
  ↓
start_memory_pairs_game.py
  ↓
memory_pairs_game_server.py
  ↓
http://localhost:7870/
  ↓
HTML visual con cartas azules
```

Después:

```text
Usuario: "uno y siete"
  ↓
Reachy dice: "Vamos a ver la uno y la siete"
  ↓
choose_memory_cards.py espera un poco
  ↓
memory_pairs_game_server.py gira las cartas
  ↓
HTML muestra cartas
  ↓
choose_memory_cards.py espera un poco
  ↓
Reachy reacciona una sola vez
```

Si falla:

```text
cartas visibles 4 segundos
  ↓
vuelven a ocultarse solas
```

Si acierta:

```text
cartas quedan visibles
  ↓
Reachy felicita
```

Al terminar:

```text
última pareja encontrada
  ↓
Reachy celebra
  ↓
espera unos segundos
  ↓
reset_current_game()
  ↓
pregunta si quiere jugar otra vez o hacer otra actividad
```

## Flujo de archivos JSON del juego

```text
animales.json
ciudades.json
alimentos.json
  ↓
memory_pairs_game_server.py carga el JSON
  ↓
crea 8 cartas: 4 parejas
  ↓
HTML muestra las cartas
```

## Flujo de voz y saludo

```text
voice.txt → voz elegida
greeting.txt → saludo inicial
instructions.txt → idioma, identidad y comportamiento
```

Valores actuales:

```text
voice.txt = Sohee
greeting.txt = saludo en castellano como Ahootsa
```
