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


## Audio de emociones

```text
AHOOTSA_EMOTION_AUDIO_BACKEND=pygame
AHOOTSA_PYGAME_AUDIO_DRIVERS=directsound,wasapi,winmm,default
AHOOTSA_EMOTION_AUDIO_VOLUME=1.0
```


## Recordatorio idle

```text
AHOOTSA_IDLE_REMINDER_ENABLED=1
AHOOTSA_IDLE_REMINDER_SECONDS=20
AHOOTSA_IDLE_REMINDER_REPEAT_SECONDS=60
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
