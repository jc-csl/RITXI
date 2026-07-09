# Ahootsa / Reachy Mini — arquitectura, instalación, configuración y guía para modificar el código

**Versión documental:** 5.0.27  
**Fecha:** 2026-07-08  
**Contexto:** Ahootsa 5.0.25 con MuJoCo web backend realtime, logs simplificados y actividades recuperadas.  
**Objetivo del documento:** explicar cómo se organiza el sistema, dónde viven los archivos importantes, qué reutiliza Ahootsa de la aplicación oficial `reachy_mini_conversation_app`, cómo se instala/lanza desde PowerShell, qué parte del funcionamiento está en la carpeta local de versión y qué parte está instalada dentro del entorno `apps_venv` de Reachy Mini Control.

---

## 1. Resumen ejecutivo

Ahootsa es una adaptación local de la aplicación conversacional de Reachy Mini. El sistema se apoya en el ecosistema oficial de **Reachy Mini Control**, pero añade una capa propia orientada a:

- conversación en castellano;
- uso con Ollama/local LLM cuando está disponible;
- actividades educativas o terapéuticas;
- emociones, bailes y animaciones del robot;
- ejecución en modo simulación/MuJoCo web cuando no se dispone del robot físico;
- logs sencillos para poder depurar sesiones;
- compatibilidad con la estructura de Desktop App de Reachy Mini.

La arquitectura real se divide en dos zonas:

1. **Carpeta de versión local**, por ejemplo:

   ```text
   D:\RITXI\5_0_25_ahootsa_logs_simples_actividades_recuperadas
   ```

   Aquí están los scripts de lanzamiento, documentación, posibles recursos propios y herramientas auxiliares.

2. **Paquete Python instalado en el entorno de Reachy Mini Control**, por ejemplo:

   ```text
   C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Lib\site-packages\ahootsa_realtime_ollama_desktop_app
   ```

   Aquí vive la aplicación Python que realmente importa y ejecuta el Desktop Control.

El script de lanzamiento 5.0.25 usa el Python del entorno oficial:

```text
C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe
```

y el daemon oficial:

```text
C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\reachy-mini-daemon.exe
```

Por eso, cuando falta un módulo como `mujoco`, no basta con instalarlo en cualquier Python. Hay que instalarlo específicamente en `apps_venv`.

---

## 2. Arquitectura general del sistema

### 2.1. Vista por capas

```text
┌─────────────────────────────────────────────────────────────┐
│ Usuario                                                     │
│ Pantalla táctil / navegador / Desktop Control               │
└───────────────────────────────┬─────────────────────────────┘
                                │ HTTP / WebSocket / eventos UI
┌───────────────────────────────▼─────────────────────────────┐
│ Frontend de la app                                           │
│ Interfaz visual, botones, chat, fichas, actividades          │
│ Puede reutilizar estructura de la app oficial                │
│ reachy_mini_conversation_app                                 │
└───────────────────────────────┬─────────────────────────────┘
                                │ Llamadas a endpoints locales
                                │ /status, /mic, /voices/current,
                                │ rutas propias de chat/acciones/etc.
┌───────────────────────────────▼─────────────────────────────┐
│ Backend Ahootsa                                              │
│ Python + FastAPI/Starlette/runner del ecosistema Reachy       │
│ Orquesta chat, actividades, robot, simulación, logs           │
└───────────────┬──────────────────────────────┬──────────────┘
                │                              │
                │                              │
┌───────────────▼───────────────┐  ┌───────────▼───────────────┐
│ IA local / Ollama              │  │ Reachy Mini / MuJoCo       │
│ ask_ollama, prompts, perfiles  │  │ emociones, bailes, cabeza, │
│ respuesta conversacional       │  │ cámara, simulación web     │
└───────────────┬───────────────┘  └───────────┬───────────────┘
                │                              │
┌───────────────▼──────────────────────────────▼──────────────┐
│ Logs y estado de sesión                                      │
│ pantalla.log, eventos.jsonl, runtime.log                     │
└──────────────────────────────────────────────────────────────┘
```

### 2.2. Componentes principales

| Componente | Ubicación típica | Función |
|---|---|---|
| Reachy Mini Control | Instalación oficial del Desktop | Gestiona entorno, daemon, apps y comunicación con robot/simulador. |
| `apps_venv` | `%LOCALAPPDATA%\Reachy Mini Control\apps_venv` | Entorno Python usado realmente por las apps de Desktop Control. |
| Paquete Ahootsa instalado | `apps_venv\Lib\site-packages\ahootsa_realtime_ollama_desktop_app` | Código Python que importa y ejecuta la app Ahootsa. |
| Carpeta de versión | `D:\RITXI\5_0_25_...` | Scripts, documentación, instaladores, wrappers, logs o recursos de esa versión. |
| Daemon Reachy | `reachy-mini-daemon.exe` | Servicio local que permite a Desktop Control comunicarse con robot/simulación. |
| MuJoCo | módulo `mujoco` dentro de `apps_venv` | Simulación física/web del robot cuando se lanza backend realtime. |
| Ollama | servicio local, normalmente `localhost:11434` | LLM local para respuestas sin depender de IA remota. |
| Logs Ahootsa | `D:\RITXI\logs` | Registro de pantalla, eventos y runtime por sesión. |

---

## 3. Relación entre Ahootsa y `reachy_mini_conversation_app`

### 3.1. Qué es la app oficial

La app oficial `pollen-robotics/reachy_mini_conversation_app` proporciona una base conversacional para Reachy Mini. En la versión que se usó como referencia aparecían archivos y carpetas como:

```text
.env.example
README.md
index.html
docs/assets/conversation_app_arch.svg
docs/assets/reachy_mini_dance.gif
docs/scheme.mmd
external_content/external_profiles/starter_profile/instructions.txt
external_content/external_profiles/starter_profile/tools.txt
external_content/external_tools/starter_custom_tool.py
profiles/default/instructions.txt
profiles/default/tools.txt
profiles/bored_teenager/instructions.txt
profiles/bored_teenager/tools.txt
profiles/captain_circuit/instructions.txt
profiles/captain_circuit/tools.txt
profiles/chess_coach/instructions.txt
profiles/chess_coach/tools.txt
profiles/cosmic_kitchen/instructions.txt
profiles/cosmic_kitchen/tools.txt
```

La idea importante es que la app oficial separa:

- **interfaz** (`index.html` y recursos web);
- **perfiles** (`profiles/.../instructions.txt` y `tools.txt`);
- **herramientas externas** (`external_content/external_tools/...`);
- **documentación y esquema de arquitectura** (`docs/...`).

Ahootsa toma esa filosofía y la adapta a un caso local en castellano, con actividades y control explícito de funciones como Ollama, cámara, emociones y bailes.

### 3.2. Qué reutiliza Ahootsa de la app oficial

Ahootsa puede reutilizar varias ideas o piezas de la app oficial:

1. **Formato de Desktop App**  
   La aplicación se presenta al ecosistema de Reachy Mini Control como una app instalable/ejecutable desde el Desktop.

2. **Estructura frontend + backend**  
   El usuario interactúa con una interfaz web, y la lógica real se resuelve en Python.

3. **Modelo de perfiles**  
   La app oficial usa perfiles con instrucciones y herramientas. Ahootsa puede usar esta idea para construir perfiles de conversación en castellano o perfiles educativos.

4. **Herramientas declarativas**  
   En la app oficial, los perfiles pueden listar herramientas. En Ahootsa, esta idea se traduce en funciones como:

   - preguntar a Ollama;
   - activar emoción;
   - ejecutar baile;
   - explorar imagen;
   - mover cabeza;
   - recordar/olvidar información;
   - iniciar actividad.

5. **Integración con Reachy Mini**  
   La base oficial sabe comunicarse con el ecosistema Reachy. Ahootsa añade reglas propias sobre cuándo mover el robot, cuándo hablar, cuándo animar y cuándo quedarse quieto.

### 3.3. Qué añade Ahootsa

Ahootsa añade una capa funcional propia:

- idioma y tono adaptados al usuario;
- lógica para actividades y fichas;
- control de animaciones automáticas;
- uso preferente de IA local/Ollama;
- logs simplificados por sesión;
- scripts PowerShell para instalación/lanzamiento en Windows;
- compatibilidad con MuJoCo web backend realtime;
- endpoints de compatibilidad para evitar errores 404 del frontend;
- documentación técnica por versión.

---

## 4. Estructura de carpetas recomendada

La estructura exacta puede cambiar por versión, pero conviene mantener algo parecido a esto:

```text
D:\RITXI\5_0_25_ahootsa_logs_simples_actividades_recuperadas
│
├── LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
├── instrucciones.txt
├── README.md
│
├── docs
│   ├── ARQUITECTURA_FUNCIONALIDAD.md
│   ├── CAMBIOS_VERSION.md
│   └── VERIFICACION.md
│
├── tools
│   ├── scripts de parche
│   ├── scripts de diagnóstico
│   └── utilidades de instalación
│
├── external_content
│   ├── external_profiles
│   │   └── ahootsa_profile
│   │       ├── instructions.txt
│   │       └── tools.txt
│   └── external_tools
│       └── herramientas propias
│
├── profiles
│   └── perfiles propios o heredados
│
├── assets
│   ├── imágenes
│   ├── iconos
│   └── recursos de interfaz
│
└── logs opcionales de versión
```

En la práctica, la ejecución puede no leer todos esos archivos desde la carpeta local. Muchas veces el script instala o modifica el paquete dentro de `apps_venv`, y el Desktop ejecuta el código desde `site-packages`.

Por eso es fundamental distinguir:

```text
Carpeta D:\RITXI\5_0_25_...       → versión, scripts, documentación, recursos.
Paquete en apps_venv\site-packages → código Python que se importa realmente.
```

---

## 5. Instalación y ejecución con PowerShell

### 5.1. Script principal 5.0.25

El lanzamiento usado es:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

El script muestra información parecida a:

```text
Ahootsa 5.0.25 - MuJoCo web backend realtime
Root:    D:\RITXI\5_0_25_ahootsa_logs_simples_actividades_recuperadas
Logs:    D:\RITXI\logs
Pantalla:D:\RITXI\logs\ahootsa5_YYYYMMDD_HHMMSS_pantalla.log
Eventos: D:\RITXI\logs\ahootsa5_YYYYMMDD_HHMMSS_eventos.jsonl
Runtime: D:\RITXI\logs\ahootsa5_YYYYMMDD_HHMMSS_runtime.log
Session: YYYYMMDD_HHMMSS
Python:  C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe
Daemon:  C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\reachy-mini-daemon.exe
```

Esa salida es muy útil porque confirma:

- qué carpeta local se está usando como versión;
- dónde se guardan los logs;
- qué Python se usa;
- qué daemon se usa;
- si el paquete Ahootsa importa correctamente.

### 5.2. Comprobación del paquete instalado

Para saber qué código Python está importando realmente Ahootsa:

```powershell
$py = "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe"
& $py -c "import ahootsa_realtime_ollama_desktop_app as p; print(p.__file__)"
```

Salida esperada:

```text
C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Lib\site-packages\ahootsa_realtime_ollama_desktop_app\__init__.py
```

Esa ruta indica dónde hay que mirar para modificar el backend Python que se está ejecutando.

### 5.3. Instalación de MuJoCo en el entorno correcto

Si aparece:

```text
ModuleNotFoundError: No module named 'mujoco'
[ERROR] MuJoCo no esta instalado en apps_venv.
```

hay que instalarlo en el Python de Reachy Mini Control:

```powershell
$py = "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe"
& $py -m ensurepip --upgrade
& $py -m pip install --upgrade pip
& $py -m pip install mujoco
```

Comprobación:

```powershell
& $py -c "import mujoco; print('MUJOCO_OK', mujoco.__version__)"
```

No conviene usar simplemente:

```powershell
pip install mujoco
```

porque puede instalarlo en otro Python del equipo.

---

## 6. Situación de los archivos de configuración

### 6.1. Configuración de la app oficial

En la app oficial aparecen principalmente estos tipos de configuración:

```text
.env.example
profiles/*/instructions.txt
profiles/*/tools.txt
external_content/external_profiles/*/instructions.txt
external_content/external_profiles/*/tools.txt
external_content/external_tools/*.py
```

Su función habitual es:

| Archivo | Función |
|---|---|
| `.env.example` | Plantilla de variables de entorno. Puede indicar claves, URLs, modelos o parámetros. |
| `instructions.txt` | Define personalidad, tono, reglas conversacionales y límites del perfil. |
| `tools.txt` | Lista herramientas disponibles para ese perfil. |
| `external_tools/*.py` | Implementa funciones personalizadas que la app puede invocar. |
| `README.md` | Explica instalación y uso. |
| `docs/scheme.mmd` | Esquema Mermaid de arquitectura o flujo. |

### 6.2. Configuración propia de Ahootsa

En Ahootsa conviene separar la configuración en bloques:

#### A. Configuración de IA local/Ollama

Parámetros habituales:

```text
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.1, gemma, qwen, mistral u otro modelo local
OLLAMA_TIMEOUT_SECONDS=...
USE_OLLAMA=true/false
```

La función relacionada suele llamarse algo parecido a:

```text
ask_ollama
```

o estar dentro de un módulo de IA local.

Su responsabilidad es:

- construir el prompt;
- llamar a Ollama;
- controlar timeout;
- devolver respuesta textual;
- aplicar fallback si Ollama no responde.

#### B. Configuración de voz y micro

Puede incluir:

```text
idioma = es-ES
motor_tts = pyttsx3 / navegador / sistema
micro_activo = true/false
modo_escucha = manual / automático / push-to-talk
```

En 5.0.25 aparecieron llamadas del frontend a:

```text
GET /voices/current
GET /mic
```

Si el backend no define esas rutas, aparecen errores 404. La corrección 5.0.27 añade endpoints de compatibilidad para que el frontend no falle aunque el micro real se gestione en otra capa.

#### C. Configuración de robot/simulación

Puede incluir:

```text
modo = robot_real / mujoco_web / mockup_sim
host = 127.0.0.1
puerto = 8000 / 7860 / según runner
usar_daemon = true
```

El script 5.0.25 muestra que se usa:

```text
MuJoCo web backend realtime
```

Por tanto, hay una dependencia clara con:

```text
mujoco
reachy-mini-daemon.exe
```

#### D. Configuración de actividades

Ahootsa recupera o incorpora actividades como:

- pregunta a Ollama;
- explorar imagen;
- opciones de baile;
- actividades con micro;
- actividades con sonido;
- chat con robot;
- chat completo;
- fichas educativas.

Conviene documentar cada actividad con:

```text
nombre
objetivo
entrada del usuario
salida esperada
si usa IA local
si usa cámara
si usa micro
si mueve el robot
si genera log de evento
```

#### E. Configuración de logs

En 5.0.25 se simplifican logs para no generar demasiados archivos. La salida esperada por sesión es:

```text
ahootsa5_YYYYMMDD_HHMMSS_pantalla.log
ahootsa5_YYYYMMDD_HHMMSS_eventos.jsonl
ahootsa5_YYYYMMDD_HHMMSS_runtime.log
```

Función de cada uno:

| Log | Función |
|---|---|
| `pantalla.log` | Registro legible de lo que se muestra o sucede en pantalla. |
| `eventos.jsonl` | Eventos estructurados, una línea JSON por evento. Útil para analizar sesiones. |
| `runtime.log` | Errores, trazas técnicas, imports, dependencias, arranque y ejecución. |

---

## 7. Qué se ejecuta desde la carpeta Ahootsa 5.0.25

La carpeta de versión suele actuar como **capa de lanzamiento y distribución**. En la 5.0.25 se ve claramente por la salida:

```text
Root: D:\RITXI\5_0_25_ahootsa_logs_simples_actividades_recuperadas
```

Desde ahí se realiza normalmente:

1. preparar variables de sesión;
2. crear nombres de logs;
3. localizar `apps_venv`;
4. comprobar que el paquete Python Ahootsa importa;
5. comprobar dependencias como `mujoco`;
6. arrancar daemon o backend;
7. lanzar app web/simulación;
8. redirigir salida a logs.

### 7.1. Elementos importantes en la carpeta local

| Archivo/carpeta | Papel |
|---|---|
| `LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1` | Script principal de arranque. |
| `instrucciones.txt` | Guía de instalación, cambios y modo de proceder. |
| `docs/ARQUITECTURA_FUNCIONALIDAD.md` | Documento obligatorio por versión con arquitectura y funcionalidades. |
| `tools/` | Scripts auxiliares de parche, diagnóstico o instalación. |
| `logs/` o ruta externa `D:\RITXI\logs` | Logs generados durante ejecución. |

### 7.2. Qué NO conviene meter en cada versión

Para mantener versiones limpias, no conviene arrastrar todos los scripts antiguos. Solo deberían quedarse:

- script principal de instalación/lanzamiento;
- scripts de diagnóstico útiles;
- script de corrección si hay una incidencia concreta;
- documentación de cambios;
- instrucciones de uso;
- recursos necesarios para esa versión.

---

## 8. Código Python instalado en `apps_venv`

### 8.1. Ruta principal

La ruta real se obtiene con:

```powershell
$py = "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe"
& $py -c "import ahootsa_realtime_ollama_desktop_app as p; print(p.__file__)"
```

El resultado apunta al paquete:

```text
...\site-packages\ahootsa_realtime_ollama_desktop_app
```

Ahí se deben buscar los módulos Python importantes.

### 8.2. Cómo listar módulos Python y pistas de contenido

Usa este diagnóstico:

```powershell
$py = "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe"
& $py - <<'PY'
import importlib, pathlib
p = importlib.import_module("ahootsa_realtime_ollama_desktop_app")
root = pathlib.Path(p.__file__).resolve().parent
print("PACKAGE", root)
for f in sorted(root.rglob("*.py")):
    if "__pycache__" in f.parts:
        continue
    txt = f.read_text(encoding="utf-8", errors="ignore")
    markers = []
    for k in ["FastAPI", "Starlette", "uvicorn", "Ollama", "mujoco", "voice", "mic", "camera", "dance", "emotion", "activity"]:
        if k.lower() in txt.lower():
            markers.append(k)
    print(f.relative_to(root), "::", ", ".join(markers) if markers else "-")
PY
```

La versión 5.0.27 incluye un script equivalente:

```text
2_DIAGNOSTICO_AHOOTSA_5_0_27.ps1
```

---

## 9. Módulos Python importantes y función esperada

Como el nombre exacto de los archivos puede variar entre versiones, esta sección describe los módulos por responsabilidad. Para localizar el archivo concreto, usar el diagnóstico anterior.

### 9.1. Módulo de entrada de app / servidor

Nombres habituales:

```text
__init__.py
app.py
main.py
server.py
backend.py
api.py
```

Responsabilidad:

- crear o exponer la aplicación ASGI;
- definir rutas HTTP;
- montar frontend;
- registrar endpoints;
- conectar con runner de Reachy Mini Control;
- iniciar lógica de app.

Pistas para localizarlo:

```text
FastAPI
Starlette
uvicorn
routes
@app.get
@app.post
```

En 5.0.26 se intentó buscar literalmente:

```python
app = FastAPI(...)
```

pero en tu instalación no apareció. Eso significa que la app se construye de otra manera, por ejemplo:

```python
fastapi_app = FastAPI(...)
```

```python
application = create_app()
```

```python
return FastAPI(...)
```

```python
Starlette(...)
```

```python
runner monta internamente una app ASGI
```

Por eso la corrección 5.0.27 es más robusta: engancha la creación de FastAPI/Starlette desde `__init__.py` sin depender del nombre de la variable.

### 9.2. Módulo de Ollama / IA local

Nombres probables:

```text
ollama_client.py
local_ai.py
llm.py
ai.py
chat.py
```

Responsabilidad:

- formar prompts;
- llamar a Ollama;
- gestionar modelo local;
- aplicar timeout;
- devolver respuesta;
- decidir fallback si no hay Ollama.

Función clave esperada:

```python
ask_ollama(...)
```

Puntos de modificación habituales:

- cambiar modelo;
- cambiar prompt de sistema;
- controlar longitud de respuesta;
- evitar respuestas demasiado complejas;
- añadir tono de tutor amable;
- desactivar IA remota;
- añadir RAG local.

### 9.3. Módulo de conversación

Nombres probables:

```text
conversation.py
chat.py
dialogue.py
agent.py
```

Responsabilidad:

- recibir texto del usuario;
- decidir si es conversación simple o actividad;
- llamar a IA local si procede;
- añadir contexto/perfil;
- devolver respuesta a pantalla/TTS;
- decidir si se activa robot o no.

Regla importante solicitada en versiones previas:

```text
Solo chat conversacional Texto + IA → sin animaciones automáticas.
Todo lo demás → puede usar animación positiva al inicio y al final.
```

Eso evita que el robot se mueva continuamente cuando solo se está conversando por texto.

### 9.4. Módulo de actividades

Nombres probables:

```text
activities.py
activity_manager.py
cards.py
fichas.py
```

Responsabilidad:

- listar actividades disponibles;
- lanzar actividad seleccionada;
- gestionar nivel/dificultad;
- controlar preguntas/respuestas;
- generar refuerzo positivo;
- registrar evento en log;
- activar animación si procede.

Actividades que se han mencionado como necesarias:

```text
pregunta a Ollama
explorar imagen
opciones de baile
actividades con micro
actividades con sonido
chat con robot
chat completo
```

### 9.5. Módulo de robot / movimientos / emociones

Nombres probables:

```text
robot.py
reachy_client.py
motions.py
emotions.py
actions.py
```

Responsabilidad:

- conectar con Reachy Mini o simulador;
- ejecutar emociones;
- mover cabeza;
- reproducir bailes;
- parar emoción;
- mandar robot a reposo/idle;
- adaptar acciones al modo MuJoCo/mockup/robot real.

Herramientas esperadas en Ahootsa:

```text
dance
play_emotion
stop_emotion
idle
move_head
camera
```

Bailes o animaciones positivas citadas:

```text
dance1
dance2
dance3
baile
calma
cheerful1
enthusiastic1
yes1
hello1
amazed1
electric1
aplauso
celebracion
saludo
fiesta
```

### 9.6. Módulo de cámara / exploración de imagen

Nombres probables:

```text
camera.py
vision.py
image_explorer.py
multimodal.py
```

Responsabilidad:

- comprobar si hay cámara disponible;
- capturar imagen;
- analizar imagen si hay modelo compatible;
- devolver descripción simple;
- registrar errores si no hay cámara.

En modo simulación puede existir una cámara virtual o puede no haber cámara real. La app debe responder de forma segura si no hay imagen disponible.

### 9.7. Módulo de voz / TTS / STT

Nombres probables:

```text
voice.py
tts.py
stt.py
audio.py
mic.py
```

Responsabilidad:

- saber qué voz está activa;
- gestionar texto a voz;
- gestionar micro o entrada de voz;
- evitar eco;
- controlar interrupciones;
- devolver estado de `/mic` y `/voices/current` si el frontend lo consulta.

En 5.0.25 el frontend pidió:

```text
GET /voices/current
GET /mic
```

y el backend respondió 404. La corrección 5.0.27 añade respuestas mínimas para evitar que la UI falle.

### 9.8. Módulo de logs

Nombres probables:

```text
logs.py
logger.py
session_logs.py
events.py
```

Responsabilidad:

- crear sesión `YYYYMMDD_HHMMSS`;
- abrir archivos de log;
- escribir eventos relevantes;
- separar log humano de log estructurado;
- evitar demasiados archivos.

Formato recomendado para `eventos.jsonl`:

```json
{"ts":"2026-07-08T05:49:33Z","type":"chat_user","text":"hola"}
{"ts":"2026-07-08T05:49:35Z","type":"ollama_response","latency_ms":1430}
{"ts":"2026-07-08T05:49:36Z","type":"robot_action","action":"hello1"}
```

### 9.9. Módulo de configuración

Nombres probables:

```text
config.py
settings.py
constants.py
```

Responsabilidad:

- rutas base;
- URLs;
- puertos;
- modelo Ollama;
- flags de simulación;
- idioma;
- valores por defecto;
- activación/desactivación de funciones.

Recomendación: centralizar aquí valores como:

```python
APP_NAME = "Ahootsa"
APP_VERSION = "5.0.25"
OLLAMA_HOST = "http://127.0.0.1:11434"
DEFAULT_LANGUAGE = "es-ES"
ENABLE_AUTO_ANIMATIONS = True
ENABLE_OLLAMA = True
ENABLE_CAMERA = False
```

---

## 10. Endpoints HTTP importantes

### 10.1. Endpoints observados en logs

Se observaron estas peticiones repetidas:

```text
GET /voices/current HTTP/1.1 404 Not Found
GET /status HTTP/1.1 404 Not Found
GET /mic HTTP/1.1 404 Not Found
```

Significado:

| Endpoint | Quién lo llama | Para qué sirve |
|---|---|---|
| `/status` | Frontend/Desktop | Saber si el backend está vivo. |
| `/mic` | Frontend | Consultar estado del micro. |
| `/voices/current` | Frontend | Saber qué voz está activa. |
| `/voices` | Frontend o panel de configuración | Listar voces disponibles. |

### 10.2. Corrección 5.0.27

La versión 5.0.27 añade un bootstrap que devuelve respuestas mínimas:

```json
{
  "ok": true,
  "status": "running",
  "app": "Ahootsa",
  "version": "5.0.27",
  "compatibility": true
}
```

Para `/mic`:

```json
{
  "ok": true,
  "available": false,
  "enabled": false,
  "recording": false,
  "source": "compatibility_stub"
}
```

Para `/voices/current`:

```json
{
  "ok": true,
  "voice": {
    "id": "system",
    "name": "Voz del sistema",
    "language": "es-ES",
    "engine": "pyttsx3_or_browser"
  }
}
```

Esto no implementa todavía un sistema completo de voz/micro. Su objetivo es que la interfaz no reciba 404 y pueda seguir funcionando.

### 10.3. Comprobación manual

Con la app arrancada:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:7860/status
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:7860/mic
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:7860/voices/current
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:7860/voices
```

O usando el script incluido:

```powershell
powershell -ExecutionPolicy Bypass -File .\1_COMPROBAR_ENDPOINTS_5_0_27.ps1
```

Si el puerto no es 7860:

```powershell
powershell -ExecutionPolicy Bypass -File .\1_COMPROBAR_ENDPOINTS_5_0_27.ps1 -Port 8000
```

---

## 11. Flujo de arranque recomendado

```text
1. Usuario ejecuta LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
2. Script calcula Root, Logs y Session
3. Script localiza apps_venv/python.exe
4. Script localiza reachy-mini-daemon.exe
5. Script comprueba import de ahootsa_realtime_ollama_desktop_app
6. Script comprueba import de mujoco
7. Script arranca daemon/simulador/backend
8. Frontend empieza a consultar endpoints
9. Backend responde a chat, actividades, voz, robot y estado
10. Logs guardan pantalla/eventos/runtime
```

Punto crítico: si falla el paso 5, el paquete Ahootsa no está instalado o el entorno no es correcto.  
Si falla el paso 6, falta MuJoCo en `apps_venv`.  
Si aparecen 404, faltan endpoints esperados por la UI.

---

## 12. Cómo modificar el código sin perderse

### 12.1. Paso 1: localizar el código real

```powershell
$py = "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe"
& $py -c "import ahootsa_realtime_ollama_desktop_app as p; print(p.__file__)"
```

Abrir esa carpeta en VS Code:

```powershell
code "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Lib\site-packages\ahootsa_realtime_ollama_desktop_app"
```

### 12.2. Paso 2: hacer copia de seguridad

Antes de tocar:

```powershell
Copy-Item `
  "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Lib\site-packages\ahootsa_realtime_ollama_desktop_app" `
  "D:\RITXI\backup_ahootsa_realtime_ollama_desktop_app_$(Get-Date -Format yyyyMMdd_HHmmss)" `
  -Recurse
```

### 12.3. Paso 3: localizar el módulo por palabras clave

Buscar IA/Ollama:

```powershell
Select-String -Path "...\ahootsa_realtime_ollama_desktop_app\*.py" -Pattern "ollama","ask_ollama","model" -Recurse
```

Buscar robot/bailes:

```powershell
Select-String -Path "...\ahootsa_realtime_ollama_desktop_app\*.py" -Pattern "dance","emotion","move_head","idle" -Recurse
```

Buscar endpoints:

```powershell
Select-String -Path "...\ahootsa_realtime_ollama_desktop_app\*.py" -Pattern "@","FastAPI","Starlette","route","/status","/mic","/voices" -Recurse
```

Buscar actividades:

```powershell
Select-String -Path "...\ahootsa_realtime_ollama_desktop_app\*.py" -Pattern "activity","actividad","ficha","card" -Recurse
```

### 12.4. Paso 4: modificar una cosa cada vez

Orden recomendado:

1. Cambiar texto/prompt.
2. Probar import.
3. Probar arranque.
4. Probar endpoint o botón.
5. Revisar logs.
6. Solo después tocar otra función.

### 12.5. Paso 5: comprobar sintaxis

```powershell
$py = "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe"
& $py -m compileall "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Lib\site-packages\ahootsa_realtime_ollama_desktop_app"
```

Si esto falla, hay un error Python antes incluso de arrancar la app.

---

## 13. Reglas recomendadas para añadir funcionalidades

### 13.1. Añadir una nueva actividad

Pasos:

1. Crear definición de actividad:

   ```python
   {
       "id": "nombre_actividad",
       "title": "Nombre visible",
       "description": "Qué trabaja",
       "level": "iniciacion/avanzado/experto",
       "uses_ai": True,
       "uses_robot": True,
       "uses_micro": False,
   }
   ```

2. Añadir función ejecutora:

   ```python
   async def run_nombre_actividad(context):
       ...
   ```

3. Registrar actividad en el panel/listado.
4. Añadir log de inicio/fin/error.
5. Decidir si activa animación positiva.
6. Probar con una sesión corta.

### 13.2. Añadir un nuevo baile

Pasos:

1. Localizar lista de acciones permitidas.
2. Añadir identificador:

   ```text
   dance4
   ```

3. Asociarlo a una función real del robot/simulador.
4. Añadir fallback si no existe en robot real o MuJoCo.
5. Registrar en log:

   ```json
   {"type":"robot_action","action":"dance4"}
   ```

### 13.3. Cambiar modelo Ollama

Localizar configuración o función `ask_ollama` y cambiar:

```python
model = "nombre_modelo"
```

Comprobar modelos disponibles:

```powershell
ollama list
```

Probar llamada externa:

```powershell
ollama run nombre_modelo "Responde en una frase sencilla en español: hola"
```

### 13.4. Añadir endpoint nuevo

Si el backend usa FastAPI:

```python
@app.get("/nuevo-endpoint")
async def nuevo_endpoint():
    return {"ok": True}
```

Si no se conoce dónde está `app`, usar diagnóstico para localizar módulos con `FastAPI`, `Starlette`, `routes` o `uvicorn`.

---

## 14. Logs: qué mirar para depurar

### 14.1. `pantalla.log`

Mirar aquí si:

- la UI parece no responder;
- un botón no hace nada;
- no se ve una respuesta;
- una actividad no aparece.

### 14.2. `eventos.jsonl`

Mirar aquí si:

- quieres saber la secuencia exacta de eventos;
- necesitas medir latencias;
- quieres saber si una acción robot se lanzó;
- quieres reconstruir una sesión.

### 14.3. `runtime.log`

Mirar aquí si:

- hay traceback Python;
- falta un módulo;
- hay error de import;
- falla MuJoCo;
- hay 404/500 HTTP;
- falla conexión con daemon.

### 14.4. Ejemplo de interpretación

Error:

```text
ModuleNotFoundError: No module named 'mujoco'
```

Causa:

```text
mujoco no está instalado en apps_venv
```

Solución:

```powershell
$py = "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe"
& $py -m pip install mujoco
```

Error:

```text
GET /voices/current HTTP/1.1 404 Not Found
```

Causa:

```text
El frontend pide endpoint de voz, pero el backend no lo define.
```

Solución:

```text
Aplicar corrección 5.0.27 o implementar endpoint real.
```

---

## 15. Diferencia entre endpoint de compatibilidad y función real

La corrección 5.0.27 añade endpoints mínimos para evitar 404. Eso no significa que implemente toda la función real.

Ejemplo:

```text
/mic devuelve available=false
```

Eso significa:

- el endpoint existe;
- la UI no se rompe por 404;
- todavía no se está controlando micro real desde ese endpoint.

Para implementar micro real habría que añadir:

- detección de dispositivo;
- permisos del navegador;
- STT;
- estado de grabación;
- gestión de interrupciones;
- antieco;
- integración con conversación.

Lo mismo ocurre con `/voices/current`: la compatibilidad devuelve una voz genérica, pero una implementación completa debería listar voces reales de Windows, pyttsx3, navegador o motor TTS usado.

---

## 16. Arquitectura funcional de IA local

### 16.1. Flujo recomendado

```text
Usuario escribe/habla
        │
        ▼
Normalización de entrada
        │
        ▼
Clasificador simple de intención
        │
        ├── Actividad → activity_manager
        ├── Acción robot → robot/actions
        ├── Cámara → vision/camera
        └── Chat → ask_ollama
                       │
                       ▼
                Respuesta textual
                       │
                       ├── Mostrar en pantalla
                       ├── TTS opcional
                       └── Animación según regla
```

### 16.2. Cuándo llamar a Ollama

Criterio recomendado:

| Caso | ¿Llamar a Ollama? |
|---|---|
| Pregunta abierta del usuario | Sí |
| Actividad que necesita explicación personalizada | Sí |
| Botón de baile | No |
| Botón de emoción | No |
| Estado del sistema | No |
| Exploración de imagen con modelo multimodal local | Sí, si existe modelo compatible |
| Ficha con respuesta cerrada | Opcional |

### 16.3. Fallback si Ollama no responde

Ahootsa debe responder de forma controlada:

```text
Ahora no puedo consultar el modelo local. Puedo seguir con actividades básicas o intentarlo de nuevo.
```

Y registrar:

```json
{"type":"ollama_error","error":"timeout"}
```

---

## 17. Arquitectura funcional de robot

### 17.1. Acciones de bajo nivel

Ejemplos:

```text
move_head
idle
play_emotion
stop_emotion
dance
camera
```

### 17.2. Acciones de alto nivel

Ejemplos:

```text
saludar
celebrar respuesta correcta
animar a continuar
calmar
bailar
mirar al usuario
```

La app debería traducir acciones de alto nivel a acciones concretas compatibles con robot real o MuJoCo.

### 17.3. Fallback por modo

| Modo | Comportamiento |
|---|---|
| Robot real conectado | Ejecutar movimiento real. |
| MuJoCo web | Ejecutar movimiento simulado. |
| Mockup/sin robot | Registrar acción y mostrar texto. |

---

## 18. Recomendaciones de organización para futuras versiones

Cada ZIP completo debería incluir:

```text
instrucciones.txt
docs/ARQUITECTURA_FUNCIONALIDAD.md
docs/CAMBIOS_VERSION.md
docs/VERIFICACION.md
script principal de lanzamiento
script de diagnóstico
script de instalación/parche si procede
recursos necesarios
```

No debería incluir:

- scripts antiguos que ya no sirven;
- logs de sesiones anteriores salvo ejemplos pequeños;
- pruebas temporales;
- copias duplicadas del mismo código sin explicación.

### 18.1. Nombre recomendado de versiones

```text
5_0_25_ahootsa_logs_simples_actividades_recuperadas
5_0_26_ahootsa_endpoints_compatibilidad
5_0_27_ahootsa_bootstrap_endpoints_docs
```

Cada nombre debe indicar qué cambia.

### 18.2. `instrucciones.txt` recomendado

Debe contener:

```text
1. Qué corrige esta versión.
2. Qué script ejecutar.
3. Qué se debe ver por pantalla.
4. Qué logs revisar.
5. Cómo comprobar que funciona.
6. Qué hacer si falla.
7. Qué archivos se han cambiado.
```

---

## 19. Qué cambió en la corrección 5.0.27

### 19.1. Problema de 5.0.26

El parche 5.0.26 buscaba un archivo con algo parecido a:

```python
app = FastAPI(...)
```

pero el paquete instalado no contenía esa forma literal. Por eso falló:

```text
[ERROR] No he encontrado ningun archivo con app = FastAPI(...).
No se ha modificado nada.
El parche de endpoints no se pudo aplicar.
```

### 19.2. Solución de 5.0.27

La 5.0.27 modifica el enfoque:

- localiza el paquete importado `ahootsa_realtime_ollama_desktop_app`;
- abre su `__init__.py`;
- crea copia de seguridad;
- inserta un bootstrap al principio;
- el bootstrap parchea la creación de apps FastAPI/Starlette;
- cuando se crea una app, añade rutas de compatibilidad;
- también intenta parchear apps ya cargadas.

Así no depende del nombre de variable `app`.

### 19.3. Archivo modificado

Archivo modificado en el entorno de Reachy Mini Control:

```text
C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Lib\site-packages\ahootsa_realtime_ollama_desktop_app\__init__.py
```

Antes de modificarlo, se crea un backup:

```text
__init__.py.bak_5_0_27_YYYYMMDD_HHMMSS
```

---

## 20. Checklist para entender y cambiar el código

### 20.1. Antes de tocar nada

```text
[ ] Sé qué carpeta local estoy usando.
[ ] Sé qué Python usa la app.
[ ] Sé dónde está el paquete instalado.
[ ] Tengo copia de seguridad.
[ ] Puedo lanzar la app y reproducir el fallo.
[ ] Sé qué log mirar.
```

### 20.2. Después de cambiar código

```text
[ ] compileall OK.
[ ] Import del paquete OK.
[ ] MuJoCo importa OK.
[ ] Script arranca OK.
[ ] No hay traceback.
[ ] No hay 404 repetidos esperados.
[ ] La funcionalidad modificada responde.
[ ] Eventos quedan registrados en jsonl.
```

### 20.3. Para documentar el cambio

```text
[ ] Añadir explicación en instrucciones.txt.
[ ] Añadir cambio en docs/CAMBIOS_VERSION.md.
[ ] Actualizar docs/ARQUITECTURA_FUNCIONALIDAD.md si cambia arquitectura.
[ ] Indicar cómo probarlo.
```

---

## 21. Comandos útiles de diagnóstico rápido

### Ver Python real

```powershell
$py = "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe"
& $py --version
```

### Ver paquete Ahootsa

```powershell
& $py -c "import ahootsa_realtime_ollama_desktop_app as p; print(p.__file__)"
```

### Ver MuJoCo

```powershell
& $py -c "import mujoco; print(mujoco.__version__)"
```

### Compilar paquete

```powershell
& $py -m compileall "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Lib\site-packages\ahootsa_realtime_ollama_desktop_app"
```

### Buscar errores en runtime log

```powershell
Select-String -Path "D:\RITXI\logs\*_runtime.log" -Pattern "Traceback","ERROR","404","500","ModuleNotFoundError"
```

### Buscar endpoints 404

```powershell
Select-String -Path "D:\RITXI\logs\*_runtime.log" -Pattern "404 Not Found"
```

### Ver últimos logs

```powershell
Get-ChildItem D:\RITXI\logs | Sort-Object LastWriteTime -Descending | Select-Object -First 10
```

---

## 22. Riesgos y precauciones

### 22.1. Modificar `site-packages`

Modificar directamente `site-packages` es práctico para pruebas, pero tiene riesgos:

- una reinstalación puede borrar cambios;
- es más difícil comparar versiones;
- puede quedar código parcheado sin documentar.

Por eso cada parche debe:

- crear backup;
- dejar marca en el archivo;
- documentar qué ha cambiado;
- poder detectarse si ya está aplicado.

### 22.2. Dependencias en el Python equivocado

Error común:

```powershell
pip install paquete
```

Puede instalar en otro Python. Usar siempre:

```powershell
& $py -m pip install paquete
```

con `$py` apuntando a `apps_venv`.

### 22.3. Frontend y backend desalineados

Si el frontend pide rutas que el backend no tiene, aparecen 404. Puede pasar al mezclar:

- frontend nuevo con backend antiguo;
- backend nuevo con frontend antiguo;
- código oficial reutilizado con rutas no implementadas en Ahootsa.

Solución:

- añadir endpoints de compatibilidad;
- o cambiar el frontend para no llamar esas rutas;
- o implementar la función real.

---

## 23. Roadmap técnico recomendado

### Fase 1: estabilizar arranque

- MuJoCo instalado en `apps_venv`.
- Ahootsa importa OK.
- Daemon arranca.
- Sin tracebacks.
- Sin 404 repetidos básicos.

### Fase 2: estabilizar interfaz

- Paneles cargan.
- Botones responden.
- Chat muestra respuesta.
- Actividades aparecen.
- Logs registran eventos.

### Fase 3: recuperar funciones

- `ask_ollama` funcional.
- Explorar imagen funcional o fallback claro.
- Bailes funcionales.
- Emociones funcionales.
- Actividades con micro/sonido revisadas.

### Fase 4: mejorar calidad de interacción

- Una pregunta por turno.
- Refuerzo positivo.
- Ritmo ajustable.
- Lenguaje sencillo.
- Reconducción si se desvía.
- Perfil adaptativo.

### Fase 5: mantenimiento

- Documentación por versión.
- Scripts mínimos.
- Logs sencillos.
- Tests/manual de verificación.
- Copia limpia instalable.

---

## 24. Resumen final para nuevos desarrolladores

Para entender Ahootsa hay que recordar tres ideas:

1. **No todo está en la carpeta `D:\RITXI\5_0_25...`**.  
   Esa carpeta lanza y documenta la versión, pero el backend Python real suele estar instalado dentro de `apps_venv\site-packages`.

2. **Ahootsa reutiliza la filosofía de `reachy_mini_conversation_app`**.  
   Usa estructura de app conversacional, perfiles, herramientas e integración con Reachy Mini, pero añade lógica propia para castellano, Ollama, actividades, logs, emociones, bailes y simulación MuJoCo.

3. **Para cambiar código hay que localizar primero el paquete real importado por el Python de Reachy Mini Control**.  
   El comando clave es:

   ```powershell
   $py = "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe"
   & $py -c "import ahootsa_realtime_ollama_desktop_app as p; print(p.__file__)"
   ```

A partir de ahí, se puede buscar por palabras clave, modificar una función concreta, compilar, arrancar y revisar logs.

---

## 25. Anexo: estructura mental mínima del código

```text
PowerShell launcher
    └── localiza apps_venv
        └── importa paquete Ahootsa
            ├── backend ASGI/FastAPI/Starlette
            │   ├── endpoints estado/voz/micro
            │   ├── endpoints chat/actividades
            │   └── endpoints robot/simulación
            │
            ├── conversación
            │   ├── clasificación de intención
            │   ├── prompts/perfiles
            │   └── ask_ollama
            │
            ├── actividades
            │   ├── fichas
            │   ├── niveles
            │   └── refuerzo positivo
            │
            ├── robot
            │   ├── emociones
            │   ├── bailes
            │   ├── cabeza/idle
            │   └── cámara
            │
            ├── voz/audio
            │   ├── TTS
            │   ├── STT/micro
            │   └── estado de voz
            │
            └── logs
                ├── pantalla.log
                ├── eventos.jsonl
                └── runtime.log
```

Este mapa debe usarse como referencia para futuras modificaciones y para decidir dónde añadir nuevas funciones sin mezclar responsabilidades.
