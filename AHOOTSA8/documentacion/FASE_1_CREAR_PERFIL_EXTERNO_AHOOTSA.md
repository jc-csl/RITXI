# Ahootsa 8 — Fase 1  
## Crear el perfil externo `ahootsa`

**Documento:** Fase 1  
**Proyecto:** Ahootsa 8  
**Revisión:** 1.1 — 11 de julio de 2026  
**Requisito previo:** Fase 0 completada  
**Objetivo:** añadir un perfil externo especializado sin modificar el código oficial

---

## 1. Objetivo de la fase

Crear el primer perfil externo de Ahootsa utilizando la estructura oficial de `reachy_mini_conversation_app`.

En esta fase se configura únicamente:

- comportamiento conversacional;
- comunicación accesible;
- trato adulto y no infantilizante;
- movimientos y emociones suaves;
- selección explícita de herramientas oficiales permitidas.

No se incorporan todavía:

- herramientas Python propias;
- actividades;
- juegos;
- Ollama;
- cámara;
- memoria;
- bailes;
- configuración definitiva de voz;
- saludo de inicio personalizado mediante `greeting.txt`.

### Delimitación entre la Fase 1 y la Fase 2

La aplicación admite cuatro archivos principales dentro de un perfil externo, pero en esta fase se crean únicamente los dos necesarios para validar la carga técnica y el comportamiento básico:

| Elemento | Fase |
|---|---|
| `instructions.txt` | Fase 1: comportamiento base de Ahootsa. |
| `tools.txt` | Fase 1: lista estricta de herramientas permitidas. |
| `REALTIME_TRANSCRIPTION_LANGUAGE=es` | Fase 1: ajuste mínimo para poder probar el perfil en español. |
| `greeting.txt` | Fase 2: saludo de inicio definitivo. |
| `voice.txt` | Fase 2: selección y validación de voz. |
| Ajuste fino de personalidad, ritmo y lenguaje | Fase 2. |

Por tanto, no se crea todavía `voice.txt` con `Serena` ni se presupone que esa voz esté disponible. La voz predeterminada depende del backend y debe comprobarse en la Fase 2.

Resultado esperado:

```text
Fase 1
└── creación del perfil externo Ahootsa
```

---

## 2. Requisitos previos

Antes de comenzar deben funcionar:

- `.venv` propio;
- aplicación oficial `0.9.0`;
- SDK `1.9.0`;
- MuJoCo `3.3.0`;
- daemon en el puerto `8000`;
- interfaz en el puerto `7860`;
- conversación, audio y movimiento básicos.

Comprobación rápida:

```powershell
cd D:\ritxi\AHOOTSA8\reachy_mini_conversation_app
.\.venv\Scripts\Activate.ps1

python -c "from importlib.metadata import version; print(version('reachy-mini-conversation-app')); print(version('reachy-mini')); print(version('mujoco'))"
```

Resultado esperado:

```text
0.9.0
1.9.0
3.3.0
```

### 2.1. Antes de editar: detener solo la aplicación

Si la aplicación oficial está abierta, detener únicamente ese proceso en su terminal:

```text
Ctrl + C
```

Mantener abiertos:

- el daemon de Reachy Mini;
- la ventana 3D de MuJoCo.

Comprobar que el daemon sigue disponible:

```powershell
Test-NetConnection 127.0.0.1 -Port 8000
```

Debe mostrar:

```text
TcpTestSucceeded : True
```

No es necesario reiniciar MuJoCo para crear o editar el perfil.

---

## 3. Estructura oficial de contenidos externos

La aplicación ya contiene:

```text
external_content\
├── external_profiles\
│   └── starter_profile\
│       ├── instructions.txt
│       └── tools.txt
│
├── external_tools\
│   └── starter_custom_tool.py
│
└── installed_tool_spaces.json
```

### Función de cada elemento

| Elemento | Función |
|---|---|
| `external_profiles` | Contiene perfiles externos. Cada subcarpeta es una personalidad. |
| `starter_profile` | Perfil de ejemplo. No se modifica. |
| `external_tools` | Contendrá las herramientas Python externas en fases posteriores. |
| `starter_custom_tool.py` | Herramienta externa de ejemplo. No pertenece a Ahootsa. |
| `installed_tool_spaces.json` | Registro administrado por la aplicación para herramientas MCP/Hugging Face Spaces. No se edita manualmente. |

---

## 4. Estructura final esperada

```text
D:\ritxi\AHOOTSA8\reachy_mini_conversation_app\
│
├── .venv\                         # Entorno virtual. No editar.
├── .env                            # Crear y configurar.
├── .env.example                    # Plantilla oficial. No modificar.
├── pyproject.toml                  # Ya modificado en la Fase 0.
├── uv.lock                         # Administrado por uv.
│
├── external_content\
│   ├── external_profiles\
│   │   ├── starter_profile\        # Ejemplo oficial. No modificar.
│   │   │   ├── instructions.txt
│   │   │   └── tools.txt
│   │   │
│   │   └── ahootsa\                # Nuevo perfil.
│   │       ├── instructions.txt
│   │       └── tools.txt
│   │
│   ├── external_tools\
│   │   └── starter_custom_tool.py  # Ejemplo oficial. No modificar.
│   │
│   └── installed_tool_spaces.json  # No modificar.
│
├── profiles\                       # Perfiles internos. No modificar.
│   └── default\
│
└── src\
    └── reachy_mini_conversation_app\
        └── tools\                  # Herramientas oficiales. No modificar.
```

---

## 5. Archivos que se modifican o crean

En esta fase:

```text
CREAR O CONFIGURAR:
.env
external_content\external_profiles\ahootsa\
external_content\external_profiles\ahootsa\instructions.txt
external_content\external_profiles\ahootsa\tools.txt

NO CREAR TODAVÍA:
external_content\external_profiles\ahootsa\greeting.txt
external_content\external_profiles\ahootsa\voice.txt
```

No se modifica código Python.

---

## 6. Crear `.env`

Desde la raíz:

```powershell
cd D:\ritxi\AHOOTSA8\reachy_mini_conversation_app
```

Comprobar si existe:

```powershell
Test-Path .\.env
```

Si devuelve `False`:

```powershell
Copy-Item .\.env.example .\.env
```

Abrir:

```powershell
notepad .\.env
```

Añadir o dejar activas estas líneas:

```env
# Transcripción de entrada en español
REALTIME_TRANSCRIPTION_LANGUAGE=es

# Backend oficial integrado de Hugging Face
HF_REALTIME_CONNECTION_MODE=deployed

# Raíz de perfiles externos
REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY=./external_content/external_profiles

# Perfil inicial
REACHY_MINI_CUSTOM_PROFILE=ahootsa
```

### Variables que no se añaden todavía

```env
REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY
AUTOLOAD_EXTERNAL_TOOLS
HF_REALTIME_WS_URL
```

#### Motivo

- No existen todavía herramientas propias de Ahootsa.
- En esta fase solo se utilizan herramientas oficiales.
- `AUTOLOAD_EXTERNAL_TOOLS` cargaría automáticamente archivos Python externos y reduciría el control sobre qué herramientas quedan activas.
- `HF_REALTIME_WS_URL` solo es necesario para un backend local.

No deben existir dos definiciones activas de una misma variable en `.env`. Comprobarlo:

```powershell
$variables = @(
    "REALTIME_TRANSCRIPTION_LANGUAGE",
    "HF_REALTIME_CONNECTION_MODE",
    "REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY",
    "REACHY_MINI_CUSTOM_PROFILE"
)

foreach ($variable in $variables) {
    $numero = (
        Select-String -Path .\.env -Pattern "^\s*$variable\s*="
    ).Count
    "$variable -> $numero"
}
```

Resultado esperado:

```text
REALTIME_TRANSCRIPTION_LANGUAGE -> 1
HF_REALTIME_CONNECTION_MODE -> 1
REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY -> 1
REACHY_MINI_CUSTOM_PROFILE -> 1
```

---



## 7. Crear la carpeta del perfil

### Opción recomendada: copiar la plantilla oficial

```powershell
Copy-Item `
  .\external_content\external_profiles\starter_profile `
  .\external_content\external_profiles\ahootsa `
  -Recurse
```

Comprobar:

```powershell
Get-ChildItem .\external_content\external_profiles\ahootsa
```

Debe mostrar:

```text
instructions.txt
tools.txt
```

A continuación se reemplaza completamente el contenido de ambos archivos.

### Alternativa: crear la carpeta manualmente

```powershell
New-Item `
  -ItemType Directory `
  -Path .\external_content\external_profiles\ahootsa `
  -Force

New-Item `
  -ItemType File `
  -Path .\external_content\external_profiles\ahootsa\instructions.txt `
  -Force

New-Item `
  -ItemType File `
  -Path .\external_content\external_profiles\ahootsa\tools.txt `
  -Force
```

### Abrir manualmente los dos archivos

```powershell
notepad .\external_content\external_profiles\ahootsa\instructions.txt
notepad .\external_content\external_profiles\ahootsa\tools.txt
```

Guardar ambos como texto UTF-8. No crear todavía `greeting.txt` ni `voice.txt`.

---

## 8. Archivo `instructions.txt`

Ruta:

```text
D:\ritxi\AHOOTSA8\reachy_mini_conversation_app\
└── external_content\
    └── external_profiles\
        └── ahootsa\
            └── instructions.txt
```

Contenido completo:

```text
Eres Ahootsa, una monitora digital especializada en acompañar a personas con discapacidad intelectual.

Tu objetivo es mantener conversaciones comprensibles, respetuosas, positivas y adaptadas a las necesidades de cada persona.

IDIOMA

Habla siempre en español, salvo que la persona pida expresamente otro idioma.

FORMA DE COMUNICARTE

Habla de forma amable, paciente, cercana y respetuosa.

Utiliza un lenguaje adulto. Nunca infantilices a la persona.

Utiliza frases cortas y vocabulario sencillo.

Explica una idea cada vez.

Haz una sola pregunta cada vez.

Da tiempo suficiente para que la persona responda.

Evita hablar demasiado rápido o dar explicaciones largas.

No utilices tecnicismos innecesarios.

COMPRENSIÓN

Si la persona no entiende algo:

- repítelo de otra manera;
- utiliza palabras más sencillas;
- divide la explicación en pasos pequeños;
- ofrece un ejemplo;
- no muestres impaciencia;
- no hagas sentir mal a la persona.

Si la respuesta de la persona no está clara, pregunta con respeto antes de asumir lo que quiere decir.

ELECCIONES

Cuando propongas alternativas, ofrece como máximo dos opciones cada vez.

Por ejemplo:

“¿Prefieres hablar de música o hacer una actividad?”

No presentes listas largas de opciones.

AUTONOMÍA

Respeta las decisiones de la persona.

Pregunta antes de iniciar una actividad.

Acepta que la persona no quiera participar.

Permite cambiar de tema, descansar o terminar la conversación.

Si la persona dice “para”, “no quiero” o algo equivalente, detén inmediatamente la actividad.

APOYO POSITIVO

Reconoce el esfuerzo y la participación de forma natural.

Puedes utilizar expresiones como:

- “Muy bien.”
- “Buen intento.”
- “Lo estás haciendo bien.”
- “Gracias por explicármelo.”
- “Podemos probar otra vez con calma.”

No exageres los elogios y no trates a la persona como a un niño.

SEGURIDAD

No realices diagnósticos.

No des instrucciones médicas.

No sustituyas a profesionales, familiares ni personas de apoyo.

Si la persona expresa una situación grave, de peligro o de emergencia, recomienda solicitar ayuda inmediatamente a una persona de confianza o a los servicios de emergencia.

MOVIMIENTOS

Puedes utilizar movimientos de cabeza y emociones suaves cuando ayuden a acompañar la conversación.

No realices movimientos continuos, bruscos o innecesarios.

En esta primera fase no uses bailes, cámara, memoria ni actividades externas.

INICIO DE LA CONVERSACIÓN

Saluda de forma breve y amable.

Preséntate como Ahootsa.

Pregunta cómo está la persona o si le apetece hablar.

Haz solamente una pregunta en el saludo inicial.
```

### Comprobación del archivo

```powershell
Get-Content .\external_content\external_profiles\ahootsa\instructions.txt
```

Comprobar que:

- no está vacío;
- comienza con `Eres Ahootsa`;
- está guardado como texto UTF-8;
- conserva tildes y caracteres españoles.

---

## 9. Archivo `tools.txt`

Ruta:

```text
D:\ritxi\AHOOTSA8\reachy_mini_conversation_app\
└── external_content\
    └── external_profiles\
        └── ahootsa\
            └── tools.txt
```

Contenido:

```text
# Movimiento sencillo de cabeza
move_head

# Emociones del robot
play_emotion
stop_emotion

# Permite permanecer quieto cuando corresponda
idle_do_nothing

# Dormir únicamente cuando la persona lo pida expresamente
go_to_sleep
```

### Herramientas habilitadas

| Herramienta | Uso |
|---|---|
| `move_head` | Movimiento sencillo de cabeza. |
| `play_emotion` | Reproduce una emoción. |
| `stop_emotion` | Detiene emociones en cola. |
| `idle_do_nothing` | Permite permanecer quieto cuando corresponda. |
| `go_to_sleep` | Duerme y detiene la aplicación únicamente ante una petición explícita. |

### Herramientas no habilitadas todavía

```text
dance
stop_dance
camera
head_tracking
remember
forget
starter_custom_tool
```

#### Motivo

- `dance` y `stop_dance`: se comprobarán de forma controlada en la Fase 3.
- `camera` y `head_tracking`: requieren pruebas específicas de cámara.
- `remember` y `forget`: implican persistencia y privacidad.
- `starter_custom_tool`: pertenece a la plantilla de ejemplo y no es una función de Ahootsa.

### Comprobación del archivo

```powershell
Get-Content .\external_content\external_profiles\ahootsa\tools.txt
```

Comprobar los nombres activos sin comentarios:

```powershell
Get-Content .\external_content\external_profiles\ahootsa\tools.txt |
    Where-Object { $_.Trim() -and -not $_.Trim().StartsWith("#") }
```

Resultado esperado:

```text
move_head
play_emotion
stop_emotion
idle_do_nothing
go_to_sleep
```

---

## 10. Archivos opcionales que no se crean todavía

### `greeting.txt`

Es opcional. Permite enviar una instrucción interna para que el modelo inicie la conversación con un saludo variable.

No se crea en esta fase porque primero se comprobará el saludo producido por `instructions.txt` y el saludo predeterminado de la aplicación. En la respuesta del endpoint de carga, el campo `greeting` deberá aparecer vacío.

### `voice.txt`

Es opcional. Permite definir una voz concreta para el perfil.

No se crea en esta fase. La selección y validación de voz pertenece a la Fase 2. Al no existir este archivo, la aplicación utilizará su voz predeterminada y el endpoint deberá indicar:

```text
uses_default_voice : True
```

El valor mostrado en `voice` puede variar según el backend. En esta fase no se exige `Serena`.

### Comprobar que ambos archivos siguen ausentes

```powershell
Test-Path .\external_content\external_profiles\ahootsa\greeting.txt
Test-Path .\external_content\external_profiles\ahootsa\voice.txt
```

Resultado esperado:

```text
False
False
```

### Herramientas Python dentro del perfil

Un perfil puede incluir herramientas Python propias, pero no se incorporan en esta fase.

### `external_tools`

La carpeta se mantiene con el ejemplo oficial:

```text
external_content\external_tools\starter_custom_tool.py
```

No se modifica ni se carga.

---

## 11. Archivos que no se modifican

Deben permanecer intactos:

```text
external_content\external_profiles\starter_profile\
external_content\external_tools\starter_custom_tool.py
external_content\installed_tool_spaces.json
profiles\
src\reachy_mini_conversation_app\
.env.example
pyproject.toml
uv.lock
```

Tampoco se modifica:

```text
src\reachy_mini_conversation_app\config.py
```

No se utiliza todavía `LOCKED_PROFILE`.

---

## 12. Estructura resultante

```text
external_content\
├── external_profiles\
│   ├── starter_profile\
│   │   ├── instructions.txt
│   │   └── tools.txt
│   │
│   └── ahootsa\
│       ├── instructions.txt
│       └── tools.txt
│
├── external_tools\
│   └── starter_custom_tool.py
│
└── installed_tool_spaces.json
```

Comprobar:

```powershell
tree .\external_content /F
```

Comprobar que el perfil contiene exactamente los dos archivos previstos:

```powershell
Get-ChildItem .\external_content\external_profiles\ahootsa -File |
    Select-Object -ExpandProperty Name
```

Resultado esperado:

```text
instructions.txt
tools.txt
```

---

## 13. Comprobar `.env`

```powershell
Get-Content .\.env |
    Select-String "REALTIME_TRANSCRIPTION_LANGUAGE|HF_REALTIME_CONNECTION_MODE|REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY|REACHY_MINI_CUSTOM_PROFILE"
```

Resultado esperado:

```text
REALTIME_TRANSCRIPTION_LANGUAGE=es
HF_REALTIME_CONNECTION_MODE=deployed
REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY=./external_content/external_profiles
REACHY_MINI_CUSTOM_PROFILE=ahootsa
```

Comprobar que la carpeta configurada existe:

```powershell
Test-Path .\external_content\external_profiles
Test-Path .\external_content\external_profiles\ahootsa
```

Ambos deben devolver:

```text
True
```

---

## 14. Arrancar la Fase 1

### Terminal 1 — daemon y MuJoCo

Si el daemon y MuJoCo continúan abiertos desde la Fase 0, no reiniciarlos. Comprobar únicamente:

```powershell
Test-NetConnection 127.0.0.1 -Port 8000
```

Si no están abiertos, iniciar el daemon:

```powershell
cd D:\ritxi\AHOOTSA8\reachy_mini_conversation_app
.\.venv\Scripts\Activate.ps1

reachy-mini-daemon --sim --scene minimal
```

Esperar a que aparezca la ventana 3D.

### Terminal 2 — aplicación

```powershell
cd D:\ritxi\AHOOTSA8\reachy_mini_conversation_app
.\.venv\Scripts\Activate.ps1

reachy-mini-conversation-app --ui --debug
```

Abrir:

```text
http://127.0.0.1:7860
```

---


### Consultar todas las rutas FastAPI

La documentación interactiva incorporada desde la Fase 0 continúa disponible en:

```text
http://127.0.0.1:7860/docs
```

Para ver las operaciones de perfiles utilizadas en esta fase:

```text
GET  /api/v1/personalities
GET  /api/v1/personalities/load
POST /api/v1/personalities/apply
```

La lista real y completa siempre debe consultarse en Swagger o en:

```text
http://127.0.0.1:7860/openapi.json
```


## 15. Comprobaciones técnicas del perfil

### 15.1. Comprobar que la API ve el perfil

```powershell
Invoke-RestMethod http://127.0.0.1:7860/api/v1/personalities |
    ConvertTo-Json -Depth 6
```

Debe aparecer `ahootsa` dentro de `choices`.

Ejemplo esperado:

```json
{
  "choices": [
    "(built-in default)",
    "ahootsa",
    "starter_profile"
  ],
  "current": "ahootsa",
  "startup": "ahootsa",
  "locked": false,
  "locked_to": null
}
```

El orden puede variar.

### 15.2. Comprobar el contenido cargado

```powershell
Invoke-RestMethod "http://127.0.0.1:7860/api/v1/personalities/load?name=ahootsa" |
    ConvertTo-Json -Depth 8
```

Comprobar:

- `instructions` comienza con `Eres Ahootsa`;
- `enabled_tools` contiene las cinco herramientas definidas;
- `greeting` está vacío porque todavía no existe `greeting.txt`;
- `uses_default_voice` es `true` porque todavía no existe `voice.txt`;
- `voice` muestra la voz predeterminada del backend, sin exigir un nombre concreto.

### 15.3. Validación automática mínima

```powershell
$perfil = Invoke-RestMethod "http://127.0.0.1:7860/api/v1/personalities/load?name=ahootsa"

$esperadas = @(
    "move_head",
    "play_emotion",
    "stop_emotion",
    "idle_do_nothing",
    "go_to_sleep"
)

[PSCustomObject]@{
    InstruccionesAhootsa = $perfil.instructions.StartsWith("Eres Ahootsa")
    SaludoPersonalizadoAusente = [string]::IsNullOrWhiteSpace($perfil.greeting)
    UsaVozPredeterminada = $perfil.uses_default_voice
    HerramientasCorrectas = (
        @($perfil.enabled_tools | Sort-Object) -join ","
    ) -eq (
        @($esperadas | Sort-Object) -join ","
    )
}
```

Todos los valores deben ser:

```text
True
```

### 15.4. Comprobar el perfil actual

```powershell
(Invoke-RestMethod http://127.0.0.1:7860/api/v1/personalities).current
```

Resultado esperado:

```text
ahootsa
```

Si devuelve otro perfil:

1. Seleccionar `ahootsa` en la interfaz.
2. Aplicar el perfil.
3. Marcarlo como perfil de inicio si la interfaz ofrece esa opción.
4. Repetir la consulta.

---

## 16. Precedencia del perfil guardado

La interfaz puede guardar la selección en:

```text
startup_settings.json
```

Una selección persistida desde la interfaz puede prevalecer sobre el valor inicial de:

```env
REACHY_MINI_CUSTOM_PROFILE=ahootsa
```

Por eso:

- `REACHY_MINI_CUSTOM_PROFILE` sirve para sembrar la selección inicial;
- después debe comprobarse el valor real mediante `/api/v1/personalities`;
- si otro perfil está persistido, seleccionar Ahootsa desde la interfaz y guardarlo como perfil de inicio.

No es necesario borrar archivos manualmente mientras la interfaz permita cambiar y guardar el perfil.

---

## 17. Logs esperados

Con `--debug`, deben aparecer mensajes equivalentes a:

```text
Environment variable 'REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY' is set.
Profiles (...) will be loaded from external_content/external_profiles.
```

Al cargar herramientas:

```text
Loading tools for profile: ahootsa
Loading external profile 'ahootsa' from ...
Found ... tools to load
```

No deben aparecer:

```text
Selected profile 'ahootsa' was not found
tools.txt not found
Failed to load profile tool
Duplicate Tool.name values detected
```

---

## 18. Pruebas conversacionales recomendadas

Antes de probar, confirmar que `current` es `ahootsa`. Si se ha editado `instructions.txt` o `tools.txt` con la aplicación abierta, volver a seleccionar el perfil en la interfaz o reiniciar únicamente la aplicación para recargar los archivos.

Realizar las pruebas una a una.

### Prueba 1 — Presentación

Usuario:

```text
Hola.
```

Comprobar:

- se presenta como Ahootsa;
- saluda de forma breve;
- realiza una sola pregunta;
- habla en español.

### Prueba 2 — Explicación sencilla

Usuario:

```text
Explícame qué podemos hacer.
```

Comprobar:

- frases cortas;
- vocabulario sencillo;
- pocas opciones;
- no introduce actividades todavía inexistentes.

### Prueba 3 — Reformulación

Usuario:

```text
No lo he entendido.
```

Comprobar:

- reformula;
- divide la explicación;
- no reprende;
- no repite exactamente el mismo texto.

### Prueba 4 — Dos opciones

Usuario:

```text
Dame dos opciones.
```

Comprobar que ofrece como máximo dos alternativas.

### Prueba 5 — Una pregunta por turno

Usuario:

```text
Pregúntame algo.
```

Comprobar que no encadena varias preguntas.

### Prueba 6 — Respeto a la negativa

Usuario:

```text
No quiero seguir.
```

Comprobar:

- acepta la decisión;
- no insiste;
- ofrece parar o despedirse;
- no inicia otra actividad.

### Prueba 7 — Movimiento suave

Usuario:

```text
Salúdame con un movimiento suave.
```

Comprobar:

- utiliza `move_head` o una emoción apropiada;
- el movimiento se ve en MuJoCo;
- no inicia un baile;
- no mantiene movimientos repetitivos.

### Prueba 8 — Cámara todavía no habilitada

Usuario:

```text
¿Qué ves?
```

Comprobar que no inventa contenido visual ni afirma haber usado la cámara.

### Prueba 9 — Memoria todavía no habilitada

Usuario:

```text
Recuerda que me gusta la música.
```

Comprobar que no afirma haber guardado memoria persistente mediante la herramienta `remember`, porque aún no está habilitada.

---

## 19. Comprobación de herramientas cargadas

La respuesta del endpoint:

```powershell
$perfil = Invoke-RestMethod "http://127.0.0.1:7860/api/v1/personalities/load?name=ahootsa"
$perfil.enabled_tools
```

Debe contener:

```text
move_head
play_emotion
stop_emotion
idle_do_nothing
go_to_sleep
```

Comprobar que no contiene:

```powershell
$noPermitidas = @(
    "dance",
    "stop_dance",
    "camera",
    "head_tracking",
    "remember",
    "forget",
    "starter_custom_tool"
)

$perfil.enabled_tools | Where-Object { $_ -in $noPermitidas }
```

No debe devolver nada.

---

## 20. Criterios de aceptación

La Fase 1 se considera terminada cuando:

- [ ] Existe `.env`.
- [ ] La transcripción está configurada en español.
- [ ] La raíz de perfiles externos está configurada.
- [ ] `REACHY_MINI_CUSTOM_PROFILE=ahootsa`.
- [ ] Existe `external_content\external_profiles\ahootsa`.
- [ ] `instructions.txt` contiene el comportamiento completo.
- [ ] `tools.txt` contiene solo las herramientas autorizadas.
- [ ] No existen todavía `greeting.txt` ni `voice.txt`.
- [ ] El endpoint indica `uses_default_voice=true`.
- [ ] La aplicación arranca sin errores.
- [ ] `ahootsa` aparece en `/api/v1/personalities`.
- [ ] El perfil actual es `ahootsa`.
- [ ] El endpoint de carga devuelve las instrucciones correctas.
- [ ] El endpoint de carga devuelve las cinco herramientas previstas.
- [ ] La conversación comienza en español.
- [ ] Ahootsa utiliza frases cortas.
- [ ] Formula una pregunta cada vez.
- [ ] Ofrece como máximo dos opciones.
- [ ] Reformula cuando no se entiende.
- [ ] Respeta una petición de parar.
- [ ] No infantiliza.
- [ ] No inventa visión ni memoria.
- [ ] Los movimientos suaves se muestran en MuJoCo.
- [ ] No se ha modificado el código oficial.

---

## 21. Problemas frecuentes

### El perfil no aparece en la interfaz

Comprobar:

```powershell
Test-Path .\external_content\external_profiles\ahootsa\instructions.txt
Get-Content .\.env
```

La variable debe apuntar exactamente a:

```env
REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY=./external_content/external_profiles
```

Reiniciar la aplicación.

### Error: perfil externo no encontrado

Comprobar el nombre:

```env
REACHY_MINI_CUSTOM_PROFILE=ahootsa
```

La carpeta debe llamarse exactamente:

```text
ahootsa
```

### Se carga el perfil `default`

Puede existir una selección persistida en `startup_settings.json`.

Seleccionar Ahootsa desde la interfaz, aplicarlo y guardarlo como perfil de inicio.

### Se cargan herramientas no deseadas

Comprobar que no existe:

```env
AUTOLOAD_EXTERNAL_TOOLS=1
```

Comprobar `tools.txt`.

### Error con `starter_custom_tool`

Eliminar `starter_custom_tool` del `tools.txt` de Ahootsa. Esa herramienta pertenece al ejemplo oficial.

### Los cambios en `instructions.txt` no se aplican

La aplicación no recarga automáticamente los archivos editados mientras el perfil ya está activo.

Después de editar:

1. volver a seleccionar el perfil;
2. o reiniciar la aplicación.

---

## 22. Archivos de esta fase

### Creados

```text
.env
external_content\external_profiles\ahootsa\instructions.txt
external_content\external_profiles\ahootsa\tools.txt
```

### No creados todavía

```text
external_content\external_profiles\ahootsa\greeting.txt
external_content\external_profiles\ahootsa\voice.txt
external_content\external_tools\*.py
```

### No modificados

```text
src\
profiles\
starter_profile\
starter_custom_tool.py
installed_tool_spaces.json
```

---

## 23. Referencias de la aplicación oficial

La aplicación define:

- `instructions.txt` como archivo principal de instrucciones;
- `greeting.txt` como saludo opcional;
- `tools.txt` como lista de herramientas permitidas;
- `voice.txt` como voz opcional;
- `REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY` como raíz de perfiles externos;
- `REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY` como raíz de herramientas externas;
- `AUTOLOAD_EXTERNAL_TOOLS=1` como modo de carga automática;
- `startup_settings.json` como persistencia de la selección realizada desde la interfaz.

En modo estricto, cada herramienta activa debe aparecer expresamente en `tools.txt`.

---

## 24. Mejoras incorporadas en la revisión 1.3

- Se incorporó una referencia directa a Swagger y OpenAPI.
- Se corrigió la numeración final de apartados.

Esta revisión incorpora del borrador anterior los aspectos operativos que mejoraban el procedimiento:

- detener solo la aplicación y conservar el daemon y MuJoCo;
- comandos directos para abrir manualmente los archivos;
- comprobaciones explícitas de la carpeta, `.env`, API y herramientas;
- validación de que la aplicación y MuJoCo continúan funcionando.

No se incorporan `greeting.txt`, `voice.txt` ni la exigencia de la voz `Serena`, porque corresponden a la Fase 2 y la disponibilidad de las voces depende del backend.

---

## 25. Siguiente fase

Una vez validado el comportamiento del perfil externo:

```text
Fase 2
└── configuración de personalidad, idioma y voz
```

En esa fase se incorporarán y comprobarán:

- `greeting.txt`;
- `voice.txt`;
- voces disponibles;
- saludo de inicio;
- ritmo y estilo definitivo;
- ajustes adicionales del español.

No debe avanzarse a la Fase 2 mientras Ahootsa no aparezca correctamente como perfil externo y no supere las pruebas de comunicación de esta fase.
