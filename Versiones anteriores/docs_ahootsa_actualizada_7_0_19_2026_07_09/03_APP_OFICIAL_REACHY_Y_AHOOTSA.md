# 03 — App oficial Reachy Mini Conversation App y Ahootsa

## 1. App oficial

`reachy_mini_conversation_app` aporta:

```text
- interfaz web oficial;
- conexión Hugging Face Realtime;
- gestión de perfiles;
- carga de tools;
- micrófono, audio y conversación;
- herramientas oficiales del robot;
- cámara oficial Reachy/MuJoCo;
- movimientos, emociones y estado.
```

Ahootsa no debe duplicar ese núcleo. Debe apoyarse en él.

## 2. App Ahootsa

Nombre de app registrada:

```text
ahootsa_realtime_ollama_app
```

Paquete instalado:

```text
ahootsa_realtime_ollama_desktop_app
```

Entrada esperada:

```text
ahootsa_realtime_ollama_app = ahootsa_realtime_ollama_desktop_app.main:AhootsaRealtimeOllamaApp
```

En diagnóstico debe aparecer algo parecido a:

```text
REACHY_MINI_APPS_ENTRYPOINTS [
  ('ahootsa_realtime_ollama_app', 'ahootsa_realtime_ollama_desktop_app.main:AhootsaRealtimeOllamaApp'),
  ('reachy_mini_conversation_app', 'reachy_mini_conversation_app.main:ReachyMiniConversationApp')
]
```

## 3. Carga de herramientas

En una ejecución correcta, el log de la app oficial debe mostrar carga de perfil externo:

```text
Loading tools for profile: ahootsa7_realtime_es
Loading external profile 'ahootsa7_realtime_es' from ...\ahootsa_realtime_ollama_desktop_app\profiles\ahootsa7_realtime_es
```

Y herramientas como:

```text
ask_ollama
camera_pc
explore_image
start_memory_pairs_game
choose_memory_cards
memory_pairs_game_status
list_emotions
play_emotion
list_panel_dances_activities
play_panel_dance_activity
list_community_dances
play_community_dance
move_head
task_status
task_cancel
```

## 4. Caso especial: `play_emotion`

Ahootsa necesita una versión controlada de `play_emotion`, pero no debe colocarla en:

```text
ahootsa_realtime_ollama_desktop_app/tools/play_emotion.py
```

porque puede chocar con la herramienta oficial.

La ubicación correcta es:

```text
ahootsa_realtime_ollama_desktop_app/profiles/ahootsa7_realtime_es/play_emotion.py
```

El diagnóstico correcto muestra:

```text
tools/play_emotion.py: exists=False
profiles/ahootsa7_realtime_es/play_emotion.py: exists=True
```

## 5. Colisiones históricas

Problemas ya tratados en la serie 7:

```text
- perfiles Ahootsa antiguos copiados dentro de paquetes oficiales;
- tools Ahootsa antiguas copiadas dentro de paquetes oficiales;
- instalaciones pip corruptas sin RECORD;
- colisión con nombres como ask_ollama, camera_pc, memory, etc.;
- colisión potencial con play_emotion si se coloca como tool externa normal.
```

La instalación de versiones recientes limpia residuos Ahootsa de ubicaciones oficiales sin borrar herramientas oficiales.
