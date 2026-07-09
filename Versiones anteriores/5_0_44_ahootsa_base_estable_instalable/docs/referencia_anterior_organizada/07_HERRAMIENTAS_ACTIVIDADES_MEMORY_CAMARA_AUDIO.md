# 07 — Herramientas, actividades, Memory, cámara y audio

## 1. Sistema de herramientas

El modelo conversacional principal puede llamar herramientas declaradas en `tools.txt`. Las herramientas son funciones Python instaladas en paquetes oficiales o propios.

Ejemplos de herramientas oficiales:

```text
camera
dance
stop_dance
play_emotion
stop_emotion
move_head
go_to_sleep
remember
forget
idle_do_nothing
```

Ejemplos Ahootsa:

```text
ask_ollama
start_memory_pairs_game
choose_memory_cards
list_memory_pairs_games
hint_memory_pairs_game
play_panel_dance_activity
list_panel_dances_activities
camera_pc
```

## 2. `ask_ollama`

Función: consultar la IA local de Ollama sin sustituir el backend conversacional principal.

Configuración:

```text
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:3b
```

Uso esperado:

```text
Usuario: pregunta a Ollama...
Modelo principal: llama herramienta ask_ollama
Ollama: responde localmente
Ahootsa: transmite respuesta
```

Problemas típicos:

```text
- Ollama no está arrancado.
- Modelo configurado no existe.
- El modelo principal no decide llamar a ask_ollama.
- Timeout demasiado largo.
- El frontend no muestra la respuesta aunque el backend la devuelva.
```

## 3. Memory / juego de parejas

Juegos documentados:

```text
animales
ciudades
alimentos
```

Flujo:

```text
start_memory_pairs_game(game_id, reset, open_browser, port)
choose_memory_cards(first_card, second_card)
```

Resultados:

```text
match
miss
duplicate_ignored
finished
```

La herramienta `choose_memory_cards` puede devolver muchos campos equivalentes para asegurar que el modelo o frontend encuentren el texto:

```text
message
text
answer
content
response
final_response
spoken_response
tts_text
message_for_user
robot_say
assistant_response
speak
say
tool_summary
```

Esto es útil para compatibilidad, pero puede aumentar ruido en logs.

## 4. Emociones y bailes

Herramientas relevantes:

```text
play_emotion
play_emotion_with_audio
play_panel_dance_activity
list_panel_dances_activities
```

Los logs pueden mostrar:

```text
motion.ok=true
mode=EmotionQueueMove
audio.ok=false
pygame not installed or not importable
```

Esto significa que el movimiento funciona, pero el audio `.ogg` de la emoción no se reproduce.

## 5. Audio de Windows

Fuentes de audio posibles:

```text
- voz principal Ahootsa / backend realtime
- speechSynthesis del navegador
- pyttsx3
- SAPI Windows
- winsound / beeps
- audio pygame/gstreamer de emociones
```

Regla recomendada:

```text
Solo debe hablar Ahootsa.
No debe sonar voz Windows ni navegador.
No deben sonar beeps Windows durante actividades, salvo que se decida expresamente.
```

Bloqueos aplicados en versiones recientes:

```text
speechSynthesis bloqueado
pyttsx3 bloqueado
SAPI Windows bloqueado
winsound.Beep / MessageBeep bloqueados
```

## 6. Cámara oficial Reachy/MuJoCo

La herramienta oficial `camera.py` usa:

```python
deps.reachy_mini.media.get_frame()
```

Por tanto obtiene la imagen desde el sistema media de Reachy/MuJoCo/robot. No es la webcam del PC.

## 7. Cámara PC

La cámara PC requiere módulo propio. Puede implementarse de dos formas:

### Navegador/WebView

```javascript
navigator.mediaDevices.getUserMedia({ video: true, audio: false })
```

Ventajas:

```text
- no requiere OpenCV
- pide permisos al usuario
- funciona en navegador moderno
```

Limitaciones:

```text
- depende de permisos de Windows/WebView
- puede fallar si el Desktop Control bloquea getUserMedia
```

### Python/OpenCV

```python
cv2.VideoCapture(0)
```

Ventajas:

```text
- control directo desde Python
- útil para diagnóstico
```

Limitaciones:

```text
- requiere instalar opencv-python
- puede bloquear si otra app usa cámara
```

## 8. Rutas de cámara PC recomendadas

```text
GET  /camera/health
GET  /camera/page
POST /camera/upload
GET  /camera/latest
```

Guardar fotos en:

```text
D:\RITXI\logs\camera
```

## 9. Recomendación de estabilidad

Para demos y pruebas:

```text
- desactivar beeps Windows
- evitar audio pygame si falta pygame
- reducir post_play_wait_seconds
- no encadenar emoción + habla + herramienta si no es necesario
- limitar tools.txt a herramientas realmente usadas
```
