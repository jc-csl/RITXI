# Configuración de AHOOTSA8

**Versión documentada:** 0.12.8.6  
**Revisión:** 5 de agosto de 2026

## 1. Regla principal

La aplicación oficial incluida en el proyecto es el motor principal de
conversación. La personalización de Ahootsa se realiza fuera de `src`.

No modificar para personalizaciones normales:

```text
reachy_mini_conversation_app\src
```

Capas propias de Ahootsa:

```text
reachy_mini_conversation_app\external_content
ahootsa_local_server
scripts
```

## 2. Respuesta directa: qué ocurre al crear una persona y una sesión

Hay que distinguir dos acciones diferentes:

### 2.1. Crear una persona nueva

Al pulsar `Nuevo` y guardar una persona en el panel:

- se crea la persona en la base de datos SQLite;
- se crea o actualiza su perfil comunicativo;
- se guardan nombre, nombre preferido, idioma, intereses, temas que evitar,
  apoyos, velocidad de habla y demás campos;
- **todavía no se modifica ningún perfil externo de la Conversation App**;
- no se crea aún un `ahootsa_session` específico para esa persona.

Los datos quedan principalmente en:

```text
D:\RITXI\AHOOTSA8\ahootsa_local_server\data\ahootsa.db
```

### 2.2. Pulsar `Preparar`

Aquí sí se prepara el perfil temporal de la sesión:

```text
external_content\external_profiles\ahootsa_session
```

No se crea una carpeta distinta por cada persona. La misma carpeta
`ahootsa_session` se reutiliza secuencialmente para todas las sesiones.

El proceso es:

```text
ahootsa_default
      │ copia completa
      ▼
ahootsa_session
      │
      ├── añade contexto temporal a instructions.txt
      ├── genera greeting.txt con el nombre preferido
      ├── conserva tools.txt procedente de la plantilla
      └── conserva voice.txt procedente de la plantilla
```

Por tanto, la respuesta exacta es:

> Al crear la persona no se modifica `ahootsa_session`. Se modifica al pulsar
> `Preparar` para una sesión. En ese momento se reemplaza desde la plantilla
> `ahootsa_default` y después se personalizan `instructions.txt` y
> `greeting.txt` para esa sesión concreta.

## 3. Perfiles utilizados

### 3.1. Perfil general `ahootsa`

Ruta:

```text
reachy_mini_conversation_app\external_content\external_profiles\ahootsa
```

Uso:

```text
INICIAR_AHOOTSA_ANONIMO.ps1
```

Características:

- conversación sin identificar a una persona;
- no utiliza el servidor local para preparar contexto;
- no recibe nombre, intereses o actividad seleccionada desde el panel;
- no genera una carpeta de sesión ni un informe personal;
- no se reemplaza al crear o preparar sesiones identificadas.

Archivos cargados:

| Archivo | Función en modo anónimo |
|---|---|
| `instructions.txt` | Identidad de Aocha, comunicación accesible, seguridad, herramientas y reglas generales. |
| `greeting.txt` | Saludo general sin nombre de persona. |
| `tools.txt` | Selecciona las herramientas que puede cargar el perfil. |
| `voice.txt` | Selecciona la voz Sohee. |

### 3.2. Plantilla `ahootsa_default`

Ruta:

```text
reachy_mini_conversation_app\external_content\profile_defaults\ahootsa_default
```

No es el perfil que se lanza directamente. Es la plantilla limpia utilizada
para construir y restablecer `ahootsa_session`.

Contiene:

```text
instructions.txt
greeting.txt
tools.txt
voice.txt
```

Debe contener todas las reglas permanentes que también necesite una sesión
identificada:

- identidad y nombre hablado de Aocha;
- español estándar, claro y neutral;
- lenguaje adulto y accesible;
- seguridad y límites;
- instrucciones generales sobre herramientas;
- catálogo y reglas permanentes de `Vamos a bailar`;
- lista de herramientas habilitadas;
- voz Sohee.

Modificar solo `ahootsa_session` manualmente no es suficiente: al preparar la
siguiente sesión será sustituido de nuevo por esta plantilla.

### 3.3. Perfil activo de sesión `ahootsa_session`

Ruta:

```text
reachy_mini_conversation_app\external_content\external_profiles\ahootsa_session
```

Uso:

```text
INICIAR_AHOOTSA_SESION.ps1
→ panel
→ Preparar
→ Iniciar conversación
```

Es un perfil temporal y reutilizable, no un perfil permanente por usuario.

Su contenido procede de:

```text
plantilla ahootsa_default
+ datos de la persona
+ actividad seleccionada
+ nivel seleccionado
+ datos de la sesión
```

### 3.4. `starter_profile`

Ruta:

```text
external_content\external_profiles\starter_profile
```

Es un perfil de ejemplo de la aplicación y no forma parte del flujo operativo
de Ahootsa.

## 4. Qué modifica exactamente el botón `Preparar`

El servicio de preparación realiza estas operaciones en orden:

1. Comprueba que la Conversation App está cerrada.
2. Comprueba que no existe otra sesión activa.
3. Lee la persona y su perfil comunicativo desde SQLite.
4. Lee la actividad y el nivel elegidos en el panel.
5. Crea un registro de sesión en la base de datos.
6. Elimina el contenido anterior de `ahootsa_session`.
7. Copia los cuatro archivos de `ahootsa_default` a `ahootsa_session`.
8. Añade un bloque temporal al final de `ahootsa_session\instructions.txt`.
9. Reescribe `ahootsa_session\greeting.txt` para la sesión.
10. Copia una fotografía del perfil preparado a `profile_snapshot`.
11. Crea `session_context.json`, `session_status.json` y
    `active_session.json`.

### 4.1. Contenido añadido a `instructions.txt`

El bloque temporal incluye:

```text
identificador de sesión
nombre preferido
idioma
estilo comunicativo
velocidad de habla
segundos de espera
máximo de instrucciones por turno
intereses
temas que evitar
apoyos y accesibilidad
actividad
nivel
objetivo
máximo de opciones
reglas de la actividad
primera propuesta de conversación
límites de evaluación profesional
```

Ejemplo conceptual:

```text
# CONTEXTO TEMPORAL DE SESIÓN — PRIORIDAD ALTA
Este bloque solo se aplica a la sesión 25.

PERSONA USUARIA
- Nombre preferido: Ana
- Intereses conocidos: música y pasear
- Temas que evitar: no constan

ACTIVIDAD ACTUAL
- Actividad: Expresar preferencias
- Nivel: Inicial
- Objetivo: elegir entre opciones sencillas
```

Este bloque no debe convertirse en información permanente del perfil general.

### 4.2. Contenido generado en `greeting.txt`

Desde la versión 0.12.8.6, el saludo se genera de forma distinta según haya o
no intereses registrados en el perfil de la persona.

#### Persona con intereses registrados

Si el campo `interests` tiene contenido, el saludo:

- utiliza el nombre preferido;
- menciona los intereses guardados;
- ofrece hablar de ellos;
- ofrece como alternativa comenzar la actividad seleccionada.

Ejemplo conceptual:

```text
Hola, Ana. Soy Aocha. Entre las cosas que te gustan tengo anotado:
música y pasear. ¿Te apetece hablar de eso o prefieres empezar con
expresar preferencias?
```

#### Persona sin intereses registrados

Si `interests` está vacío, se utiliza el `greeting_template` del nivel de la
actividad, sustituyendo `{preferred_name}` por el nombre preferido.

Ejemplo:

```text
Hola, Ana. Soy Aocha. Vamos a elegir algo que te guste.
¿Qué prefieres: música o un cuento?
```

#### El archivo contiene una orden literal

`greeting.txt` no guarda únicamente la frase. Guarda una instrucción de alta
prioridad parecida a esta:

```text
PRIMER TURNO OBLIGATORIO DE ESTA SESIÓN.

Di literalmente y completa la frase situada entre comillas.
No la resumas, no cambies las palabras y no omitas el nombre.

«Hola, Ana. Soy Aocha. ...»

Después de decirla, espera la respuesta de la persona.
```

Esta forma evita que el modelo reduzca el saludo a la primera pregunta de la
actividad. La frase real utilizada también queda registrada en
`session_context.json` y en el evento `session_greeting`.

Si Aocha no conoce el nombre o no menciona los intereses, deben comprobarse:

```text
ahootsa_session\instructions.txt
ahootsa_session\greeting.txt
session_context.json
REACHY_MINI_CUSTOM_PROFILE=ahootsa_session
```

### 4.3. Qué ocurre con `tools.txt`

`tools.txt` no se personaliza con el nombre del usuario. Se copia desde
`ahootsa_default` y selecciona las herramientas disponibles en esa sesión.

Configuración funcional actual:

```text
move_head
idle_do_nothing
remember
forget
go_to_sleep
ahootsa_dances
```

Las líneas comentadas con `#` no están habilitadas por ese perfil.

### 4.4. Qué ocurre con `voice.txt`

`voice.txt` tampoco se genera con datos personales. Se copia desde
`ahootsa_default`.

Configuración esperada desde la versión 0.12.8.6:

```text
Sohee
```

## 5. Qué ocurre al pulsar `Iniciar conversación`

El panel ejecuta:

```text
scripts\iniciar_conversation_sesion.ps1
```

El lanzador selecciona:

```text
REACHY_MINI_CUSTOM_PROFILE=ahootsa_session
```

La Conversation App carga entonces desde `ahootsa_session`:

```text
instructions.txt
greeting.txt
tools.txt
voice.txt
```

El contexto no se envía mediante un segundo sistema de conversación: queda
integrado en los archivos del perfil externo que carga la aplicación oficial.

## 6. Qué ocurre al finalizar la sesión

Al finalizar:

1. se cierra la Conversation App;
2. se importa el log y se generan los informes;
3. se guarda el resultado en la carpeta de la sesión;
4. `ahootsa_session` se restablece copiando nuevamente `ahootsa_default`;
5. se elimina `active_session.json`;
6. la información temporal de la persona deja de permanecer en el perfil
   activo reutilizable.

La copia exacta utilizada durante la sesión se conserva en:

```text
ahootsa_local_server\data\sessions\session_XXXXXX\profile_snapshot
```

La información personal y la historia de la sesión permanecen en SQLite y en
la carpeta de esa sesión, no en el perfil general `ahootsa`.

## 7. Diferencia entre perfiles, herramientas y actividades

Son tres conceptos distintos.

### 7.1. Perfil

Un perfil es la combinación de:

```text
instructions.txt
greeting.txt
tools.txt
voice.txt
```

Determina cómo habla Aocha, cómo saluda, qué herramientas puede utilizar y qué
voz selecciona.

### 7.2. Herramientas externas

Directorio compartido:

```text
external_content\external_tools
```

Herramienta propia principal:

```text
ahootsa_dances.py
```

El hecho de que el archivo Python exista no significa que esté activo. El
perfil debe incluir su nombre de herramienta en `tools.txt`.

Con:

```env
AUTOLOAD_EXTERNAL_TOOLS=false
```

la selección explícita del perfil es especialmente importante.

### 7.3. Actividades del panel profesional

Directorio:

```text
ahootsa_local_server\config\activities\*.json
```

Estas actividades definen para cada nivel:

```text
título
objetivo
reglas
máximo de opciones
primera propuesta
greeting_template
```

Al pulsar `Preparar`, la actividad seleccionada no se copia como archivo dentro
del perfil. Sus datos se transforman en:

- el bloque temporal de `instructions.txt`;
- el saludo de `greeting.txt`;
- el contexto JSON de la sesión.

### 7.4. Recursos locales de `Vamos a bailar`

Directorio compartido:

```text
external_content\activities\vamos_a_bailar
```

Contiene catálogo, movimientos y audio local. Lo utiliza:

```text
external_tools\ahootsa_dances.py
```

Esta carpeta:

- no se copia a `ahootsa_session`;
- no se duplica por usuario;
- puede ser utilizada en modo anónimo o sesión cuando `ahootsa_dances` está
  habilitada en `tools.txt`;
- es distinta de las actividades pedagógicas configuradas en el servidor
  local.

#### Finalización automática desde 0.12.8.6

`play_ahootsa_dance` permanece ejecutándose hasta que termina el audio o el
movimiento de mayor duración. Al finalizar:

1. detiene y limpia automáticamente la cola de movimiento;
2. limpia la salida musical sin detener el micrófono;
3. devuelve `status: completed` al sistema de conversación;
4. solicita una respuesta hablada breve;
5. Aocha confirma que el baile ha terminado y formula una sola pregunta para
   continuar.

Ejemplo de continuación:

```text
Ya hemos terminado el baile. ¿Te ha gustado?
```

No debe ser necesario que la persona vuelva a hablar para que Aocha reactive
la conversación. Si otro baile sustituye al anterior, el baile anterior no
produce una frase que interrumpa el nuevo.

## 8. Tabla comparativa completa

| Elemento | Modo anónimo | Sesión identificada |
|---|---|---|
| Perfil cargado | `external_profiles\ahootsa` | `external_profiles\ahootsa_session` |
| Plantilla usada | No | `profile_defaults\ahootsa_default` |
| Persona identificada | No | Sí, desde SQLite |
| `instructions.txt` | Reglas generales permanentes y continuación tras bailes | Reglas de la plantilla + contexto temporal + saludo obligatorio |
| `greeting.txt` | Saludo general | Orden literal con nombre y, si existen, intereses registrados |
| `tools.txt` | El del perfil `ahootsa` | Copiado desde `ahootsa_default` |
| `voice.txt` | Sohee | Sohee copiada desde `ahootsa_default` |
| Actividad del panel | No se selecciona | Se inyecta actividad y nivel |
| `vamos_a_bailar` | Disponible si la herramienta está habilitada | Disponible si la herramienta está habilitada |
| Carpeta de sesión | No | `data\sessions\session_XXXXXX` |
| `profile_snapshot` | No | Sí |
| Informe personal | No | Sí |

## 9. Archivos que deben editarse según el objetivo

### Cambiar el comportamiento general anónimo

Editar:

```text
external_profiles\ahootsa\instructions.txt
external_profiles\ahootsa\greeting.txt
external_profiles\ahootsa\tools.txt
external_profiles\ahootsa\voice.txt
```

### Cambiar el comportamiento base de todas las sesiones futuras

Editar:

```text
profile_defaults\ahootsa_default\instructions.txt
profile_defaults\ahootsa_default\greeting.txt
profile_defaults\ahootsa_default\tools.txt
profile_defaults\ahootsa_default\voice.txt
```

Después debe prepararse una nueva sesión para que se regenere
`ahootsa_session`.

### Corregir únicamente una sesión ya preparada

Puede revisarse temporalmente:

```text
external_profiles\ahootsa_session
```

Pero esos cambios se perderán al preparar o finalizar otra sesión. Para un
cambio permanente también debe modificarse `ahootsa_default`.

### Cambiar una actividad o un nivel del panel

Editar:

```text
ahootsa_local_server\config\activities\*.json
```

### Cambiar la ejecución de los bailes

Editar, según el caso:

```text
external_tools\ahootsa_dances.py
external_content\activities\vamos_a_bailar\catalogo_bailes.json
external_content\activities\vamos_a_bailar\dataset\data
```

## 10. Resumen del ciclo completo de una persona y una sesión

```text
NUEVO + GUARDAR PERSONA
    │
    ├── escribe datos en SQLite
    └── NO modifica perfiles externos

PREPARAR
    │
    ├── copia ahootsa_default → ahootsa_session
    ├── añade datos temporales a instructions.txt
    ├── genera greeting.txt con nombre
    ├── añade intereses al saludo cuando existen
    ├── conserva tools.txt
    ├── conserva voice.txt = Sohee
    └── guarda profile_snapshot

INICIAR CONVERSACIÓN
    │
    └── carga ahootsa_session

FINALIZAR
    │
    ├── guarda log e informes
    ├── elimina el contexto activo
    └── restaura ahootsa_session desde ahootsa_default
```

## 11. Archivo `.env` de la aplicación

Ruta:

```text
D:\RITXI\AHOOTSA8\reachy_mini_conversation_app\.env
```

Configuración principal:

```env
REALTIME_TRANSCRIPTION_LANGUAGE="es"
HF_REALTIME_CONNECTION_MODE="deployed"
HF_TOKEN=
REACHY_MINI_CUSTOM_PROFILE=ahootsa
REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY=./external_content/external_profiles
REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY=./external_content/external_tools
AUTOLOAD_EXTERNAL_TOOLS=false
```

Los scripts seleccionan temporalmente `ahootsa_session` para una sesión
identificada y restauran `ahootsa` al finalizar.

## 12. Configuración del servidor local

Archivo:

```text
ahootsa_local_server\config\panel_config.json
```

Relaciones principales:

```text
base_profile_directory             external_profiles\ahootsa
profile_template_directory         profile_defaults\ahootsa_default
active_session_profile_directory   external_profiles\ahootsa_session
external_tools_directory           external_tools
session_data_directory             data\sessions
active_session_file                data\active_session.json
active_profile_name                ahootsa_session
```

## 13. Base de datos y archivos de sesión

Base de datos:

```text
ahootsa_local_server\data\ahootsa.db
```

Carpeta de una sesión:

```text
ahootsa_local_server\data\sessions\session_XXXXXX
```

Archivos relevantes:

```text
session_context.json
session_status.json
conversation_app.log
profile_snapshot\
summary.json
informe_sesion.pdf
informe_sesion.html
informe_sesion.json
transcripcion_sesion.txt
```

## 14. Puertos y direcciones

| Componente | Puerto | Dirección |
|---|---:|---|
| Reachy Mini daemon | 8000 | `http://127.0.0.1:8000/docs` |
| Ahootsa Local Server | 8100 | `http://127.0.0.1:8100/docs` |
| Panel profesional | 8100 | `http://127.0.0.1:8100/panel-12-8-5` |
| Conversation App | 7860 | `http://127.0.0.1:7860` |

## 15. Comprobación práctica de una sesión preparada

Después de pulsar `Preparar`:

```powershell
$activo = Get-Content `
    D:\RITXI\AHOOTSA8\ahootsa_local_server\data\active_session.json `
    -Raw |
    ConvertFrom-Json

Get-Content $activo.context_file -Raw

Get-Content `
    D:\RITXI\AHOOTSA8\reachy_mini_conversation_app\external_content\external_profiles\ahootsa_session\greeting.txt `
    -Raw

Select-String `
    D:\RITXI\AHOOTSA8\reachy_mini_conversation_app\external_content\external_profiles\ahootsa_session\instructions.txt `
    -Pattern "Nombre preferido|Actividad:|Nivel:|Intereses conocidos"
```

La salida debe mostrar la persona, la actividad y el nivel seleccionados.

## Fuentes técnicas verificadas

Documentación revisada el 5 de agosto de 2026:

- `ahootsa_local_server/app/session_preparation_service.py`
- `ahootsa_local_server/config/panel_config.json`
- `external_profiles/ahootsa`
- `external_profiles/ahootsa_session`
- `profile_defaults/ahootsa_default`
- `external_tools/ahootsa_dances.py`
- `external_content/activities/vamos_a_bailar`
- Repositorio: https://github.com/jc-csl/RITXI

La voz Sohee y la ruta `panel-12-8-5` corresponden a la actualización local
0.12.8.6/12.8.5.1. Si esos cambios todavía no se han incorporado al repositorio,
deben aplicarse antes en el PC nuevo.
