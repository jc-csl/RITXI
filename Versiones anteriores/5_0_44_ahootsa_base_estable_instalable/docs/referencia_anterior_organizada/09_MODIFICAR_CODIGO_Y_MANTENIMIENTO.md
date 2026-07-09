# 09 — Modificar código y mantenimiento

## 1. Regla principal

Antes de modificar, identificar qué capa se quiere cambiar:

```text
Lanzamiento       -> PowerShell
App Ahootsa       -> ahootsa_realtime_ollama_desktop_app
Conversación base -> reachy_mini_conversation_app
Perfil            -> instructions.txt / tools.txt / voice.txt / greeting.txt
Ollama            -> ask_ollama.py o endpoints /ollama/ask
Memory            -> start_memory_pairs_game.py / choose_memory_cards.py
Cámara PC         -> /camera/page / /camera/upload / camera_pc.py
Robot/MuJoCo      -> herramientas oficiales y daemon
```

## 2. Cambiar comportamiento conversacional

Modificar:

```text
profiles/ahootsa_realtime_es/instructions.txt
```

Cambios típicos:

```text
- estilo más natural
- respuestas más breves
- una pregunta cada vez
- cuándo usar IA local
- cómo guiar actividades
- cómo responder si no entiende audio
```

Después reiniciar app o re-seleccionar perfil si el backend permite recarga rápida.

## 3. Cambiar herramientas disponibles

Modificar:

```text
tools.txt
```

Recomendación:

```text
No listar herramientas que no se usan.
No duplicar herramientas equivalentes.
No dejar tools experimentales en producción.
```

Muchas herramientas pueden ralentizar la decisión del modelo.

## 4. Cambiar Ollama

Modificar:

```text
ask_ollama.py
OLLAMA_MODEL
OLLAMA_BASE_URL
AHOOTSA_OLLAMA_TIMEOUT_SECONDS
```

Modelo recomendado:

```text
llama3.2:3b
```

Timeout recomendado para agilidad:

```text
15-25 segundos
```

Prompt recomendado para conversación natural:

```text
Responde en castellano claro, breve y natural. Usa frases cortas.
```

## 5. Cambiar Hugging Face principal

Variables:

```text
HF_REALTIME_CONNECTION_MODE=deployed
HF_REALTIME_CONNECTION_MODE=local
HF_REALTIME_WS_URL=ws://127.0.0.1:8765/v1/realtime
```

No intentar cambiar el modelo principal con:

```text
MODEL_NAME
BACKEND_PROVIDER
```

porque la app oficial moderna los ignora.

## 6. Cambiar cámara PC

Si se usa navegador:

```text
HTML/JS de /camera/page
endpoint /camera/upload
directorio D:\RITXI\logs\camera
```

Si se usa OpenCV:

```text
camera_pc.py
opencv-python en apps_venv
índice de cámara 0, 1, 2...
```

## 7. Cambiar audio

Revisar:

```text
speechSynthesis
pyttsx3
winsound
pygame
gstreamer
voice.txt
variables VOICE/AHOOTSA_VOICE
```

Regla estable:

```text
La voz de conversación debe salir por un único canal.
Los sonidos de actividad no deben pisar la voz.
```

## 8. Cambiar scripts PowerShell

Recomendaciones:

```text
- param(...) siempre al inicio.
- Evitar switch mal pasados.
- No borrar la carpeta desde la que se está ejecutando el script.
- Usar timestamp por ejecución.
- Registrar variables de IA y puertos al arranque.
```

## 9. Cambiar instalación

Versiones modernas completas deben incluir:

```text
LANZAR_AHOOTSA_5_0_xx.ps1
LANZAR_AHOOTSA_OLLAMA_5_0_xx.cmd
0_INSTALAR_O_ACTUALIZAR_AHOOTSA_5_0_xx.ps1
1_COMPROBAR_IA_CAMARA_5_0_xx.ps1
2_RESUMIR_LOGS_5_0_xx.ps1
3_ARCHIVAR_VERSIONES_ANTIGUAS.ps1
tools/patch_ahootsa_5_0_xx.py
docs/
README.md
```

## 10. Rendimiento y conversación más natural

Factores que ralentizan:

```text
- modelo remoto con latencia de red
- modelo local grande
- timeout largo de Ollama
- demasiadas herramientas
- movimientos/emociones con esperas post-play
- audio de emociones fallando y haciendo fallback
- cámara con bloqueo
```

Opciones para agilizar:

```text
- usar llama3.2:3b en Ollama
- limitar respuesta a 2-3 frases
- reducir tools.txt
- desactivar beeps y audio de emoción si no aportan
- reducir AHOOTSA_POST_PLAY_WAIT_SECONDS
- no llamar a Ollama si no se pide explícitamente
- mostrar estado de backend en pantalla
```

## 11. Control de versiones

Cada versión completa debe ser autónoma y documentada. Evitar parches dependientes de carpetas anteriores.

Regla actual solicitada:

```text
Cada nueva versión debe ser completa y traer sus scripts de instalación/lanzamiento.
```
