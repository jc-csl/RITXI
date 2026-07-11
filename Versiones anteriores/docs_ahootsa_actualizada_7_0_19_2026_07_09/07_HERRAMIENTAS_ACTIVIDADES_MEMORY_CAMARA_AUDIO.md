# 07 — Herramientas, actividades, Memory, cámara, audio, bailes y emociones

## 1. Herramientas Ahootsa principales

```text
ask_ollama                    consulta auxiliar a Ollama
camera_pc                     cámara PC
explore_image                 análisis de imagen/foto
start_memory_pairs_game        inicia juego de parejas
choose_memory_cards            elige dos cartas por voz
reset_memory_pairs_game        reinicia Memory
memory_pairs_game_status       estado del juego
list_memory_pairs_games        juegos disponibles
hint_memory_pairs_game         pista del juego
list_panel_dances_activities   lista bailes/emociones en español
play_panel_dance_activity      ejecuta baile/emoción desde alias español
list_community_dances          lista recursos de comunidad
play_community_dance           reproduce recurso de comunidad
```

## 2. Juego de parejas Memory

Estado actual:

```text
- integrado en el mismo servidor 7860;
- se visualiza dentro del iframe del panel /ahootsa;
- puede abrirse también en pantalla grande con /memory/page;
- voz y panel deben compartir el mismo estado;
- las cartas se muestran con imagen/icono, no con número invertido;
- tiempo de visualización configurable.
```

Rutas:

```text
/memory/page?game_id=animales&reset=0
/memory/state
/memory/games
/memory/choose
/memory/reset
```

Juegos conocidos:

```text
animales
alimentos
```

Frases de voz esperadas:

```text
abre juego de parejas
elige tres y cinco
prueba uno y dos
reinicia el juego
```

Respuestas deseadas:

```text
Acierto: felicitar, animar y pedir otros dos números.
Fallo: decir que no eran pareja, animar a intentar otra vez, opcionalmente añadir una curiosidad breve.
Final: felicitar y ofrecer volver a jugar o salir.
```

Evitar respuestas desfasadas como:

```text
Míralas con calma
```

si las cartas ya se han ocultado.

## 3. Cámara PC frente a cámara MuJoCo

Problema detectado:

```text
Al analizar imagen, la app podía describir el suelo de cuadros azules de MuJoCo.
```

Causa:

```text
Se estaba usando la cámara oficial de Reachy/MuJoCo en vez de la cámara PC.
```

Criterio actual:

```text
analizar imagen real / foto del entorno → cámara PC
mirar entorno del robot/simulación       → cámara oficial Reachy/MuJoCo
```

Fotos reales:

```text
D:\RITXI\fotos
```

## 4. Audio de emociones

Dependencia:

```text
pygame
```

La instalación reciente comprueba `pygame`. En consola puede aparecer:

```text
pygame 2.6.1
Hello from the pygame community
```

Eso no es un error.

## 5. Bailes y emociones

Recursos comprobados en la librería local:

```text
D:\RITXI\reachy-mini-emotions-library
```

Identificadores técnicos importantes:

```text
dance1
dance2
dance3
welcoming2
success1
calming1
electric1
```

Cada recurso debe tener:

```text
<id>.json
<id>.ogg
```

Ejemplo:

```text
dance2.json
dance2.ogg
```

Alias naturales:

```text
baile uno / play / olay        → dance1
baile dos / play dos / olay dos → dance2
baile tres / play tres          → dance3
saludo / saludo ahootsa         → welcoming2
celebración                     → success1
calma                           → calming1
eléctrico                       → electric1
```

## 6. Estado validado

En 7.0.19 se ha comprobado que los bailes se reproducen desde panel/prueba directa. Eso valida:

```text
- recursos existentes;
- play_emotion del perfil funcionando;
- play_panel_dance_activity lanzando acción;
- MuJoCo recibiendo y ejecutando movimiento.
```

Si por voz no funciona pero desde panel sí, el problema ya no es de recurso ni de reproducción, sino de selección de herramienta por el modelo remoto.
