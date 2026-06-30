# Ahootsa Realtime Ollama — Arquitectura y funcionalidad

**Versión documentada:** v0.4.35 `base_original_resources`  
**Programa:** Ahootsa Realtime Ollama  
**Entry-point Desktop:** `ahootsa_realtime_ollama_app`  
**Base estable recomendada:** v0.4.35  
**Objetivo del documento:** explicar qué partes vienen de la app oficial, qué partes añade Ahootsa, qué usa IA remota y qué consulta Ollama local.

---

## 1. Idea principal

Ahootsa Realtime Ollama **no sustituye la app oficial de conversación** de Reachy Mini.

La arquitectura correcta es:

```text
Reachy Mini Desktop
│
├─ App oficial de conversación
│  ├─ micrófono
│  ├─ voz realtime
│  ├─ interfaz web
│  ├─ perfiles
│  ├─ herramientas del robot
│  ├─ emociones
│  ├─ bailes
│  ├─ cámara
│  └─ memoria
│
└─ Ahootsa Realtime Ollama
   ├─ arranca la app oficial
   ├─ añade perfil Ahootsa en español
   ├─ mantiene herramientas originales
   └─ añade una sola herramienta nueva:
      └─ ask_ollama
```

La mejora principal de Ahootsa es **añadir la posibilidad de consultar Ollama local**, pero sin romper el sistema original de voz, herramientas, emociones y movimientos.

---

## 2. Qué se reutiliza de la app original

Ahootsa usa la app oficial `reachy_mini_conversation_app` como núcleo.

Se reutiliza:

```text
- Interfaz web original
- Micrófono
- Voz realtime
- Gestión de turnos de conversación
- Sistema de perfiles
- Sistema de herramientas
- Movimiento del robot
- Emociones oficiales
- Bailes oficiales
- Cámara
- Memoria
```

En el código, la app nueva se apoya en la original mediante importaciones equivalentes a:

```python
from reachy_mini_conversation_app.main import run
from reachy_mini_conversation_app.utils import parse_args
```

Esto significa que Ahootsa **envuelve** la app oficial, no la reemplaza.

---

## 3. Carpetas nuevas de Ahootsa

Estructura de la versión limpia:

```text
ahootsa_v0_4_9_base_original_resources/
│
├─ pyproject.toml
├─ AHOOTSA_VERSION.txt
├─ README_AHOOTSA_REALTIME_OLLAMA.md
│
├─ docs/
│  └─ ARQUITECTURA_FUNCIONALIDAD.md
│
├─ scripts/
│  └─ windows/
│     ├─ 00_crear_modelo_ollama_ahootsa.ps1
│     ├─ 01_instalar_ahootsa_realtime_ollama_en_desktop.ps1
│     ├─ 04_limpiar_variables_emociones_locales.ps1
│     ├─ 05_instalar_metadata_desktop.ps1
│     └─ 08_liberar_puertos_ahootsa.ps1
│
└─ src/
   └─ ahootsa_realtime_ollama_desktop_app/
      ├─ __init__.py
      ├─ main.py
      ├─ assets/
      │  └─ ahootsa_logo.png
      │
      └─ profiles/
         └─ ahootsa_realtime_es/
            ├─ instructions.txt
            ├─ greeting.txt
            ├─ tools.txt
            ├─ voice.txt
            └─ ask_ollama.py
```

---

## 4. Propósito de cada parte nueva

### 4.1. `pyproject.toml`

Registra Ahootsa como aplicación nueva de Reachy Mini Desktop:

```text
ahootsa_realtime_ollama_app
```

Así aparece en el panel de aplicaciones sin pisar la app oficial.

---

### 4.2. `main.py`

Es el wrapper principal.

Funciones:

```text
1. Registra la app nueva.
2. Copia el perfil Ahootsa a user_personalities.
3. Configura el idioma español.
4. Mantiene el backend realtime de la app oficial.
5. Configura Ollama local.
6. Limpia variables antiguas de versiones experimentales.
7. Lanza la app oficial de conversación.
```

Decisión técnica importante:

```text
Ollama no sustituye el backend realtime.
Ollama se añade como herramienta opcional.
```

---

### 4.3. Perfil `ahootsa_realtime_es`

Carpeta:

```text
src/ahootsa_realtime_ollama_desktop_app/profiles/ahootsa_realtime_es/
```

Propósito:

```text
- Definir la personalidad Ahootsa.
- Hablar en español.
- Usar frases cortas.
- Ser amable, positivo y paciente.
- Actuar como tutor de apoyo.
- Usar herramientas originales cuando se pidan movimientos.
- Usar ask_ollama solo cuando proceda consultar IA local.
```

Archivos:

```text
instructions.txt  → reglas de comportamiento
greeting.txt      → saludo inicial
voice.txt         → voz del perfil
tools.txt         → herramientas disponibles
ask_ollama.py     → herramienta nueva para consultar Ollama
```

---

## 5. Herramientas activas

En v0.4.35 las herramientas activas son:

```text
dance
stop_dance
play_emotion
stop_emotion
camera
idle_do_nothing
move_head
sweep_look
remember
forget
ask_ollama
```

### Herramientas originales

Estas vienen de la app oficial:

```text
dance
stop_dance
play_emotion
stop_emotion
camera
idle_do_nothing
move_head
sweep_look
remember
forget
```

Se usan para:

```text
- bailar
- parar baile
- expresar emociones
- parar emociones
- usar cámara
- mantener espera tranquila
- mover cabeza
- mirar alrededor
- recordar información
- olvidar información
```

### Herramienta nueva

La única herramienta añadida por Ahootsa es:

```text
ask_ollama
```

Se usa para consultar el modelo local:

```text
Ollama local
URL: http://127.0.0.1:11434/api/chat
Modelo: ahootsa-local:latest
```

---

## 6. Qué partes usan IA remota

Mientras se usa la app oficial de conversación, la IA remota o backend realtime sigue siendo el **orquestador principal**.

La IA remota participa en:

```text
- Escucha y conversación realtime.
- Interpretación del turno del usuario.
- Decisión de qué herramienta usar.
- Respuesta hablada al usuario.
- Gestión natural del diálogo.
- Decisión de llamar o no a ask_ollama.
```

Ejemplos que normalmente usa la IA remota sin Ollama:

```text
Usuario: hola
→ responde la IA remota con voz.

Usuario: baila
→ la IA remota llama a dance.

Usuario: saluda
→ la IA remota llama a play_emotion.

Usuario: mira a la izquierda
→ la IA remota llama a move_head.

Usuario: celebra que lo he hecho bien
→ la IA remota puede llamar a play_emotion emotion="success"
→ opcionalmente puede llamar a dance
→ responde con refuerzo positivo.
```

---

## 7. Qué partes consultan Ollama local

Ollama local solo se consulta mediante:

```text
ask_ollama.py
```

No se consulta automáticamente para todo.

Flujo:

```text
Usuario habla
→ app oficial procesa el turno
→ IA remota decide que necesita IA local
→ llama a ask_ollama
→ ask_ollama envía texto a Ollama
→ Ollama responde texto
→ IA remota convierte ese resultado en respuesta hablada
```

Ollama local recibe solo el texto que se le envía en esa herramienta.

---

## 8. Cuándo se debe llamar a `ask_ollama`

Se debe llamar a `ask_ollama` cuando el usuario lo pida explícitamente o cuando la instrucción del perfil indique usar IA local.

Casos claros:

```text
"usa la IA local"
"consulta Ollama"
"pregunta al modelo local"
"usa ahootsa-local"
"usa el modelo local para responder"
"pide a Ollama una actividad"
"dame una actividad sencilla usando IA local"
"consulta tu modelo local y dime..."
```

También puede usarse para:

```text
- Generar actividades sencillas.
- Crear explicaciones educativas breves.
- Proponer preguntas adaptadas.
- Reformular contenidos con lenguaje sencillo.
- Generar ideas sin depender del modelo remoto para el contenido final.
```

Ejemplo:

```text
Usuario: usa la IA local para darme una actividad sencilla
→ IA remota llama a ask_ollama
→ Ollama genera una actividad
→ Ahootsa la dice con voz
```

---

## 9. Cuándo NO se debe llamar a `ask_ollama`

No se debe usar Ollama para acciones del robot.

Ejemplos:

```text
Usuario: baila
→ usar dance
→ NO usar ask_ollama

Usuario: para
→ usar stop_dance / stop_emotion
→ NO usar ask_ollama

Usuario: saluda
→ usar play_emotion
→ NO usar ask_ollama

Usuario: mira a la izquierda
→ usar move_head
→ NO usar ask_ollama

Usuario: haz una emoción alegre
→ usar play_emotion
→ NO usar ask_ollama

Usuario: recuérdame esto
→ usar remember
→ NO usar ask_ollama

Usuario: olvida eso
→ usar forget
→ NO usar ask_ollama
```

Tampoco debe usarse para conversación normal salvo que se pida IA local.

Ejemplo:

```text
Usuario: ¿cómo estás?
→ responde la IA remota
→ NO usar ask_ollama
```

---

## 10. Resumen de reparto entre IA remota y Ollama local

| Función | Responsable principal |
|---|---|
| Escuchar por micrófono | App oficial / backend realtime |
| Responder con voz | App oficial / backend realtime |
| Decidir herramientas | IA remota |
| Bailar | Herramienta original `dance` |
| Parar baile | Herramienta original `stop_dance` |
| Emociones | Herramienta original `play_emotion` |
| Parar emociones | Herramienta original `stop_emotion` |
| Cámara | Herramienta original `camera` |
| Movimiento cabeza | Herramienta original `move_head` |
| Mirada barrido | Herramienta original `sweep_look` |
| Memoria | Herramientas originales `remember` / `forget` |
| Consulta a IA local | Herramienta nueva `ask_ollama` |
| Modelo local | Ollama `ahootsa-local:latest` |

---

## 11. Privacidad y límites

En esta arquitectura, Ahootsa **no es todavía 100% local**.

Porque:

```text
- La conversación principal sigue usando el backend realtime remoto.
- La IA remota decide cuándo llamar a herramientas.
- La voz realtime depende del sistema original.
```

Lo que sí es local:

```text
- Ollama.
- El modelo ahootsa-local:latest.
- Las respuestas generadas dentro de ask_ollama.
```

Importante:

```text
ask_ollama no controla el micrófono.
ask_ollama no controla la voz realtime.
ask_ollama no controla directamente los movimientos.
ask_ollama no sustituye a la IA remota.
```

Para una versión 100% local haría falta otra arquitectura:

```text
STT local
+ LLM local
+ TTS local
+ controlador local de herramientas del robot
```

Esa sería una rama futura distinta.

---

## 12. Evolución de versiones

### v0.2.x — Ahootsa clásico

```text
- Fork de la app oficial.
- Voz, micro, perfiles y herramientas originales.
- Backend remoto.
- Sin Ollama local.
```

### v0.3.x — Ahootsa Ollama Local

```text
- Prueba de chat local por texto.
- Usa Ollama correctamente.
- No mantiene voz realtime completa.
- No mantiene movimientos automáticos del robot.
- Sirvió para verificar que Ollama y ahootsa-local:latest funcionaban.
```

### v0.4.35 — Realtime Ollama Fork

```text
- Vuelve a partir de la app oficial.
- Mantiene micro, voz y herramientas.
- Añade ask_ollama.
```

### v0.4.35 a v0.4.35 — Performance Library experimental

```text
- Intentos de usar librería local JSON/OGG.
- Intentos de audio asociado a emociones/bailes.
- Problemas con RecordedMoves, rutas locales, media.play_sound y GStreamer.
- No deben ser la base estable.
```

### v0.4.35 — Original Robot Tools Recovery

```text
- Recupera herramientas originales.
- Todavía quedaba una variable antigua que provocaba error.
```

### v0.4.35 — Original Tools Clean Start

```text
- Base limpia.
- Sin JSON/OGG local.
- Sin media.play_sound.
- Sin variables antiguas de emociones locales.
- Usa solo herramientas originales.
- Añade ask_ollama.
- Recomendado como base estable actual.
```

---

## 13. Regla para versiones nuevas

Toda nueva versión de Ahootsa debe incluir este archivo:

```text
docs/ARQUITECTURA_FUNCIONALIDAD.md
```

Y debe actualizar:

```text
- Nombre de versión.
- Fecha.
- Herramientas activas.
- Qué se reutiliza de la app oficial.
- Qué código nuevo se añade.
- Qué usa IA remota.
- Qué consulta Ollama local.
- Cuándo se llama a ask_ollama.
- Limitaciones conocidas.
- Cambios respecto a la versión anterior.
```

También debe incluir:

```text
AHOOTSA_VERSION.txt
README_AHOOTSA_REALTIME_OLLAMA.md
docs/CAMBIOS_vX_Y_Z.md
```

---

## 14. Conclusión

La versión estable actual debe entenderse así:

```text
Ahootsa Realtime Ollama
=
App oficial de conversación de Reachy Mini
+
perfil educativo en español
+
herramientas originales del robot
+
consulta opcional a Ollama local mediante ask_ollama
```

La consulta a Ollama local es **opcional y controlada**.  
No sustituye la IA remota.  
Solo se realiza cuando el usuario pide usar IA local o cuando el perfil decide explícitamente llamar a `ask_ollama`.



## 15. Actualización v0.4.35

La versión v0.4.35 consolida esta arquitectura como base estable. La diferencia importante respecto a v0.4.35 es que `instructions.txt` queda más estricto: `ask_ollama` no se usa por defecto para preguntas generales ni para razonamiento normal; solo se usa cuando el usuario pide explícitamente IA local, Ollama, modelo local o ahootsa-local.
