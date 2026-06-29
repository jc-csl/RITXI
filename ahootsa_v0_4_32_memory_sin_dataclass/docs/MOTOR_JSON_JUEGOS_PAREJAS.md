# v0.4.30 — Motor JSON de juegos de parejas

## Qué cambia

Antes había un único juego fijo de animales.

Ahora hay un motor genérico:

```text
memory_pairs_game_server.py
memory_pairs_generic.html
```

y los contenidos están en JSON:

```text
animales.json
ciudades.json
alimentos.json
```

## Juegos incluidos

### 1. Animales

```text
animal + grupo
rana → anfibio
águila → ave
delfín → mamífero
```

### 2. Ciudades europeas

```text
ciudad + monumento
París → Torre Eiffel
Roma → Coliseo
Praga → Puente de Carlos
```

### 3. Alimentos

```text
alimento + grupo alimentario
manzana → fruta
pan → cereal
lentejas → legumbre
```

## Cómo crear más juegos

Crear un nuevo archivo JSON en el perfil Ahootsa, por ejemplo:

```text
profesiones.json
```

con esta estructura:

```json
{
  "id": "profesiones",
  "title": "Juego de parejas: profesiones y herramientas",
  "subtitle": "Busca parejas: profesión + herramienta.",
  "theme": "Profesiones",
  "left_title": "profesión",
  "right_title": "herramienta",
  "start_message": "Busca una profesión y su herramienta.",
  "finish_title": "¡Juego terminado!",
  "facts_title": "Datos rápidos",
  "pairs": [
    {
      "id": "doctor",
      "left": "médico",
      "left_icon": "🧑‍⚕️",
      "right": "estetoscopio",
      "right_icon": "🩺",
      "fact": "El estetoscopio ayuda a escuchar sonidos del cuerpo."
    }
  ]
}
```

Recomendación: 8 parejas para mantener 16 cartas.

## Herramientas del robot

```text
list_memory_pairs_games
start_memory_pairs_game
choose_memory_cards
reset_memory_pairs_game
memory_pairs_game_status
```

## Prueba sin Desktop

```powershell
powershell -ExecutionPolicy Bypass -File .\PROBAR_JUEGOS_PAREJAS_JSON.ps1
```

## Reparar instalación

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_JUEGOS_PAREJAS_JSON.ps1
```

## Frases de prueba

```text
quiero un juego de parejas
quiero el juego de animales
quiero el juego de ciudades
quiero el juego de alimentos
levanta la 1 y la 5
```


## v0.4.30 — Juegos visuales simples

Los juegos de parejas ahora tienen:

```text
- 4 parejas / 8 cartas
- cartas grandes
- número grande en el dorso
- pantalla solo con cartas
```

El robot lleva las instrucciones, los ánimos, los aciertos y el final.


## v0.4.30 — Memory visual con ritmo del robot

```text
- Dorso azul.
- Número blanco grande.
- Solo cartas en pantalla.
- Si no acierta, las cartas quedan visibles 3 segundos.
- El robot puede dar pistas con hint_memory_pairs_game.
```
