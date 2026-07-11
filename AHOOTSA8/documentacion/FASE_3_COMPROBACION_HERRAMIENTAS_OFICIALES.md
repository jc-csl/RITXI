# Ahootsa 8 — Fase 3
## Comprobación paso a paso de las herramientas oficiales

**Documento:** Fase 3  
**Proyecto:** Ahootsa 8  
**Requisito previo:** Fases 0, 1 y 2 completadas  
**Aplicación:** `reachy_mini_conversation_app 0.9.0`  
**SDK:** `reachy-mini 1.9.0`  
**Entorno de prueba:** daemon manual + simulación MuJoCo visible  
**Objetivo:** validar las herramientas oficiales antes de añadir funciones propias de Ahootsa

---

## 1. Objetivo de la fase

Esta fase comprueba las herramientas incluidas en la aplicación oficial y decide cuáles deben permanecer habilitadas para Ahootsa.

La comprobación se realiza:

- sin modificar el código Python oficial;
- editando únicamente `tools.txt`;
- manteniendo el perfil externo `ahootsa`;
- activando herramientas por grupos;
- revisando la respuesta, los logs y MuJoCo;
- registrando las limitaciones de la simulación;
- dejando `go_to_sleep` para la última prueba.

Resultado previsto:

```text
Fase 3
├── inventario real de herramientas
├── comprobación de carga
├── move_head
├── play_emotion / stop_emotion
├── idle_do_nothing
├── dance / stop_dance
├── camera
├── head_tracking
├── remember / forget
├── task_status / task_cancel
├── sweep_look del perfil oficial default
├── go_to_sleep
└── tools.txt final de Ahootsa
```

---

## 2. Herramientas oficiales identificadas

### 2.1. Herramientas principales documentadas por la aplicación

```text
move_head
head_tracking
camera
dance
stop_dance
play_emotion
stop_emotion
remember
forget
go_to_sleep
idle_do_nothing
```

### 2.2. Herramienta local del perfil oficial `default`

```text
sweep_look
```

Esta herramienta no se encuentra en el directorio compartido:

```text
src\reachy_mini_conversation_app\tools\
```

Está implementada en:

```text
profiles\default\sweep_look.py
```

Por eso funciona con el perfil interno `default`, pero no debe añadirse directamente al `tools.txt` del perfil externo Ahootsa sin incorporar también su archivo Python.

En esta fase se prueba seleccionando temporalmente el perfil oficial `default`. No se copia todavía su código.

### 2.3. Herramientas internas de gestión de tareas

```text
task_status
task_cancel
```

La aplicación las añade automáticamente al registro interno.

No deben escribirse manualmente en:

```text
external_content\external_profiles\ahootsa\tools.txt
```

Su función es gestionar herramientas ejecutadas en segundo plano.

---

## 3. Diferencia entre `tools.txt` y el registro real

`tools.txt` es la lista de herramientas elegidas para el perfil:

```text
external_content\external_profiles\ahootsa\tools.txt
```

La aplicación añade además automáticamente:

```text
task_status
task_cancel
```

Por tanto, pueden existir dos listas diferentes:

```text
enabled_tools
└── contenido explícito de tools.txt

registro interno
├── contenido de tools.txt
├── task_status
└── task_cancel
```

### Comprobar el contenido declarado por el perfil

Con la aplicación abierta:

```powershell
$perfil = Invoke-RestMethod `
    "http://127.0.0.1:7860/api/v1/personalities/load?name=ahootsa"

$perfil.enabled_tools
```

### Comprobar el registro real de herramientas

Desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe -c "import reachy_mini_conversation_app.tools.core_tools as c; c.initialize_tools(force=True); print('\n'.join(sorted(c.ALL_TOOLS)))"
```

El resultado debe incluir también:

```text
task_cancel
task_status
```

### Mostrar descripciones y parámetros de todas las herramientas cargadas

```powershell
.\.venv\Scripts\python.exe -c "import json; import reachy_mini_conversation_app.tools.core_tools as c; c.initialize_tools(force=True); print(json.dumps([t.spec() for t in c.ALL_TOOLS.values()], ensure_ascii=False, indent=2))"
```

Este comando es la comprobación más precisa de:

- nombre;
- descripción;
- parámetros;
- valores admitidos.

---

## 4. FastAPI durante la Fase 3

### Aplicación de conversación

```text
Interfaz:
http://127.0.0.1:7860/

Swagger:
http://127.0.0.1:7860/docs

ReDoc:
http://127.0.0.1:7860/redoc

OpenAPI:
http://127.0.0.1:7860/openapi.json
```

### Daemon

```text
Swagger:
http://127.0.0.1:8000/docs

ReDoc:
http://127.0.0.1:8000/redoc

OpenAPI:
http://127.0.0.1:8000/openapi.json
```

Las herramientas del modelo no aparecen necesariamente como endpoints independientes. Se cargan en el backend conversacional y se invocan mediante llamadas de herramienta del modelo.

Swagger se utiliza para comprobar:

- perfil activo;
- herramientas declaradas;
- voces;
- micrófono;
- estado;
- configuración disponible.

---

## 5. Reglas de seguridad para las pruebas

### Orden obligatorio

```text
1. movimiento
2. emociones
3. inactividad
4. bailes
5. cámara
6. seguimiento
7. memoria
8. herramientas de sistema
9. sweep_look
10. go_to_sleep
```

`go_to_sleep` se prueba al final porque detiene la aplicación.

### Datos de memoria

Utilizar únicamente un dato ficticio y no sensible:

```text
Mi color favorito para esta prueba es el verde.
```

No utilizar:

- direcciones;
- contraseñas;
- información médica;
- números de identificación;
- datos económicos;
- información real de personas usuarias.

### Cámara

Pedir permiso antes de capturar una imagen.

En simulación debe comprobarse qué fuente visual recibe realmente la aplicación. No se debe asumir que utiliza la webcam del ordenador.

### Movimiento

Mantener la escena MuJoCo visible y comprobar:

- dirección;
- amplitud;
- finalización;
- parada;
- retorno a una postura razonable.

---

## 6. Añadir reglas de herramientas a `instructions.txt`

Antes de habilitar todas las herramientas, añadir al final de:

```text
external_content\external_profiles\ahootsa\instructions.txt
```

este bloque:

```text
USO DE HERRAMIENTAS

Utiliza una herramienta cuando la persona la pida expresamente o cuando sea necesaria para responder correctamente.

Durante las pruebas, si la persona pide de forma clara una herramienta disponible, utiliza esa herramienta y no finjas haberla utilizado.

No digas que una herramienta ha funcionado hasta recibir su resultado.

Antes de hacer un baile, pregunta si la persona quiere verlo.

Si la persona pide parar un baile, una emoción o un seguimiento, detenlo inmediatamente.

Antes de utilizar la cámara, pide permiso.

Utiliza la memoria únicamente cuando la persona pida expresamente recordar un dato estable y no sensible.

No guardes información médica, contraseñas, direcciones, datos económicos ni información privada sensible.

Si la persona pide olvidar un dato, utiliza la herramienta de olvido.

Utiliza go_to_sleep únicamente ante una petición clara de dormir, cerrar o terminar la aplicación.

No confundas una emoción de sueño con la orden de cerrar la aplicación.
```

### Comprobar que el bloque está presente

```powershell
Get-Content `
    .\external_content\external_profiles\ahootsa\instructions.txt |
    Select-String "USO DE HERRAMIENTAS|Antes de utilizar la cámara|go_to_sleep"
```

Después de modificar `instructions.txt`, reiniciar la aplicación o volver a seleccionar el perfil.

---

## 7. Preparar una copia de seguridad de `tools.txt`

Detener únicamente la aplicación:

```text
Ctrl + C
```

Mantener abierto el daemon y MuJoCo.

Crear la carpeta de copias:

```powershell
New-Item `
    -ItemType Directory `
    -Path .\docs\copias_configuracion `
    -Force
```

Copiar el archivo de la Fase 2:

```powershell
Copy-Item `
    .\external_content\external_profiles\ahootsa\tools.txt `
    .\docs\copias_configuracion\ahootsa_tools_FASE2.txt `
    -Force
```

Comprobar:

```powershell
Get-Content .\docs\copias_configuracion\ahootsa_tools_FASE2.txt
```

---

## 8. Procedimiento común para cada grupo

Para cada grupo de herramientas:

1. Detener la aplicación con `Ctrl + C`.
2. Mantener el daemon y MuJoCo abiertos.
3. Sustituir el contenido de `ahootsa\tools.txt`.
4. Iniciar la aplicación.
5. Comprobar `enabled_tools`.
6. Realizar la petición oral.
7. Observar MuJoCo.
8. Revisar los logs de la terminal.
9. Anotar el resultado.
10. Continuar con el siguiente grupo.

### Arranque de la aplicación

```powershell
cd D:\ritxi\AHOOTSA8\reachy_mini_conversation_app
.\.venv\Scripts\Activate.ps1
reachy-mini-conversation-app --ui --debug
```

### Comprobación del perfil

```powershell
(Invoke-RestMethod `
    http://127.0.0.1:7860/api/v1/personalities).current
```

Debe devolver:

```text
ahootsa
```

### Comprobar herramientas declaradas

```powershell
$perfil = Invoke-RestMethod `
    "http://127.0.0.1:7860/api/v1/personalities/load?name=ahootsa"

$perfil.enabled_tools
```

### Logs

Durante cada prueba buscar mensajes con esta forma:

```text
Tool call:
Started background tool:
Background tool completed:
```

Varias herramientas tienen:

```text
needs_response = False
```

Por tanto, pueden ejecutar un movimiento sin producir una explicación hablada posterior. La ausencia de una frase no significa necesariamente que hayan fallado.

---

# BLOQUE A — MOVIMIENTO

## 9. Comprobar `move_head`

### 9.1. Contenido temporal de `tools.txt`

```text
move_head
```

Guardar:

```text
external_content\external_profiles\ahootsa\tools.txt
```

Reiniciar la aplicación.

### 9.2. Comprobar carga

```powershell
$perfil = Invoke-RestMethod `
    "http://127.0.0.1:7860/api/v1/personalities/load?name=ahootsa"

$perfil.enabled_tools
```

Resultado esperado:

```text
move_head
```

### 9.3. Direcciones oficiales

```text
left
right
up
down
front
```

### 9.4. Pruebas orales

Decir una frase, esperar a que finalice el movimiento y pasar a la siguiente.

```text
Mira a la izquierda.
```

```text
Mira a la derecha.
```

```text
Mira hacia arriba.
```

```text
Mira hacia abajo.
```

```text
Vuelve a mirar al frente.
```

### 9.5. Logs esperados

```text
Tool call: move_head direction=left
Tool call: move_head direction=right
Tool call: move_head direction=up
Tool call: move_head direction=down
Tool call: move_head direction=front
```

### 9.6. Comprobación en MuJoCo

- `left`: giro hacia la izquierda.
- `right`: giro hacia la derecha.
- `up`: inclinación hacia arriba.
- `down`: inclinación hacia abajo.
- `front`: retorno al frente.

### 9.7. Criterio de aceptación

- [ ] Las cinco direcciones se ejecutan.
- [ ] No aparecen errores.
- [ ] Los movimientos son suaves.
- [ ] `front` devuelve el robot a la orientación frontal.
- [ ] La herramienta no necesita una respuesta hablada posterior.

---

# BLOQUE B — EMOCIONES

## 10. Comprobar `play_emotion` y `stop_emotion`

### 10.1. Contenido temporal de `tools.txt`

```text
play_emotion
stop_emotion
```

Reiniciar la aplicación.

### 10.2. Consultar intenciones admitidas

```powershell
.\.venv\Scripts\python.exe -c "from reachy_mini_conversation_app.tools.play_emotion import EMOTION_INTENTS; print('\n'.join(EMOTION_INTENTS))"
```

Entre las intenciones disponibles aparecen:

```text
happy
excited
loving
grateful
success
thinking
attentive
confused
uncertain
sad
angry
scared
surprised
calming
relief
tired
sleepy
yes
no
welcoming
greeting
goodbye
helpful
random
```

La lista obtenida por el comando es la referencia válida para la versión instalada.

### 10.3. Primera ejecución

La primera llamada puede descargar el conjunto oficial de emociones.

Durante esa primera ejecución:

- mantener la conexión a Internet;
- esperar a que termine la descarga;
- no cerrar la aplicación;
- revisar la terminal.

### 10.4. Pruebas orales

```text
Muestra una emoción alegre.
```

```text
Muestra una emoción de calma.
```

```text
Haz un gesto de que sí y de que lo has entendido.
```

```text
Muestra sorpresa.
```

### 10.5. Logs esperados

Ejemplos:

```text
Tool call: play_emotion emotion=happy
Tool call: play_emotion emotion=calming
Tool call: play_emotion emotion=yes_understanding
Tool call: play_emotion emotion=surprised
```

El movimiento concreto puede tener un nombre interno como:

```text
laughing2
calming1
understanding2
surprised1
```

### 10.6. Comprobar `stop_emotion`

Iniciar una emoción:

```text
Muestra una emoción.
```

Antes de que termine o inmediatamente después, decir:

```text
Para la emoción.
```

Log esperado:

```text
Tool call: stop_emotion
Cleared move queue and stopped current move
```

### 10.7. Criterio de aceptación

- [ ] La biblioteca de emociones está disponible.
- [ ] Se ejecuta al menos una emoción positiva.
- [ ] Se ejecuta al menos una emoción calmada.
- [ ] Se ejecuta un gesto afirmativo.
- [ ] `stop_emotion` limpia la cola.
- [ ] No se mezcla una emoción con un baile no solicitado.

---

# BLOQUE C — INACTIVIDAD

## 11. Comprobar `idle_do_nothing`

Esta herramienta no está pensada para responder a una petición normal.

La política de inactividad de la aplicación se activa aproximadamente después de:

```text
180 segundos
```

Para realizar una prueba determinista, dejar únicamente esta herramienta activa.

### 11.1. Contenido temporal de `tools.txt`

```text
idle_do_nothing
```

Reiniciar la aplicación.

### 11.2. Preparar la prueba

1. Esperar a que termine el saludo.
2. Silenciar el micrófono desde la interfaz si es necesario.
3. No hablar.
4. No pulsar controles.
5. Esperar al menos 3 minutos y 10 segundos.

### 11.3. Logs esperados

```text
Started local idle tool after ... idle: idle_do_nothing
Tool call: idle_do_nothing reason=random idle policy selected stillness
```

### 11.4. Resultado esperado

- el robot permanece quieto;
- no responde verbalmente;
- no inicia un baile;
- no reproduce una emoción;
- la aplicación sigue activa.

### 11.5. Criterio de aceptación

- [ ] El temporizador de inactividad llega a ejecutarse.
- [ ] Se selecciona `idle_do_nothing`.
- [ ] No se produce movimiento.
- [ ] No se produce voz.
- [ ] La aplicación no se cierra.

---

# BLOQUE D — BAILES

## 12. Comprobar `dance` y `stop_dance`

### 12.1. Contenido temporal de `tools.txt`

```text
dance
stop_dance
```

Reiniciar la aplicación.

### 12.2. Comprobar que la biblioteca está instalada

```powershell
.\.venv\Scripts\python.exe -c "from reachy_mini_dances_library.collection.dance import AVAILABLE_MOVES; print('Cantidad:', len(AVAILABLE_MOVES)); print('\n'.join(AVAILABLE_MOVES.keys()))"
```

Debe devolver una cantidad superior a cero.

La lista obtenida es la referencia real. No es recomendable fijar manualmente nombres que puedan cambiar en otra versión.

### 12.3. Probar un baile aleatorio

```text
¿Quieres hacer un baile corto?
```

Después de que Ahootsa pida o reciba autorización:

```text
Sí, haz un baile una vez.
```

Log esperado:

```text
Tool call: dance move=... repeat=1
```

### 12.4. Probar un baile concreto

Elegir uno de los nombres obtenidos en el comando anterior.

Ejemplo:

```text
Haz el baile llamado NOMBRE una vez.
```

### 12.5. Probar repetición y parada

```text
Haz ese baile cinco veces.
```

Mientras se ejecuta:

```text
Para el baile.
```

Logs esperados:

```text
Tool call: dance move=... repeat=5
Tool call: stop_dance
Cleared move queue and stopped current move
```

### 12.6. Criterio de aceptación

- [ ] Existen bailes disponibles.
- [ ] Se ejecuta un baile aleatorio.
- [ ] Se ejecuta un baile por nombre.
- [ ] El parámetro de repetición se acepta.
- [ ] `stop_dance` detiene el movimiento actual.
- [ ] `stop_dance` vacía los movimientos pendientes.
- [ ] Ahootsa no inicia un baile sin permiso.

---

# BLOQUE E — CÁMARA

## 13. Comprobar `camera`

### 13.1. Condiciones necesarias

La aplicación debe iniciarse sin:

```text
--no-camera
```

Comando correcto:

```powershell
reachy-mini-conversation-app --ui --debug
```

Contenido temporal de `tools.txt`:

```text
camera
```

Reiniciar la aplicación.

### 13.2. Comprobar que la herramienta está declarada

```powershell
$perfil = Invoke-RestMethod `
    "http://127.0.0.1:7860/api/v1/personalities/load?name=ahootsa"

$perfil.enabled_tools
```

Debe devolver:

```text
camera
```

### 13.3. Primera petición

```text
¿Puedes usar la cámara?
```

Ahootsa debe pedir permiso o confirmar la intención.

Después:

```text
Sí. Haz una foto y dime qué ves.
```

### 13.4. Log esperado

```text
Tool call: camera question=...
```

Si hay imagen disponible, el backend recibe una imagen JPEG codificada y debe describirla.

### 13.5. Comprobación del origen visual

En simulación:

1. mover o cambiar la escena de MuJoCo;
2. colocar objetos visibles en la escena `minimal`;
3. repetir la consulta;
4. comprobar si la descripción coincide con la cámara virtual.

No asumir que la herramienta utiliza la webcam del ordenador.

### 13.6. Errores posibles

```text
Camera is disabled
```

La aplicación se inició con `--no-camera`.

```text
No frame available
```

El daemon no está entregando una imagen.

```text
camera: empty question
```

La llamada no incluía una pregunta válida.

### 13.7. Comprobaciones adicionales

Abrir:

```text
http://127.0.0.1:8000/docs
```

Revisar los endpoints multimedia y de cámara que exponga la versión del daemon.

No utilizar nombres de endpoints memorizados; consultar Swagger porque pueden variar.

### 13.8. Criterio de aceptación

- [ ] La aplicación se inicia con cámara habilitada.
- [ ] La herramienta recibe una pregunta.
- [ ] Existe un fotograma.
- [ ] El backend describe una imagen real.
- [ ] No inventa elementos que no aparecen.
- [ ] Se ha identificado la fuente visual utilizada.
- [ ] Ahootsa pide permiso antes de capturar.

---

# BLOQUE F — SEGUIMIENTO DE CABEZA

## 14. Comprobar `head_tracking`

### 14.1. Contenido temporal de `tools.txt`

```text
head_tracking
```

Reiniciar la aplicación sin `--no-camera`.

### 14.2. Activar

```text
Empieza a seguir mi cara con la cabeza.
```

Log esperado:

```text
Tool call: head_tracking enabled=True
```

### 14.3. Desactivar

```text
Deja de seguirme.
```

Log esperado:

```text
Tool call: head_tracking enabled=False
```

### 14.4. Advertencias que invalidan la prueba

Revisar la terminal. No debe aparecer:

```text
Head-tracking toggle failed
```

Tampoco errores relacionados con:

```text
mediapipe
vision
camera
tracked face
```

### 14.5. Limitación de MuJoCo

En simulación puede comprobarse:

- que la herramienta está cargada;
- que la llamada activa y desactiva el modo;
- que no se producen excepciones;
- que los logs son correctos.

El seguimiento físico real de la cara solo se considera completamente validado cuando existe:

- una fuente de cámara compatible;
- un rostro detectable;
- movimiento observable hacia la persona.

Si la cámara de simulación no muestra un rostro real, la prueba funcional completa se aplaza hasta disponer del robot físico o de una fuente de vídeo adecuada.

### 14.6. Dependencia opcional de visión

No instalar dependencias adicionales antes de observar un error real.

Si la versión instalada informa de que falta el componente de visión, revisar primero:

```text
http://127.0.0.1:8000/docs
```

y la ayuda del daemon:

```powershell
reachy-mini-daemon --help
```

La aplicación `0.9.0` depende de `reachy-mini-toolbox`, cuyo componente de visión puede requerir una instalación opcional. Esta instalación se debe documentar únicamente si el error aparece realmente.

### 14.7. Criterio de aceptación en simulación

- [ ] La herramienta se registra.
- [ ] La activación genera `enabled=True`.
- [ ] La desactivación genera `enabled=False`.
- [ ] No aparece `Head-tracking toggle failed`.
- [ ] La limitación de la fuente de vídeo está anotada.

### 14.8. Criterio pendiente para el robot físico

- [ ] Detecta una cara.
- [ ] Gira hacia la persona.
- [ ] Mantiene un seguimiento estable.
- [ ] Se detiene inmediatamente al pedirlo.
- [ ] No sigue a una persona sin permiso.

---

# BLOQUE G — MEMORIA

## 15. Comprobar `remember` y `forget`

### 15.1. Contenido temporal de `tools.txt`

```text
remember
forget
```

Reiniciar la aplicación.

### 15.2. Localizar el archivo de memoria real

```powershell
$rutaMemoria = .\.venv\Scripts\python.exe -c "from reachy_mini_conversation_app.memory import memory_path_for_instance; print(memory_path_for_instance())"

$rutaMemoria
```

En el arranque manual, normalmente se encuentra bajo el directorio personal del usuario, dentro de:

```text
.local\share\reachy_mini_conversation_app\memory.v1.json
```

El comando anterior es la referencia válida.

C:\Users\Alumno\.local\share\reachy_mini_conversation_app\memory.v1.json

### 15.3. Proteger memorias existentes

```powershell
if (Test-Path $rutaMemoria) {
    Copy-Item `
        $rutaMemoria `
        "$rutaMemoria.FASE3.bak" `
        -Force
}
```

### 15.4. Guardar un dato ficticio

Decir:

```text
Recuerda que mi color favorito para esta prueba es el verde.
```

Log esperado:

```text
Tool call: remember fact=...
```

### 15.5. Comprobar el archivo

```powershell
Test-Path $rutaMemoria
```

Debe devolver:

```text
True
```

Mostrarlo:

```powershell
Get-Content $rutaMemoria -Raw |
    ConvertFrom-Json |
    ConvertTo-Json -Depth 6
```

Debe aparecer un hecho relacionado con:

```text
color favorito
verde
```

### 15.6. Comprobar persistencia

1. Detener la aplicación.
2. Reiniciarla.
3. Preguntar:

```text
¿Qué color favorito recuerdas de mí?
```

La respuesta debe utilizar el dato guardado de forma natural.

No debe leer toda la memoria ni revelar identificadores internos.

### 15.7. Olvidar el dato

Decir:

```text
Olvida que mi color favorito para la prueba es el verde.
```

Log esperado:

```text
Tool call: forget query=...
```

Comprobar de nuevo:

```powershell
Get-Content $rutaMemoria -Raw |
    ConvertFrom-Json |
    ConvertTo-Json -Depth 6
```

El dato de prueba ya no debe aparecer.

### 15.8. Comprobar una búsqueda inexistente

```text
Olvida que tengo un elefante azul.
```

La herramienta debe indicar que no existe coincidencia y no eliminar otro dato.

### 15.9. Restaurar el archivo original

Si existía una copia:

```powershell
if (Test-Path "$rutaMemoria.FASE3.bak") {
    Copy-Item `
        "$rutaMemoria.FASE3.bak" `
        $rutaMemoria `
        -Force

    Remove-Item "$rutaMemoria.FASE3.bak"
}
```

Si no existía memoria previa y el archivo de prueba ha quedado vacío, se puede eliminar:

```powershell
if (
    -not (Test-Path "$rutaMemoria.FASE3.bak") -and
    (Test-Path $rutaMemoria)
) {
    $memoria = Get-Content $rutaMemoria -Raw | ConvertFrom-Json
    if (@($memoria.facts).Count -eq 0) {
        Remove-Item $rutaMemoria
    }
}
```

### 15.10. Criterio de aceptación

- [ ] `remember` crea o actualiza `memory.v1.json`.
- [ ] Se guarda un único hecho breve.
- [ ] La memoria persiste al reiniciar.
- [ ] `forget` elimina el hecho correcto.
- [ ] Una búsqueda inexistente no elimina otro dato.
- [ ] No se han usado datos sensibles.
- [ ] Se ha restaurado la memoria previa.

---

# BLOQUE H — HERRAMIENTAS DE SISTEMA

## 16. Comprobar `task_status` y `task_cancel`

### 16.1. No añadirlas a `tools.txt`

Estas herramientas se agregan automáticamente.

Comprobar:

```powershell
.\.venv\Scripts\python.exe -c "import reachy_mini_conversation_app.tools.core_tools as c; c.initialize_tools(force=True); print('task_status' in c.ALL_TOOLS); print('task_cancel' in c.ALL_TOOLS)"
```

Resultado esperado:

```text
True
True
```

### 16.2. Comprobar `task_status`

Con la aplicación abierta, decir:

```text
¿Hay alguna herramienta ejecutándose ahora en segundo plano?
```

El modelo puede utilizar:

```text
task_status
```

Cuando no hay ninguna herramienta activa, el resultado interno debe indicar:

```text
status: idle
No tools running in the background.
```

Log esperado:

```text
Tool call: tool_status tool_id=None
```

### 16.3. Limitación de `task_cancel`

Las herramientas oficiales comprobadas en esta fase suelen terminar rápidamente.

Además:

- `dance` devuelve inmediatamente después de poner movimientos en cola;
- `stop_dance` es la herramienta correcta para detener bailes;
- `stop_emotion` es la herramienta correcta para detener emociones.

Por eso no debe utilizarse `task_cancel` para detener un baile o una emoción.

La validación completa de `task_cancel` se aplaza hasta la Fase 4, cuando exista una herramienta externa de larga duración que entregue un `tool_id` activo.

### 16.4. Criterio de aceptación

- [ ] `task_status` está registrado automáticamente.
- [ ] `task_cancel` está registrado automáticamente.
- [ ] No aparecen en `tools.txt`.
- [ ] `task_status` puede informar de que no hay tareas.
- [ ] Se ha anotado que `task_cancel` requiere una tarea larga real.

---

# BLOQUE I — HERRAMIENTA LOCAL DEL PERFIL DEFAULT

## 17. Comprobar `sweep_look`

`sweep_look` pertenece a la aplicación oficial, pero está implementada dentro del perfil:

```text
profiles\default\sweep_look.py
```

No es una herramienta compartida.

### 17.1. No añadir directamente a Ahootsa

No escribir todavía:

```text
sweep_look
```

en:

```text
external_content\external_profiles\ahootsa\tools.txt
```

Si se añade solo el nombre, el cargador buscará:

```text
external_content\external_profiles\ahootsa\sweep_look.py
```

y después:

```text
src\reachy_mini_conversation_app\tools\sweep_look.py
```

Ninguno de esos archivos existe en esta fase.

### 17.2. Probar con el perfil oficial

1. Abrir la interfaz.
2. Seleccionar el perfil integrado `default`.
3. Iniciar la conversación.
4. Pedir:

```text
Look slowly from left to right and return to the center.
```

o:

```text
Mira lentamente de izquierda a derecha y vuelve al centro.
```

### 17.3. Log esperado

```text
Tool call: sweep_look
```

### 17.4. Resultado esperado en MuJoCo

Secuencia:

```text
izquierda
pausa
centro
derecha
pausa
centro
```

### 17.5. Volver a Ahootsa

Después de la prueba:

1. seleccionar `ahootsa`;
2. comprobar el perfil actual;
3. confirmar la voz.

```powershell
Invoke-RestMethod http://127.0.0.1:7860/api/v1/personalities |
    Format-List

Invoke-RestMethod http://127.0.0.1:7860/api/v1/voices/current
```

### 17.6. Decisión para la Fase 4

Si interesa incorporar `sweep_look` a Ahootsa, se tratará como una integración explícita:

```text
copiar o adaptar profiles\default\sweep_look.py
a external_content\external_profiles\ahootsa\sweep_look.py
```

No se realiza en la Fase 3.

---

# BLOQUE J — CIERRE DE LA APLICACIÓN

## 18. Comprobar `go_to_sleep`

Esta debe ser la última prueba.

### 18.1. Contenido temporal de `tools.txt`

```text
go_to_sleep
```

Reiniciar la aplicación.

### 18.2. Petición ambigua que no debe cerrar

Decir:

```text
Estoy un poco cansado.
```

Ahootsa no debe cerrar la aplicación.

Puede responder de forma empática o proponer descansar.

### 18.3. Emoción de sueño que no debe cerrar

Decir:

```text
Haz una expresión de sueño.
```

Con `play_emotion` deshabilitada en esta prueba, no debe confundir la frase con una orden de cierre.

### 18.4. Petición explícita

Decir:

```text
Ahootsa, ve a dormir y termina la aplicación.
```

Log esperado:

```text
Tool call: go_to_sleep
Going to sleep before stopping conversation app
```

### 18.5. Resultado esperado

- Reachy ejecuta la postura de sueño.
- La aplicación de conversación se detiene.
- El puerto `7860` deja de responder.
- El daemon puede seguir activo en el puerto `8000`.

Comprobar:

```powershell
Test-NetConnection 127.0.0.1 -Port 7860
Test-NetConnection 127.0.0.1 -Port 8000
```

Resultado previsto:

```text
7860 : False
8000 : True
```

### 18.6. Reiniciar después de la prueba

```powershell
reachy-mini-conversation-app --ui --debug
```

### 18.7. Criterio de aceptación

- [ ] Una frase ambigua no cierra la app.
- [ ] Solo una petición explícita invoca `go_to_sleep`.
- [ ] Se ejecuta la postura de sueño.
- [ ] La aplicación se detiene.
- [ ] El daemon permanece disponible.
- [ ] La aplicación puede iniciarse nuevamente.

---

## 19. `tools.txt` recomendado al terminar la Fase 3

### 19.1. Variante recomendada durante la simulación

```text
# Movimiento sencillo
move_head

# Emociones
play_emotion
stop_emotion

# Inactividad
idle_do_nothing

# Bailes
dance
stop_dance

# Cámara de la fuente disponible en el daemon
camera

# Memoria explícita y no sensible
remember
forget

# Cierre solo ante petición explícita
go_to_sleep

# Pendiente de validación completa con cámara física
# head_tracking
```

### 19.2. Variante para el robot físico, después de validar la cámara

```text
move_head
play_emotion
stop_emotion
idle_do_nothing
dance
stop_dance
camera
head_tracking
remember
forget
go_to_sleep
```

### 19.3. No añadir manualmente

```text
task_status
task_cancel
```

La aplicación los añade automáticamente.

### 19.4. No añadir todavía

```text
sweep_look
```

Requiere incorporar su archivo Python al perfil externo y corresponde a la Fase 4.

---

## 20. Aplicar el archivo final

Detener la aplicación.

Abrir:

```powershell
notepad .\external_content\external_profiles\ahootsa\tools.txt
```

Pegar la variante elegida.

Reiniciar:

```powershell
reachy-mini-conversation-app --ui --debug
```

Comprobar:

```powershell
$perfil = Invoke-RestMethod `
    "http://127.0.0.1:7860/api/v1/personalities/load?name=ahootsa"

$perfil.enabled_tools
```

Comprobar el registro completo:

```powershell
.\.venv\Scripts\python.exe -c "import reachy_mini_conversation_app.tools.core_tools as c; c.initialize_tools(force=True); print('\n'.join(sorted(c.ALL_TOOLS)))"
```

---

## 21. Matriz final de validación

| Herramienta | Validación en MuJoCo | Validación con robot físico | Resultado esperado |
|---|---:|---:|---|
| `move_head` | Completa | Repetir | Cinco direcciones correctas |
| `play_emotion` | Completa | Repetir | Emoción en cola y movimiento visible |
| `stop_emotion` | Completa | Repetir | Cola y movimiento detenidos |
| `idle_do_nothing` | Completa | Opcional | Inactividad sin acción |
| `dance` | Completa | Repetir con espacio libre | Baile visible |
| `stop_dance` | Completa | Repetir | Movimiento detenido |
| `camera` | Según fuente virtual disponible | Obligatoria | Fotograma real y descripción |
| `head_tracking` | Parcial | Obligatoria | Seguimiento real de una cara |
| `remember` | Completa | No depende del robot | Persistencia correcta |
| `forget` | Completa | No depende del robot | Eliminación exacta |
| `go_to_sleep` | Completa | Repetir | Postura y cierre |
| `task_status` | Registro y estado | No depende del robot | Estado de tareas |
| `task_cancel` | Registro | Con tarea larga en Fase 4 | Cancelación por `tool_id` |
| `sweep_look` | Completa con perfil `default` | Repetir | Barrido lateral completo |

---

## 22. Problemas frecuentes

### La herramienta aparece en `tools.txt`, pero no se carga

Comprobar el log:

```text
Tool not found in profile or shared tools
```

Comprobar su existencia:

```powershell
Get-ChildItem `
    .\src\reachy_mini_conversation_app\tools `
    -Filter *.py |
    Select-Object Name
```

### El perfil activo no es Ahootsa

```powershell
(Invoke-RestMethod `
    http://127.0.0.1:7860/api/v1/personalities).current
```

Volver a seleccionar `ahootsa`.

### Los cambios de `tools.txt` no aparecen

Reiniciar la aplicación o volver a seleccionar el perfil.

### La emoción tarda mucho la primera vez

La primera ejecución puede descargar el conjunto de datos.

Esperar y mantener Internet disponible.

### No hay bailes

Comprobar:

```powershell
.\.venv\Scripts\python.exe -c "from reachy_mini_dances_library.collection.dance import AVAILABLE_MOVES; print(len(AVAILABLE_MOVES))"
```

### Cámara deshabilitada

No iniciar con:

```text
--no-camera
```

### No hay fotograma

Revisar el daemon y su Swagger:

```text
http://127.0.0.1:8000/docs
```

### Head tracking dice que funciona, pero no se mueve

La herramienta coloca la orden en el gestor de movimiento. Revisar obligatoriamente la terminal por:

```text
Head-tracking toggle failed
```

En MuJoCo puede faltar un rostro visible para realizar la comprobación completa.

### No aparece `memory.v1.json`

Comprobar el log de `remember` y obtener la ruta con:

```powershell
.\.venv\Scripts\python.exe -c "from reachy_mini_conversation_app.memory import memory_path_for_instance; print(memory_path_for_instance())"
```

### La aplicación se cierra

Puede haberse ejecutado:

```text
go_to_sleep
```

Comprobar que el daemon sigue activo y reiniciar la aplicación.

### `task_cancel` no detiene un baile

Es el comportamiento esperado.

Utilizar:

```text
stop_dance
```

Para emociones:

```text
stop_emotion
```

---

## 23. Criterios de aceptación de la Fase 3

- [ ] Se ha creado una copia del `tools.txt` de la Fase 2.
- [ ] Se han añadido las reglas de uso seguro a `instructions.txt`.
- [ ] Se ha comprobado el perfil activo.
- [ ] Se han enumerado las herramientas del registro real.
- [ ] Se han comprobado las cinco direcciones de `move_head`.
- [ ] Se ha probado `play_emotion`.
- [ ] Se ha probado `stop_emotion`.
- [ ] Se ha probado `idle_do_nothing` tras la inactividad.
- [ ] Se ha probado `dance`.
- [ ] Se ha probado `stop_dance`.
- [ ] Se ha probado `camera`.
- [ ] Se ha identificado la fuente visual.
- [ ] Se ha comprobado el encendido y apagado de `head_tracking`.
- [ ] Se ha anotado su validación pendiente con robot físico.
- [ ] Se ha probado `remember` con un dato ficticio.
- [ ] Se ha probado la persistencia tras reiniciar.
- [ ] Se ha probado `forget`.
- [ ] Se ha restaurado la memoria anterior.
- [ ] Se ha comprobado el registro automático de `task_status`.
- [ ] Se ha comprobado el registro automático de `task_cancel`.
- [ ] Se ha probado `sweep_look` con el perfil `default`.
- [ ] Se ha probado `go_to_sleep` al final.
- [ ] Se ha restaurado la aplicación después del cierre.
- [ ] Se ha creado el `tools.txt` final.
- [ ] No se ha modificado código Python oficial.

---

## 24. Archivos modificados en esta fase

### Modificados

```text
external_content\external_profiles\ahootsa\instructions.txt
external_content\external_profiles\ahootsa\tools.txt
```

### Creados para documentación

```text
docs\copias_configuracion\ahootsa_tools_FASE2.txt
```

### Sin cambios

```text
src\
profiles\
external_tools\
pyproject.toml
uv.lock
```

No se copia todavía:

```text
profiles\default\sweep_look.py
```

---

## 25. Siguiente fase

Después de validar las herramientas oficiales:

```text
Fase 4
└── incorporación progresiva de funciones de Ahootsa
```

Orden recomendado para la Fase 4:

```text
1. herramienta externa mínima de prueba
2. ask_ollama
3. cámara del ordenador, si sigue siendo necesaria
4. exploración de imágenes
5. actividades de comunicación
6. juego de parejas
7. actividades y bailes propios
8. gestión de tareas largas con task_status y task_cancel
9. paneles o interfaz ampliada
```

Cada función se incorporará como herramienta externa o como actividad compatible con la arquitectura oficial, evitando modificar el núcleo mientras no sea imprescindible.
