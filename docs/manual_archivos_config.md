# manual_archivos_config.md  
# Manual de archivos de configuración — Ahootsa v0.4.57

Versión del manual: 2026-07-01  
Proyecto: **Ahootsa Realtime Ollama para Reachy Mini Desktop**  
Perfil principal: **ahootsa_realtime_es**

---

## 1. Resumen rápido

La configuración de Ahootsa se reparte en cuatro grupos:

```text
1. Configuración de la app Python
2. Perfil conversacional Ahootsa
3. Herramientas invocables por la IA
4. Conocimientos específicos de actividades
```

La carpeta más importante es:

```text
src\ahootsa_realtime_ollama_desktop_app\profiles\ahootsa_realtime_es
```

Ahí se guardan:

```text
- prompt del perfil
- saludo
- voz
- herramientas disponibles
- juegos Memory
- emociones
- dances
- alias en español
- conocimiento de actividades
```

---

## 2. Ubicaciones principales

### 2.1. Carpeta raíz del proyecto

Ejemplo:

```text
D:\RITXI\ahootsa_v0_4_47_mujoco_dances_library
```

### 2.2. Perfil fuente Ahootsa

```text
D:\RITXI\ahootsa_v0_4_47_mujoco_dances_library
└── src
    └── ahootsa_realtime_ollama_desktop_app
        └── profiles
            └── ahootsa_realtime_es
```

Ruta directa:

```text
D:\RITXI\ahootsa_v0_4_47_mujoco_dances_library\src\ahootsa_realtime_ollama_desktop_app\profiles\ahootsa_realtime_es
```

### 2.3. Copias instaladas en Reachy Mini Desktop

El perfil puede estar copiado en varias rutas. Las más habituales son:

```text
C:\Users\Alumno\AppData\Local\Reachy Mini Control\user_personalities\ahootsa_realtime_es
C:\Users\Alumno\AppData\Local\Reachy Mini Control\profiles\ahootsa_realtime_es
C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es
C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Lib\site-packages\reachy_talk_data\profiles\ahootsa_realtime_es
```

La ruta más importante en ejecución suele ser:

```text
C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es
```

---

## 3. Configuración de la aplicación

---

### 3.1. `pyproject.toml`

Ubicación:

```text
D:\RITXI\ahootsa_v0_4_47_mujoco_dances_library\pyproject.toml
```

Invocación:

```powershell
pip install -e .
```

Función:

Registra la aplicación Ahootsa dentro de Reachy Mini Desktop.

Contenido clave:

```toml
[project.entry-points."reachy_mini_apps"]
ahootsa_realtime_ollama_app = "ahootsa_realtime_ollama_desktop_app.main:AhootsaRealtimeOllamaApp"
```

Esto permite que Desktop vea la app:

```text
ahootsa_realtime_ollama_app
```

---

### 3.2. `main.py`

Ubicación:

```text
src\ahootsa_realtime_ollama_desktop_app\main.py
```

Invocación:

```text
ahootsa_realtime_ollama_app
```

Función:

Es el wrapper principal. Arranca la app oficial de conversación y fija variables importantes:

```text
PROFILE_NAME = ahootsa_realtime_es
OLLAMA_MODEL = ahootsa-local:latest
VOICE = Sohee
IDENTITY = Ahootsa
MEMORY_REACTION_ENABLED = 0
IDLE_REMINDER_ENABLED = 0
DANCES_LIBRARY_DIR = D:\RITXI\reachy-mini-dances-library
```

Variables importantes:

```text
REACHY_MINI_CUSTOM_PROFILE=ahootsa_realtime_es
REACHY_MINI_PROFILE=ahootsa_realtime_es
AHOOTSA_NAME=Ahootsa
ASSISTANT_NAME=Ahootsa
ROBOT_NAME=Ahootsa
AHOOTSA_VOICE=Sohee
AHOOTSA_DANCES_LIBRARY_DIR=D:\RITXI\reachy-mini-dances-library
AHOOTSA_MEMORY_REACTION_ENABLED=0
AHOOTSA_IDLE_REMINDER_ENABLED=0
```

---

## 4. Perfil conversacional

---

### 4.1. `instructions.txt`

Ubicación:

```text
profiles\ahootsa_realtime_es\instructions.txt
```

Invocación:

Lo carga la app oficial como prompt del sistema/perfil.

Función:

Define el comportamiento global de Ahootsa:

```text
- identidad
- idioma
- tono
- reglas de conversación
- reglas de Memory
- reglas de emociones
- reglas de dances
- cuándo usar cada herramienta
```

Fragmento crítico:

```text
Tu nombre es Ahootsa.
Cuando te pregunten cómo te llamas, responde: "Soy Ahootsa."
No digas que te llamas Reachy Mini.
Reachy Mini es solo la plataforma física/técnica, no tu nombre.
```

Regla crítica del Memory:

```text
Una jugada de Memory = una llamada a choose_memory_cards y ninguna herramienta más.
```

Regla de dances comunitarios:

```text
Si el usuario pide "haz un dance de la librería", usa play_community_dance.
Si pide "asiente", usa play_community_dance con yeah_nod o simple_nod.
Si pide "haz el baile de gallina", usa chicken_peck.
```

---

### 4.2. `greeting.txt`

Ubicación:

```text
profiles\ahootsa_realtime_es\greeting.txt
```

Invocación:

Lo usa el perfil como saludo inicial.

Contenido:

```text
¡Hola! Soy Ahootsa. Estoy lista para ayudarte. ¿Qué quieres hacer?
```

Función:

Evita el saludo oficial tipo “Hi there, I’m Reachy Mini”.

---

### 4.3. `voice.txt`

Ubicación:

```text
profiles\ahootsa_realtime_es\voice.txt
```

Contenido:

```text
Sohee
```

Función:

Indica la voz deseada.

---

### 4.4. `tools.txt`

Ubicación:

```text
profiles\ahootsa_realtime_es\tools.txt
```

Invocación:

La app lo lee para saber qué herramientas puede invocar el modelo.

Contenido actual:

```text
dance
stop_dance
play_emotion
play_emotion_with_audio
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
play_panel_dance_activity
list_panel_dances_activities
list_community_dances
play_community_dance
```

Función:

Actúa como índice de capacidades.

Si una herramienta no aparece aquí, normalmente la IA no podrá usarla.

---

## 5. Conocimiento específico de actividades

---

### 5.1. `actividades_disponibles.txt`

Ubicación:

```text
profiles\ahootsa_realtime_es\actividades_disponibles.txt
```

Invocación:

No es una herramienta. Es conocimiento textual del perfil.

Función:

Describe qué actividades puede ofrecer Ahootsa.

Contenido esperado:

```text
Juegos Memory:
- animales
- ciudades
- alimentos

Dances comunitarios:
- simple_nod
- yeah_nod
- chicken_peck
- dizzy_spin
- groovy_sway_and_roll
```

---

## 6. Juego Memory

---

### 6.1. `start_memory_pairs_game.py`

Ubicación:

```text
profiles\ahootsa_realtime_es\start_memory_pairs_game.py
```

Invocación:

```text
start_memory_pairs_game(game_id="animales")
start_memory_pairs_game(game_id="ciudades")
start_memory_pairs_game(game_id="alimentos")
```

Función:

Arranca el servidor local del Memory y abre:

```text
http://localhost:7870/
```

---

### 6.2. `choose_memory_cards.py`

Ubicación:

```text
profiles\ahootsa_realtime_es\choose_memory_cards.py
```

Invocación:

```text
choose_memory_cards(first_card=1, second_card=3)
```

Función:

Gira dos cartas.

En la versión estable actual:

```text
- No ejecuta movimiento interno.
- No ejecuta audio interno.
- No llama a emociones.
- Devuelve una frase para que Ahootsa hable.
- Evita bloquear el micrófono.
```

Esto se hizo porque las emociones dentro del juego podían bloquear la escucha.

---

### 6.3. `memory_pairs_game_server.py`

Ubicación:

```text
profiles\ahootsa_realtime_es\memory_pairs_game_server.py
```

Invocación:

Lo importan internamente:

```text
start_memory_pairs_game.py
choose_memory_cards.py
reset_memory_pairs_game.py
memory_pairs_game_status.py
hint_memory_pairs_game.py
```

Función:

Es el motor del juego Memory:

```text
- crea cartas
- mezcla cartas
- comprueba parejas
- mantiene estado
- sirve la web local
- controla fallos y aciertos
- mantiene cartas visibles 4 segundos tras fallo
```

---

### 6.4. `memory_pairs_generic.html`

Ubicación:

```text
profiles\ahootsa_realtime_es\memory_pairs_generic.html
```

Invocación:

Lo sirve el motor Memory en:

```text
http://localhost:7870/
```

Función:

Interfaz visual del juego:

```text
- cartas grandes
- dorso azul
- números blancos
- 4 parejas
- 8 cartas
```

---

### 6.5. `animales.json`

Ubicación:

```text
profiles\ahootsa_realtime_es\animales.json
```

Invocación:

```text
start_memory_pairs_game(game_id="animales")
```

Función:

Contenido del Memory de animales.

Ejemplos de parejas:

```text
rana ↔ anfibio
águila ↔ ave
salmón ↔ pez
delfín ↔ mamífero
```

---

### 6.6. `ciudades.json`

Ubicación:

```text
profiles\ahootsa_realtime_es\ciudades.json
```

Invocación:

```text
start_memory_pairs_game(game_id="ciudades")
```

Función:

Contenido del Memory de ciudades.

Ejemplos de parejas:

```text
París ↔ Torre Eiffel
Roma ↔ Coliseo
Londres ↔ Big Ben
Praga ↔ Puente de Carlos
```

---

### 6.7. `alimentos.json`

Ubicación:

```text
profiles\ahootsa_realtime_es\alimentos.json
```

Invocación:

```text
start_memory_pairs_game(game_id="alimentos")
```

Función:

Contenido del Memory de alimentos.

Ejemplos de parejas:

```text
manzana ↔ fruta
zanahoria ↔ hortaliza
pan ↔ cereal
lentejas ↔ legumbre
```

---

### 6.8. Otras herramientas Memory

#### `reset_memory_pairs_game.py`

Invocación:

```text
reset_memory_pairs_game()
```

Función:

Reinicia el juego activo.

#### `memory_pairs_game_status.py`

Invocación:

```text
memory_pairs_game_status()
```

Función:

Devuelve estado actual del juego.

#### `list_memory_pairs_games.py`

Invocación:

```text
list_memory_pairs_games()
```

Función:

Lista juegos disponibles:

```text
animales
ciudades
alimentos
```

#### `hint_memory_pairs_game.py`

Invocación:

```text
hint_memory_pairs_game()
```

Función:

Da una pista.

---

## 7. Emociones oficiales

---

### 7.1. `play_emotion.py`

Ubicación:

```text
profiles\ahootsa_realtime_es\play_emotion.py
```

Invocación:

```text
play_emotion(emotion="greeting")
play_emotion(emotion="success")
play_emotion(emotion="calming")
play_emotion(emotion="thinking")
```

Función:

Reproduce una emoción con:

```text
- movimiento JSON
- audio OGG asociado, si existe
```

Dataset local esperado:

```text
D:\RITXI\reachy-mini-emotions-library
```

Ejemplos detectados anteriormente:

```text
amazed1
anxiety1
attentive1
boredom1
calming1
cheerful1
come1
confused1
dance1
dance2
dance3
success1
welcoming1
welcoming2
laughing2
thoughtful1
```

---

### 7.2. `play_emotion_with_audio.py`

Ubicación:

```text
profiles\ahootsa_realtime_es\play_emotion_with_audio.py
```

Invocación:

```text
play_emotion_with_audio(emotion="greeting")
play_emotion_with_audio(emotion="success")
```

Función:

Wrapper explícito para pedir emoción con audio.

---

## 8. Dances y actividades del panel

---

### 8.1. `play_panel_dance_activity.py`

Ubicación:

```text
profiles\ahootsa_realtime_es\play_panel_dance_activity.py
```

Invocación:

```text
play_panel_dance_activity(activity="dance1")
play_panel_dance_activity(activity="dance2")
play_panel_dance_activity(activity="dance3")
play_panel_dance_activity(activity="electric1")
```

Función:

Reproduce movimientos/actividades de la librería local de emociones o movimientos ya detectados.

---

### 8.2. `list_panel_dances_activities.py`

Ubicación:

```text
profiles\ahootsa_realtime_es\list_panel_dances_activities.py
```

Invocación:

```text
list_panel_dances_activities()
```

Función:

Lista actividades y movimientos disponibles parecidos a los del panel.

---

## 9. Nueva librería comunitaria de dances

---

### 9.1. `community_dances.json`

Ubicación:

```text
profiles\ahootsa_realtime_es\community_dances.json
```

Invocación:

Lo usan:

```text
list_community_dances.py
play_community_dance.py
```

Función:

Es el archivo de configuración nuevo donde se guardan:

```text
- nombre técnico del dance
- nombre en español
- alias en español
- dataset de origen
- ruta local por defecto
```

Contenido conceptual:

```json
{
  "dataset": "pollen-robotics/reachy-mini-dances-library",
  "default_local_dir": "D:\\RITXI\\reachy-mini-dances-library",
  "moves": [
    {
      "id": "simple_nod",
      "name_es": "asentir simple",
      "aliases": ["asiente", "asentir", "nod"]
    },
    {
      "id": "chicken_peck",
      "name_es": "picoteo de gallina",
      "aliases": ["gallina", "picoteo", "chicken"]
    }
  ]
}
```

Este archivo es el sitio principal para definir nombres españoles.

---

### 9.2. `list_community_dances.py`

Ubicación:

```text
profiles\ahootsa_realtime_es\list_community_dances.py
```

Invocación:

```text
list_community_dances()
```

Función:

Permite que Ahootsa liste sus dances comunitarios.

Ejemplo de petición por voz:

```text
Ahootsa, dime qué bailes comunitarios sabes hacer.
```

Respuesta esperada:

```text
Puedo hacer simple nod, yeah nod, chicken peck, dizzy spin...
```

---

### 9.3. `play_community_dance.py`

Ubicación:

```text
profiles\ahootsa_realtime_es\play_community_dance.py
```

Invocación:

```text
play_community_dance(dance="simple_nod")
play_community_dance(dance="chicken_peck")
play_community_dance(dance="groovy_sway_and_roll")
```

Función:

Reproduce un dance comunitario desde la librería:

```text
pollen-robotics/reachy-mini-dances-library
```

Importante:

```text
Esta librería es solo movimiento.
No tiene audio OGG asociado.
```

---

### 9.4. `INSTALAR_DANCES_LIBRARY_AHOOTSA.ps1`

Ubicación:

```text
D:\RITXI\ahootsa_v0_4_47_mujoco_dances_library\INSTALAR_DANCES_LIBRARY_AHOOTSA.ps1
```

Invocación:

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_DANCES_LIBRARY_AHOOTSA.ps1
```

Función:

Descarga o instala los JSON de la librería comunitaria en:

```text
D:\RITXI\reachy-mini-dances-library
```

También fija:

```text
AHOOTSA_DANCES_LIBRARY_DIR=D:\RITXI\reachy-mini-dances-library
```

---

### 9.5. `DIAGNOSTICAR_DANCES_LIBRARY_AHOOTSA.ps1`

Ubicación:

```text
test\DIAGNOSTICAR_DANCES_LIBRARY_AHOOTSA.ps1
```

Invocación:

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_DANCES_LIBRARY_AHOOTSA.ps1
```

Función:

Comprueba:

```text
- si existe la librería local
- cuántos JSON hay
- qué dances están configurados
- si community_dances.json existe
```

---

## 10. Nombres españoles para pedir emotions y dances

Sí, es posible definir nombres en español.

Hay dos niveles:

```text
1. Alias internos en los archivos de configuración.
2. Reglas en instructions.txt para que Ahootsa entienda lenguaje natural.
```

---

### 10.1. Dances comunitarios

El archivo principal es:

```text
community_dances.json
```

Ejemplo:

```json
{
  "id": "chicken_peck",
  "name_es": "picoteo de gallina",
  "aliases": ["gallina", "picoteo", "baile de gallina"]
}
```

Con eso puedes pedir:

```text
haz el baile de gallina
haz el picoteo de gallina
haz gallina
```

Y Ahootsa debe invocar:

```text
play_community_dance(dance="chicken_peck")
```

---

### 10.2. Emociones

Actualmente los alias de emociones están principalmente en:

```text
play_emotion.py
play_emotion_with_audio.py
instructions.txt
```

Ejemplos de nombres españoles recomendados:

| Nombre español | Nombre técnico probable |
|---|---|
| saludo | `greeting` / `welcoming2` |
| celebración | `success` / `success1` |
| calma | `calming` / `calming1` |
| pensar | `thinking` / `thoughtful1` |
| alegría | `happy` / `laughing2` |
| sorpresa | `amazed` / `amazed1` |
| confusión | `confused` / `confused1` |
| atención | `attentive` / `attentive1` |

Ejemplos de petición:

```text
saluda con emoción
haz una celebración
ponte alegre
haz cara de pensar
haz una emoción de calma
```

---

## 11. ¿Puede Ahootsa listar sus opciones?

Sí.

Para dances comunitarios:

```text
Ahootsa, dime qué dances comunitarios sabes hacer.
```

Herramienta esperada:

```text
list_community_dances()
```

Para dances/actividades del panel:

```text
Ahootsa, dime qué bailes del panel tienes.
```

Herramienta esperada:

```text
list_panel_dances_activities()
```

Para juegos Memory:

```text
Ahootsa, dime qué juegos de parejas tienes.
```

Herramienta esperada:

```text
list_memory_pairs_games()
```

Para emociones, conviene añadir una herramienta explícita en una próxima versión:

```text
list_emotions
```

Ahora mismo se pueden listar algunas desde diagnóstico, pero para conversación natural sería mejor crear:

```text
list_emotions.py
emotions_aliases.json
```

---

## 12. Propuesta de mejora recomendada

Para hacerlo más limpio, conviene crear dos archivos nuevos:

```text
emotions_aliases.json
dances_aliases_es.json
```

O mejor:

```text
emotions_catalog_es.json
dances_catalog_es.json
```

### 12.1. `emotions_catalog_es.json`

Contenido propuesto:

```json
{
  "saludo": {
    "tool": "play_emotion_with_audio",
    "id": "greeting",
    "technical": "welcoming2",
    "aliases": ["hola", "saluda", "saludo con emoción"]
  },
  "celebración": {
    "tool": "play_emotion_with_audio",
    "id": "success",
    "technical": "success1",
    "aliases": ["celebra", "bravo", "muy bien"]
  },
  "calma": {
    "tool": "play_emotion_with_audio",
    "id": "calming",
    "technical": "calming1",
    "aliases": ["tranquilo", "relájate", "calma"]
  }
}
```

### 12.2. `dances_catalog_es.json`

Contenido propuesto:

```json
{
  "baile de gallina": {
    "tool": "play_community_dance",
    "id": "chicken_peck",
    "aliases": ["gallina", "picoteo"]
  },
  "asentir": {
    "tool": "play_community_dance",
    "id": "yeah_nod",
    "aliases": ["sí", "di que sí", "asiente"]
  },
  "baile groovy": {
    "tool": "play_community_dance",
    "id": "groovy_sway_and_roll",
    "aliases": ["groovy", "balanceo"]
  }
}
```

Con esos catálogos, Ahootsa podría responder:

```text
Tengo saludos, celebraciones, calma, pensamiento, sorpresa, bailes de gallina, asentir, giro mareado y baile groovy. ¿Cuál quieres ver?
```

---

## 13. Simulador MuJoCo

---

### 13.1. `LANZAR_SIMULADOR_MUJOCO_AHOOTSA.ps1`

Ubicación:

```text
D:\RITXI\ahootsa_v0_4_47_mujoco_dances_library\LANZAR_SIMULADOR_MUJOCO_AHOOTSA.ps1
```

Invocación:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_SIMULADOR_MUJOCO_AHOOTSA.ps1
```

Función:

Lanza el daemon en modo simulación:

```text
reachy-mini-daemon --sim
```

o alternativa:

```text
python -m reachy_mini.daemon.app.main --sim
```

Después se abre Reachy Mini Desktop y se ejecuta Ahootsa.

Importante:

```text
MuJoCo normalmente abre una ventana nativa 3D.
No expone por defecto un visor web en otro puerto.
```

Para verlo en navegador habría que añadir:

```text
- noVNC
- VNC
- escritorio remoto
- streaming de la ventana
- visor WebGL propio
```

---

## 14. Resumen de archivos nuevos de v0.4.57

Archivos añadidos:

```text
profiles\ahootsa_realtime_es\community_dances.json
profiles\ahootsa_realtime_es\list_community_dances.py
profiles\ahootsa_realtime_es\play_community_dance.py
INSTALAR_DANCES_LIBRARY_AHOOTSA.ps1
LANZAR_SIMULADOR_MUJOCO_AHOOTSA.ps1
test\DIAGNOSTICAR_DANCES_LIBRARY_AHOOTSA.ps1
docs\18_MUJOCO_Y_DANCES_LIBRARY_v0_4_47.md
```

Archivos modificados:

```text
profiles\ahootsa_realtime_es\tools.txt
profiles\ahootsa_realtime_es\instructions.txt
profiles\ahootsa_realtime_es\actividades_disponibles.txt
main.py
INSTALAR_AHOOTSA_COMPLETO.ps1
README_AHOOTSA_REALTIME_OLLAMA.md
AHOOTSA_VERSION.txt
```

---

## 15. Cómo pedir las nuevas librerías en español

### Listar dances comunitarios

```text
Ahootsa, dime qué dances comunitarios sabes hacer.
Ahootsa, dime qué bailes nuevos tienes.
Ahootsa, lista los movimientos comunitarios.
```

### Ejecutar un dance comunitario

```text
Haz el baile de gallina.
Haz un simple nod.
Asiente con la cabeza.
Haz un giro mareado.
Haz un baile groovy.
Haz el movimiento de péndulo.
```

### Listar juegos

```text
¿Qué juegos de parejas tienes?
¿Qué Memory sabes hacer?
Dime tus juegos de cartas.
```

### Ejecutar Memory

```text
Quiero el juego de animales.
Quiero el juego de ciudades.
Quiero el juego de alimentos.
```

### Elegir cartas

```text
Uno y tres.
Dos y cinco.
Levanta la cuatro y la ocho.
```

### Pedir emociones

```text
Saluda con emoción.
Celebra.
Haz una emoción de calma.
Ponte alegre.
Haz cara de pensar.
```

---

## 16. Conclusión

Sí, es posible definir nombres españoles para emotions y dances.

Ahora mismo:

```text
Dances comunitarios:
- se configuran en community_dances.json

Emociones:
- se resuelven desde play_emotion.py, play_emotion_with_audio.py e instructions.txt
```

Mejora recomendada para una versión siguiente:

```text
emotions_catalog_es.json
dances_catalog_es.json
list_emotions.py
list_all_activities.py
```

Eso permitiría que Ahootsa tuviera un catálogo completo y pudiera decir:

```text
Puedo hacer saludos, celebraciones, calma, sorpresa, asentir, baile de gallina, baile groovy y juegos de parejas.
```


---

# Anexo v0.4.57 — Catálogos españoles de emociones, dances y actividades

## Archivos nuevos

```text
profiles\ahootsa_realtime_es\emotions_catalog_es.json
profiles\ahootsa_realtime_es\dances_catalog_es.json
profiles\ahootsa_realtime_es\list_emotions.py
profiles\ahootsa_realtime_es\list_all_activities.py
REPARAR_CATALOGOS_ES_AHOOTSA.ps1
test\DIAGNOSTICAR_CATALOGOS_ES_AHOOTSA.ps1
docs\manual_archivos_config.md
```

## `emotions_catalog_es.json`

Función:

```text
Catálogo en español de emociones, reacciones y pequeños bailes de la librería de emociones.
```

Guarda:

```text
- id semántico
- technical_id real o probable
- nombre en español
- categoría
- herramienta recomendada
- alias en español
- ejemplos de petición por voz
```

Ejemplo:

```json
{
  "id": "calma",
  "technical_id": "calming1",
  "name_es": "calma",
  "category": "calma_apoyo",
  "tool": "play_emotion_with_audio",
  "aliases": ["calma", "tranquila", "relájate"]
}
```

Cómo pedirlo:

```text
haz una emoción de calma
ponte tranquila
relájate
```

## `dances_catalog_es.json`

Función:

```text
Catálogo en español de dances comunitarios de pollen-robotics/reachy-mini-dances-library.
```

Guarda:

```text
- id técnico del JSON
- nombre español
- categoría
- alias en español
- ejemplos de petición
```

Ejemplo:

```json
{
  "id": "chicken_peck",
  "name_es": "picoteo de gallina",
  "category": "animal",
  "aliases": ["gallina", "picoteo", "baile de gallina"]
}
```

Cómo pedirlo:

```text
haz el baile de gallina
haz el picoteo de gallina
```

## `list_emotions.py`

Invocación:

```text
list_emotions()
list_emotions(category="positivas")
list_emotions(only_available=true)
```

Función:

```text
Lista emociones disponibles con nombre español, id técnico, alias y disponibilidad de JSON/OGG local.
```

Peticiones por voz:

```text
dime tus emociones
qué emociones tienes
lista tus reacciones
```

## `list_all_activities.py`

Invocación:

```text
list_all_activities()
list_all_activities(detail="full")
```

Función:

```text
Lista todo lo que Ahootsa sabe hacer:
- juegos Memory
- emociones
- dances comunitarios
- actividades del panel
```

Peticiones por voz:

```text
qué sabes hacer
dime tus actividades
qué juegos y emociones tienes
lista todo lo que puedes hacer
```

## `tools.txt`

Se actualiza añadiendo:

```text
list_emotions
list_all_activities
```

## `instructions.txt`

Se actualiza con reglas:

```text
Si el usuario pregunta "¿qué sabes hacer?", usa list_all_activities.
Si pregunta "¿qué emociones tienes?", usa list_emotions.
Si pregunta "¿qué bailes o dances tienes?", usa list_community_dances o list_all_activities.
```

## Reparación directa

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_CATALOGOS_ES_AHOOTSA.ps1
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_CATALOGOS_ES_AHOOTSA.ps1
```

Resultado esperado:

```text
emotions_catalog_es.json = True
dances_catalog_es.json = True
list_emotions.py = True
list_all_activities.py = True
tool list_emotions = True
tool list_all_activities = True
```


---

# 20 — Audio GStreamer / Windows v0.4.57

## Error detectado

```text
reachy_mini.media.audio_gstreamer
gst-resource-error-quark: Failed to write to device
GstWasapi2Sink
```

## Significado

El problema está en la salida de audio de Windows usada por GStreamer/WASAPI.

Causas habituales:

```text
- cambio de dispositivo de salida mientras Ahootsa estaba abierto;
- HDMI/monitor/auriculares desconectado o dormido;
- modo exclusivo del dispositivo de sonido;
- dos sistemas de audio intentando escribir a la vez;
- driver de audio bloqueado.
```

## Reparación

Con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_AUDIO_GSTREAMER_WINDOWS_AHOOTSA.ps1
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_AUDIO_WINDOWS_AHOOTSA.ps1
```

## Reactivar audio de emociones

Solo si la conversación normal ya funciona:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_AUDIO_GSTREAMER_WINDOWS_AHOOTSA.ps1 -EnableEmotionAudio
```


---

# 21 — Play después de hablar v0.4.57

## Problema

Ahootsa decía algo como:

```text
Ahora voy a hacer el baile tres.
```

pero el movimiento/audio empezaba antes o al mismo tiempo.  
Eso producía solape de audios.

## Causa

Las herramientas de emoción/dance se ejecutan en segundo plano.  
El play puede comenzar mientras la voz principal todavía está hablando.

## Solución

Las herramientas esperan antes de ejecutar:

```text
AHOOTSA_ACTION_PLAY_DELAY_SECONDS=2.8
```

Secuencia:

```text
1. Se invoca la herramienta.
2. Ahootsa habla una frase corta.
3. La herramienta espera 2,8 segundos.
4. Se ejecuta el movimiento/audio.
```

## Herramientas afectadas

```text
play_emotion
play_emotion_with_audio
play_panel_dance_activity
play_community_dance
```

## Configurar

```powershell
powershell -ExecutionPolicy Bypass -File .\CONFIGURAR_PLAY_DESPUES_DE_HABLAR_AHOOTSA.ps1 -Seconds 2.8
```

Si la frase hablada es más larga:

```powershell
powershell -ExecutionPolicy Bypass -File .\CONFIGURAR_PLAY_DESPUES_DE_HABLAR_AHOOTSA.ps1 -Seconds 3.5
```

Sin retardo:

```powershell
powershell -ExecutionPolicy Bypass -File .\CONFIGURAR_PLAY_DESPUES_DE_HABLAR_AHOOTSA.ps1 -DisableDelay
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_SECUENCIA_AUDIO_PLAY_AHOOTSA.ps1
```

## Nota técnica

No es un hook perfecto "después de terminar TTS", porque la app oficial no expone ese evento al perfil.  
Es un retardo configurable que en la práctica evita el solape.


---

# 22 — Retardo de play en archivo de configuración v0.4.57

## Dónde se configura el retardo

El retardo se guarda ahora en un archivo de configuración del perfil:

```text
profiles\ahootsa_realtime_es\play_timing_config.json
```

En la copia instalada suele estar aquí:

```text
C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es\play_timing_config.json
```

## Campo principal

```json
{
  "action_play_delay_seconds": 2.8
}
```

Ese valor significa:

```text
esperar 2,8 segundos antes de ejecutar el movimiento/audio
```

## Qué script lo modifica

```powershell
powershell -ExecutionPolicy Bypass -File .\CONFIGURAR_PLAY_DESPUES_DE_HABLAR_AHOOTSA.ps1 -Seconds 2.8
```

El script actualiza:

```text
- variable de entorno AHOOTSA_ACTION_PLAY_DELAY_SECONDS
- play_timing_config.json del perfil fuente
- play_timing_config.json de perfiles instalados
- play_timing_config.json de perfiles fallback/default
```

## Orden de prioridad

Las herramientas leen el retardo en este orden:

```text
1. delay_before_play_seconds pasado en la llamada de herramienta
2. variable de entorno AHOOTSA_ACTION_PLAY_DELAY_SECONDS
3. profiles\ahootsa_realtime_es\play_timing_config.json
4. valor por defecto 2.8
```

## Herramientas afectadas

```text
play_emotion
play_emotion_with_audio
play_panel_dance_activity
play_community_dance
```

## Ejemplos

Retardo normal:

```powershell
powershell -ExecutionPolicy Bypass -File .\CONFIGURAR_PLAY_DESPUES_DE_HABLAR_AHOOTSA.ps1 -Seconds 2.8
```

Frases algo más largas:

```powershell
powershell -ExecutionPolicy Bypass -File .\CONFIGURAR_PLAY_DESPUES_DE_HABLAR_AHOOTSA.ps1 -Seconds 3.5
```

Sin retardo:

```powershell
powershell -ExecutionPolicy Bypass -File .\CONFIGURAR_PLAY_DESPUES_DE_HABLAR_AHOOTSA.ps1 -DisableDelay
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_SECUENCIA_AUDIO_PLAY_AHOOTSA.ps1
```

Debe mostrar:

```text
play_timing_config.json = True
usa play_timing_config = True
delay support = True
```


---

# 23 — Reparar herramientas instaladas con soporte de retardo v0.4.57

## Problema detectado

El diagnóstico podía mostrar:

```text
play_timing_config.json = True
play_emotion.py
  usa play_timing_config = False
  delay support = False
```

Eso significa:

```text
- el archivo de configuración existe;
- pero las herramientas instaladas siguen siendo versiones antiguas;
- por tanto no leen play_timing_config.json.
```

## Corrección

Nuevo script:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_HERRAMIENTAS_RETARDO_PLAY_AHOOTSA.ps1 -Seconds 2.8 -EnableEmotionAudio
```

Este script copia a los perfiles instalados:

```text
play_timing_config.json
play_emotion.py
play_emotion_with_audio.py
play_panel_dance_activity.py
play_community_dance.py
tools.txt
instructions.txt
```

## Diagnóstico esperado

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_SECUENCIA_AUDIO_PLAY_AHOOTSA.ps1
```

Debe mostrar, tanto en fuente como instalado:

```text
usa play_timing_config = True
delay support = True
```

## Nota

Después de ejecutar el script hay que cerrar completamente Reachy Mini Desktop y volver a abrirlo.


---

# 24 — Sonidos Memory y play sin solape v0.4.57

## Problemas corregidos

```text
1. En el juego de parejas ya no se escuchaban sonidos.
2. El retardo antes del play no evitaba bien el solape.
```

## Cambio de estrategia

Se abandona la estrategia:

```text
hablar primero -> esperar -> play
```

porque no siempre funcionaba con la app oficial.

La nueva estrategia es:

```text
play primero -> esperar -> respuesta corta al final
```

Así se evita que Ahootsa diga:

```text
Ahora voy a hacer el baile tres
```

mientras el audio del baile ya está sonando.

## Configuración

```text
profiles\ahootsa_realtime_es\play_timing_config.json
```

Campos principales:

```json
{
  "sequence_mode": "tool_first_wait_then_response",
  "action_play_delay_seconds": 0.0,
  "post_play_wait_seconds": 3.0
}
```

## Sonidos del Memory

Archivo nuevo:

```text
profiles\ahootsa_realtime_es\memory_sound_config.json
```

La pantalla del juego reproduce sonidos simples con Web Audio:

```text
flip
match
miss
finish
```

No usa:

```text
GStreamer
pygame
play_emotion
audio OGG de emociones
```

## Reparación

Con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_MEMORY_SONIDOS_Y_PLAY_SIN_SOLAPE_AHOOTSA.ps1 -PostPlayWaitSeconds 3.0 -EnableEmotionAudio
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_MEMORY_SONIDOS_Y_PLAY_AHOOTSA.ps1
```

Debe mostrar:

```text
web sound hook = True
needs_response True = True
post_play_wait = True
timing config = True
```


---

# 25 — Memory interactivo restaurado v0.4.57

## Problemas corregidos

```text
- El Memory ya no daba instrucciones después de levantar cartas.
- No decía si la respuesta era buena o mala.
- No reaccionaba con emoción en cada interacción.
- El final del juego no estaba suficientemente controlado.
- En dances directos se oían frases como "vale" o "ya está" durante el play.
```

## Solución

El Memory vuelve a ser una actividad guiada.

Archivo principal:

```text
profiles\ahootsa_realtime_es\memory_interaction_config.json
```

Herramienta principal:

```text
choose_memory_cards.py
```

Ahora `choose_memory_cards` hace todo esto:

```text
1. Levanta las cartas.
2. Detecta acierto, fallo o final.
3. Reproduce una única emoción:
   - acierto: success
   - fallo: calming
   - final: dance3
4. Devuelve una frase clara para que Ahootsa la diga.
5. Prohíbe llamar a otra emoción después.
```

## Frases esperadas

Acierto:

```text
Vamos a ver la 1 y la 3. ¡Muy bien! Es pareja. Elige otros dos números.
```

Fallo:

```text
Vamos a ver la 1 y la 3. Casi. No son pareja. Inténtalo de nuevo con otros dos números.
```

Final:

```text
¡Felicidades! Has terminado el juego. ¿Quieres jugar otra vez o prefieres hacer otra actividad?
```

## Dances directos

Las herramientas de play directo quedan silenciosas:

```text
play_emotion
play_emotion_with_audio
play_panel_dance_activity
play_community_dance
```

Así, si el usuario dice:

```text
haz el baile tres
```

Ahootsa no debe decir "vale" ni "ya está" durante el play.  
El baile es la respuesta.

## Reparación

Con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_MEMORY_INTERACTIVO_AHOOTSA.ps1
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_MEMORY_INTERACTIVO_AHOOTSA.ps1
```

Debe mostrar:

```text
feedback restaurado = True
reacción interna = True
final con dance = True
instrucciones inicio = True
direct play silent = True
```


---

# 26 — Fix instalación del módulo Python en Desktop v0.4.57

## Error corregido

```text
C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe:
Error while finding module specification for 'ahootsa_realtime_ollama_desktop_app.main'
ModuleNotFoundError: No module named 'ahootsa_realtime_ollama_desktop_app'
```

## Significado

Reachy Mini Desktop está intentando ejecutar:

```text
python -m ahootsa_realtime_ollama_desktop_app.main
```

pero el paquete Python de Ahootsa no está instalado o no es visible dentro del venv interno:

```text
%LOCALAPPDATA%\Reachy Mini Control\apps_venv
```

El perfil puede estar copiado correctamente, pero falta el módulo Python.

## Reparación

Con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\REINSTALAR_AHOOTSA_EN_DESKTOP.ps1
```

El script hace dos cosas:

```text
1. Instala el paquete en modo editable con pip install -e .
2. Crea un archivo .pth de seguridad dentro de site-packages apuntando a la carpeta src.
```

Archivo .pth creado:

```text
%LOCALAPPDATA%\Reachy Mini Control\apps_venv\Lib\site-packages\ahootsa_realtime_ollama_desktop_app_dev.pth
```

Contenido esperado:

```text
D:\RITXI\ahootsa_v0_4_55_fix_instalacion_modulo\src
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_INSTALACION_MODULO_AHOOTSA.ps1
```

Debe mostrar:

```text
main OK
APP_VERSION= 0.4.55
```

## Nota

Después de reparar, hay que cerrar completamente Reachy Mini Desktop y volver a abrirlo.


---

# 27 — Fix diagnóstico de importación PowerShell v0.4.57

## Qué ha pasado

La instalación editable sí llegó a completarse:

```text
Successfully installed ahootsa-realtime-ollama-desktop-app-0.4.55
```

El fallo posterior no era necesariamente del módulo, sino del propio test de importación:

```text
SyntaxError: print(python=, sys.executable)
```

Eso ocurrió porque el script usaba `python -c` con código Python entre comillas, y PowerShell puede romper esas comillas.

## Corrección

En v0.4.57, los scripts ya no usan `python -c` para el test.  
Ahora escriben un archivo temporal `.py` y ejecutan:

```text
python ahootsa_test_import_v056.py
```

## Reparación

Con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\REINSTALAR_AHOOTSA_EN_DESKTOP.ps1
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_INSTALACION_MODULO_AHOOTSA.ps1
```

Debe mostrar:

```text
main OK
APP_VERSION= 0.4.56
```


---

# 28 — Voz Sohee y secuencia Memory v0.4.57

## Problemas corregidos

```text
1. En el inicio se usaba Aiden en lugar de Sohee.
2. En Memory el orden no era natural:
   - primero se giraban cartas;
   - sonaba fallo;
   - después hablaba Ahootsa.
3. Faltaba pedir de nuevo los números tras un tiempo sin respuesta.
```

## Voz de inicio

Archivos:

```text
profiles\ahootsa_realtime_es\voice.txt
profiles\ahootsa_realtime_es\voice_startup_config.json
```

Valor esperado:

```text
Sohee
```

Script:

```powershell
powershell -ExecutionPolicy Bypass -File .\FORZAR_VOZ_INICIO_SOHEE_AHOOTSA.ps1
```

Script completo recomendado:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_SOHEE_MEMORY_SECUENCIA_AHOOTSA.ps1
```

## Secuencia Memory

Archivo:

```text
profiles\ahootsa_realtime_es\memory_sequence_config.json
```

Valores principales:

```json
{
  "flip_delay_seconds": 1.2,
  "result_sound_delay_seconds": 3.2,
  "idle_prompt_seconds": 10
}
```

Secuencia buscada:

```text
1. Ahootsa dice: "Vamos a ver la 3 y la 5."
2. La pantalla gira las cartas con retraso visual.
3. Ahootsa dice: "Casi, no son pareja."
4. Suena el fallo.
5. Ahootsa dice: "Inténtalo de nuevo. Dime otros dos números."
6. Si pasan 10 segundos sin interacción, la pantalla muestra:
   "Dime otros dos números para seguir jugando."
```

## Limitación importante

El aviso de 10 segundos se muestra en la pantalla del juego.  
Para que sea voz real de Sohee tras silencio de usuario haría falta un detector de silencio integrado en la app oficial, no solo en el perfil.

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_SOHEE_MEMORY_SECUENCIA_AHOOTSA.ps1
```

Debe mostrar:

```text
voice.txt contenido = Sohee
vamos a ver = True
dime otros dos numeros = True
ordered feedback = True
idle prompt 10s = True
delayed sound = True
```


---

# Memory interactivo + logs — v0.4.57.2

## Base

Esta versión parte de:

```text
ahootsa_v0_4_57_sohee_memory_secuencia
```

No usa las versiones posteriores.

## Problema observado

En los logs aportados, la aplicación arranca, pero:

```text
- No aparecen eventos JSONL de Ahootsa.
- Las reacciones de Memory llegan a play_emotion con sound=false.
- La herramienta no está devolviendo una respuesta compacta y clara para que el robot la diga.
```

## Correcciones

```text
1. Copia las herramientas también a la raíz de instance_path.
2. choose_memory_cards devuelve resultado compacto:
   - robot_say
   - assistant_response
   - speak
3. choose_memory_cards fuerza reacción emocional con sonido activo.
4. memory_pairs_generic.html añade sonido web de acierto/fallo como respaldo.
5. memory_pairs_game_server añade logs de jugadas.
6. Se evita devolver el state completo al LLM.
```

## Reparación

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_MEMORY_INTERACTIVO_LOGS_AHOOTSA.ps1 -EnableReactionSound
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_MEMORY_INTERACTIVO_LOGS_AHOOTSA.ps1
```

## Ver logs

```powershell
powershell -ExecutionPolicy Bypass -File .\test\VER_ULTIMOS_LOGS_AHOOTSA.ps1
```

## Esperado

Fallo:

```text
Vamos a ver la 3 y la 5. Casi, no son pareja. Inténtalo de nuevo. Dime otros dos números.
```

Acierto:

```text
Vamos a ver la 3 y la 5. ¡Muy bien! Es pareja. Elige otros dos números.
```


---

# Fix copia de perfil instalado — v0.4.57.3

## Problema detectado

El diagnóstico del usuario muestra:

```text
RAIZ_INSTANCE_PATH = correcto
FUENTE_PROFILE = correcto
INSTALADO_PROFILE = antiguo
```

Concretamente, en `INSTALADO_PROFILE` faltaban:

```text
ahootsa_debug_logger.py
logging_config.json
memory_feedback_config.json
```

y `choose_memory_cards.py` no tenía:

```text
assistant_response
feedback_emotion_restored
logging
```

Eso explica que el juego no interactúe: Reachy Mini Desktop puede estar cargando herramientas desde:

```text
%LOCALAPPDATA%\Reachy Mini Control\apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es
```

en vez de la raíz del proyecto.

## Solución

Nuevo script:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_COPIA_PERFILES_INSTALADOS_AHOOTSA.ps1
```

Este script copia el perfil completo a:

```text
user_personalities\ahootsa_realtime_es
profiles\ahootsa_realtime_es
reachy_mini_conversation_app\profiles\ahootsa_realtime_es
reachy_talk_data\profiles\ahootsa_realtime_es
```

y además copia los archivos críticos de nuevo uno por uno.

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_COPIA_PERFIL_INSTALADO_AHOOTSA.ps1
```

Todos los destinos instalados deben mostrar:

```text
ahootsa_debug_logger.py = True
memory_feedback_config.json = True
assistant_response = True
reaction restored = True
logging = True
flip delay = True
memory logs = True
```


---

# Respuesta directa Memory y sonido retardado — v0.4.57.4

## Qué demuestran los logs

Los logs muestran que la lógica ya se ejecuta:

```text
tool_start choose_memory_cards
memory_choose_result result=miss
tool_start play_emotion
audio ok true backend pygame
tool_result choose_memory_cards con robot_say / assistant_response / speak
```

Por tanto, el problema ya no es que el juego no llame a herramientas.  
El problema probable es que la app oficial no está diciendo el campo `robot_say`, aunque esté presente.

## Cambios

```text
- choose_memory_cards devuelve muchos campos equivalentes:
  text, message, answer, content, response, final_response,
  spoken_response, tts_text, robot_say, assistant_response, speak.
- No devuelve el state completo al LLM.
- Programa la emoción en segundo plano con retardo.
- Añade winsound como fallback audible en Windows.
- Mantiene logs JSONL.
```

## Orden buscado

```text
1. La herramienta devuelve rápido el texto.
2. La app puede decir el texto.
3. La emoción/sonido se ejecuta con retardo.
```

## Reparación

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_RESPUESTA_DIRECTA_MEMORY_AHOOTSA.ps1
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_RESPUESTA_DIRECTA_MEMORY_AHOOTSA.ps1
```

Debe mostrar:

```text
direct mode = True
text field = True
content field = True
final_response = True
background reaction = True
winsound = True
```


---

# Perfil monitora comunicación y educación especial — v0.4.57.5

## Base

Parte de:

```text
v0.4.57.4_respuesta_directa_memory_sonido
```

No usa ramas posteriores.

## Perfil combinado

Rol:

```text
Actúa como una monitora experta en comunicación y educación especial.
```

Tono:

```text
dulce, paciente, motivador, claro y respetuoso
```

Regla de oro:

```text
Nunca usar lenguaje complejo, tecnicismos ni dobles sentidos.
```

Si el usuario no entiende:

```text
reformular con ejemplos de la vida cotidiana
```

Gestión de voz:

```text
pausas más largas entre frases
una idea por frase
una pregunta cada vez
```

Estilo de guía:

```text
No dar siempre la respuesta hecha.
Guiar con preguntas sencillas.
```

Ejemplo:

```text
¿Quieres decir que estás feliz o que estás sorprendido?
```

## Archivos añadidos

```text
profiles\ahootsa_realtime_es\ahootsa_persona_config.json
profiles\ahootsa_realtime_es\communication_profile.md
```

## Archivos modificados

```text
profiles\ahootsa_realtime_es\instructions.txt
profiles\ahootsa_realtime_es\choose_memory_cards.py
profiles\ahootsa_realtime_es\start_memory_pairs_game.py
```

## Reparación

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_PERFIL_MONITORA_AHOOTSA.ps1
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_PERFIL_MONITORA_AHOOTSA.ps1
```

Debe mostrar:

```text
monitora = True
educación especial = True
regla oro = True
pausas voz = True
no respuesta hecha = True
buen intento = True
```


---

# Actividades de comunicación por niveles — v0.4.57.6

## Flujo de conversación

Cuando el usuario pida actividades de comunicación, Ahootsa debe preguntar:

```text
¿Qué tipo de actividades quieres hacer: fáciles, normales o avanzadas?
```

Herramienta:

```text
list_communication_activity_levels
```

Cuando el usuario elige un nivel:

```text
list_communication_activities
```

Cuando el usuario elige una actividad concreta:

```text
start_communication_activity
```

## Niveles

### Fácil

1. Elige una emoción.
2. Pido lo que necesito.
3. ¿Qué acción ves?
4. Completa una frase.
5. Respondo sí o no.
6. Primero y después.

### Normal

1. Explico lo que me gusta.
2. Cuento qué ha pasado.
3. Escribo un mensaje corto.
4. Del pictograma a la frase.
5. Pido ayuda de forma clara.
6. Elijo y explico.

### Avanzada

1. Doy mi opinión con respeto.
2. Diferencio emociones parecidas.
3. Resuelvo un malentendido.
4. Mejoro un mensaje escrito.
5. Cuento una historia en tres partes.
6. Ordeno pictogramas y explico.

## Archivos nuevos

```text
communication_activities_catalog.json
communication_activities_overview.md
list_communication_activity_levels.py
list_communication_activities.py
start_communication_activity.py
```

## Reparación

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_ACTIVIDADES_COMUNICACION_AHOOTSA.ps1
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_ACTIVIDADES_COMUNICACION_AHOOTSA.ps1
```


---

# Fix instalación actividades comunicación — v0.4.57.7

## Problema detectado

El diagnóstico muestra que `RAIZ_INSTANCE_PATH` y `FUENTE_PROFILE` tienen las actividades, pero los perfiles realmente instalados siguen antiguos.

## Solución

Ejecutar con Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_INSTALACION_ACTIVIDADES_COMUNICACION_AHOOTSA.ps1
```

Nuevo diagnóstico:

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_INSTALACION_ACTIVIDADES_AHOOTSA.ps1
```

Debe salir `True` en todos los destinos para catálogo, herramientas y marcadores.


---

# Router español para actividades de comunicación — v0.4.57.8

## Diagnóstico de los logs

En los logs subidos aparece `choose_memory_cards`, `memory_choose_result` y `play_emotion`, pero no aparece:

```text
list_communication_activity_levels
list_communication_activities
start_communication_activity
```

Eso indica que la instalación ya estaba bien, pero el modelo no estaba llamando a las herramientas de actividades.

## Corrección

Se añade una herramienta principal en español:

```text
actividades_comunicacion
```

Y dos alias:

```text
listar_actividades_comunicacion
iniciar_actividad_comunicacion
```

## Regla añadida

Si el usuario dice actividades, lista actividades, comunicación, hablar mejor, escribir mejor, pictogramas, emociones, fácil, normal, avanzada o iniciar actividad, Ahootsa debe usar `actividades_comunicacion`.

## Reparación

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_ROUTER_ACTIVIDADES_COMUNICACION_AHOOTSA.ps1
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_ROUTER_ACTIVIDADES_AHOOTSA.ps1
```


---

# Fix diagnóstico router actividades — v0.4.57.9

## Problema

El diagnóstico de v0.4.57.8 fallaba por una cadena PowerShell con backticks:

```text
No uses `choose_memory_cards`
```

En PowerShell el backtick puede escapar la comilla y romper el script.

## Corrección

Se reemplaza el diagnóstico por una versión segura sin backticks dentro de cadenas.

## Parche rápido

```powershell
powershell -ExecutionPolicy Bypass -File .\FIX_DIAGNOSTICO_ROUTER_ACTIVIDADES_AHOOTSA.ps1
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_ROUTER_ACTIVIDADES_AHOOTSA.ps1
```

---

## Actualización 5_0: modo MuJoCo web sin Desktop

Esta documentación pertenece ahora al paquete `5_0_ahootsa_mujoco_web_sin_desktop`.

Modo recomendado para esta versión:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

Reglas de uso:

```text
- No abrir Reachy Mini Desktop en este modo.
- Usar el panel web http://127.0.0.1:8000.
- Mantener ON solo ahotsa_realtime_ollama_app.
- Mantener OFF reachy_mini_conversation_app.
```

Documentos principales añadidos:

```text
39_MODO_MUJOCO_WEB_SIN_DESKTOP_5_0.md
40_COMANDOS_5_AHOOTSA_MUJOCO_WEB.md
41_API_REST_USADA_5_AHOOTSA_MUJOCO_WEB.md
42_NO_USAR_DESKTOP_EN_MODO_MUJOCO_WEB.md
43_CHANGELOG_5_0.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0 -->

---

## Actualización 5_0_1: fix rutas con espacios

Se corrige el error de PowerShell provocado por la ruta:

```text
Reachy Mini Control
```

El script principal `LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1` ahora genera un `.ps1` temporal y llama al daemon mediante variable, no mediante una cadena inline.

Documento nuevo:

```text
44_FIX_RUTAS_CON_ESPACIOS_5_0_1.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_1 -->

---

## Actualización 5_0_2: limpieza de scripts antiguos

Se han eliminado scripts anteriores que ya no son necesarios para el modo actual.

Scripts actuales:

```text
INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
LANZAR_SOLO_DAEMON_5_MUJOCO.ps1
PARAR_5_AHOOTSA_MUJOCO_WEB.ps1
test\DIAGNOSTICAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

Documento nuevo:

```text
45_LIMPIEZA_SCRIPTS_5_0_2.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_2 -->

---

## Actualización 5_0_3: fix profile=default

En modo daemon web, el log puede mostrar:

```text
Loading tools for profile: default
```

Desde 5.0.3, `INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1` copia el perfil Ahootsa también sobre `default` y `starter_profile`, para que las herramientas de Ahootsa carguen aunque el motor interno use el perfil `default`.

Documento nuevo:

```text
46_FIX_PROFILE_DEFAULT_5_0_3.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_3 -->

---

## Actualización 5_0_4: identidad Ahootsa y castellano

Se corrige el caso en que la app arranca diciendo que es Reachy Mini o hablando en inglés.

Cambios:
- greeting en castellano;
- instrucciones reforzadas;
- perfil copiado también sobre `default`, `starter_profile` y `external_content/external_profiles`;
- `.env` con identidad Ahootsa;
- variables de proceso en el launcher;
- runtime copy activado en `main.py`.

Documento nuevo:

```text
47_FIX_IDENTIDAD_CASTELLANO_5_0_4.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_4 -->

---

## Actualización 5_0_5: reinstalación del módulo Python de Ahootsa

Se corrige el error:

```text
No module named 'ahootsa_realtime_ollama_desktop_app'
```

El instalador copia el módulo Python a `apps_venv\Lib\site-packages`, crea un `.pth` y verifica `IMPORT_OK`.

Documento nuevo:

```text
48_FIX_MODULO_APP_NO_IMPORTABLE_5_0_5.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_5 -->

---

## Actualizacion 5_0_6: instalador PowerShell 5.1 safe

Se corrige el error de parseo del instalador en Windows PowerShell:

```text
Token 'BLOQUE' inesperado
```

El instalador se ha reescrito con codificacion UTF-8 con BOM y cadenas seguras.

Documento nuevo:

```text
49_FIX_INSTALADOR_POWERSHELL51_5_0_6.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_6 -->

---

## Actualizacion 5_0_7: actividades directas sin bloqueo post-tool

Se corrige el bloqueo al iniciar una actividad de comunicacion. Las herramientas de actividades pasan de `needs_response = True` a `needs_response = False`, para que devuelvan la respuesta directamente sin esperar una segunda generacion del backend realtime.

Documento nuevo:

```text
50_FIX_ACTIVIDADES_DIRECTAS_5_0_7.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_7 -->
