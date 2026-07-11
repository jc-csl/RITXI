# Ahootsa 8 — Fase 6
## Herramientas conversacionales para la actividad «Vamos a bailar»

**Proyecto:** Ahootsa 8  
**Aplicación base:** `reachy_mini_conversation_app 0.9.0`  
**SDK:** `reachy-mini 1.9.0`  
**Requisito previo:** Fase 5 completada y verificada  
**Estado de este documento:** diseño e instrucciones de implantación  
**Objetivo:** conectar la biblioteca local de 16 bailes con la conversación mediante herramientas externas, sin modificar el código oficial.

---

## 1. Relación con las fases anteriores

La arquitectura queda dividida de esta manera:

```text
Fase 4
└── descarga, caché e inventario de datasets completos

Fase 5
└── copia local de los 16 bailes seleccionados dentro de Ahootsa

Fase 6
└── herramientas externas para:
    ├── consultar el catálogo
    ├── reproducir un baile
    └── detenerlo
```

La Fase 4 sigue siendo la fuente de adquisición y recuperación.

La Fase 5 ya debe contener:

```text
external_content\
└── activities\
    └── vamos_a_bailar\
        ├── actividad.json
        ├── catalogo_bailes.json
        ├── local_recorded_moves.py
        ├── inventario_recursos_locales.json
        ├── verificacion_biblioteca_local.json
        └── dataset\
            └── data\
                ├── 16 archivos JSON
                ├── 15 archivos OGG
                └── 1 archivo WAV
```

La Fase 6 no vuelve a descargar datasets y no necesita consultar el Hub durante la reproducción.

---

## 2. Alcance de la Fase 6

Esta fase incorporará tres herramientas conversacionales:

```text
list_ahootsa_dances
play_ahootsa_dance
stop_ahootsa_dance
```

La persona podrá decir, por ejemplo:

```text
¿Qué bailes sabes hacer?
Pon Las Ketchup.
Quiero bailar Thriller.
Haz el baile de Star Wars.
Para el baile.
```

El flujo será:

```text
Persona
→ reconocimiento de voz
→ modelo conversacional
→ herramienta externa
→ catálogo local de Ahootsa
→ movimiento RecordedMove
→ MovementManager
→ robot o MuJoCo

                              └→ audio local
                                 → sistema multimedia
                                 → altavoz del robot o Windows
```

---

## 3. Principios de implementación

La Fase 6 debe cumplir estos criterios:

```text
extensión oficial
└── herramientas externas

sin modificar el núcleo
└── no tocar src/reachy_mini_conversation_app

recursos locales
└── no depender de la caché de Hugging Face en ejecución

una actividad cada vez
└── no solapar dos bailes

parada inmediata
└── detener movimiento y sonido

sin inicio automático
└── no bailar por inactividad

sin voz sobre la música
└── no generar una respuesta hablada después de iniciar el baile
```

---

## 4. Decisión de arquitectura de herramientas

Se utilizará un único archivo externo:

```text
external_content\
└── external_tools\
    └── ahootsa_dances.py
```

Ese módulo definirá tres clases derivadas de `Tool`:

```text
ListAhootsaDances
PlayAhootsaDance
StopAhootsaDance
```

Sus nombres expuestos al modelo serán:

```text
list_ahootsa_dances
play_ahootsa_dance
stop_ahootsa_dance
```

### Por qué se utiliza un solo módulo

La aplicación oficial puede cargar varias clases `Tool` definidas dentro del mismo archivo.

Esto permite:

- compartir el catálogo;
- compartir el cargador local;
- compartir el estado del baile activo;
- evitar duplicación de código;
- evitar problemas al importar módulos auxiliares desde archivos externos;
- sincronizar `play` y `stop`.

En `tools.txt` se añadirá el nombre del módulo:

```text
ahootsa_dances
```

No se escribirán allí los tres nombres de las clases.

El registro final mostrará tres herramientas, aunque `tools.txt` contenga una sola línea para este módulo.

---

## 5. Estructura después de la Fase 6

```text
reachy_mini_conversation_app\
├── .env
│
└── external_content\
    ├── activities\
    │   └── vamos_a_bailar\
    │       ├── actividad.json
    │       ├── catalogo_bailes.json
    │       ├── local_recorded_moves.py
    │       ├── inventario_recursos_locales.json
    │       ├── verificacion_biblioteca_local.json
    │       └── dataset\
    │           └── data\
    │               └── 32 recursos
    │
    ├── external_profiles\
    │   └── ahootsa\
    │       ├── instructions.txt
    │       ├── greeting.txt
    │       ├── tools.txt
    │       └── voice.txt
    │
    └── external_tools\
        └── ahootsa_dances.py
```

---

## 6. Configuración de `.env`

Añadir o comprobar:

```text
REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY=./external_content/external_profiles
REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY=./external_content/external_tools
REACHY_MINI_CUSTOM_PROFILE=ahootsa
AUTOLOAD_EXTERNAL_TOOLS=false
```

### Motivo de `AUTOLOAD_EXTERNAL_TOOLS=false`

La carga debe ser explícita y controlada desde:

```text
external_content\external_profiles\ahootsa\tools.txt
```

Así:

- no se activa por accidente cualquier archivo Python;
- cada herramienta queda asociada al perfil;
- el inventario de herramientas es reproducible;
- resulta más sencillo diagnosticar el arranque.

---

## 7. Herramientas que debe exponer el módulo

### 7.1. `list_ahootsa_dances`

**Finalidad:** devolver el catálogo ordenado.

**Respuesta esperada:**

```json
{
  "status": "success",
  "count": 16,
  "activity": "vamos_a_bailar",
  "dances": [
    {
      "id": "dance1",
      "name": "Baile 1",
      "group": "Bailes cortos"
    }
  ]
}
```

**Comportamiento:**

- lee `catalogo_bailes.json`;
- conserva el orden definido en la Fase 5;
- devuelve únicamente entradas activas;
- no reproduce movimiento;
- no reproduce audio;
- permite que Ahootsa responda después.

**Configuración:**

```text
needs_response = true
```

La respuesta hablada no debe leer las 16 opciones de una vez.

Ahootsa ofrecerá como máximo dos o tres opciones por turno y preguntará cuál prefiere la persona.

---

### 7.2. `play_ahootsa_dance`

**Finalidad:** reproducir un movimiento y su audio local.

**Parámetro:**

```json
{
  "dance_id": "las-ketchup"
}
```

El esquema deberá limitar el valor a los 16 identificadores del catálogo:

```text
dance1
dance2
dance3
las-ketchup
michael-jackson-thriller
spice-girls
pharrell-williams-happy
queen-we-will-rock-you
the-white-stripes-seven-nation-army
bohemian-rhapsody
happy-birthday
harry-potter
star-wars
the-lion-king
titanic
secret-dance
```

**Comportamiento:**

1. valida el identificador;
2. comprueba que la entrada esté activa;
3. localiza JSON y audio;
4. detiene un baile anterior si todavía existe;
5. construye un objeto oficial `RecordedMove`;
6. encola el movimiento en `MovementManager`;
7. inicia el audio local mediante el sistema multimedia;
8. registra nombre, duración y rutas;
9. devuelve el estado de inicio.

**Respuesta interna prevista:**

```json
{
  "status": "started",
  "dance_id": "las-ketchup",
  "name": "Las Ketchup",
  "duration_seconds": 15.0,
  "audio": true,
  "replaced_previous": false
}
```

**Configuración:**

```text
needs_response = false
```

Esto evita que la voz de Ahootsa se superponga a la música después de iniciar el baile.

Antes de llamar a la herramienta, el modelo puede decir una frase muy breve:

```text
¡Vamos a bailar!
```

Después debe permanecer en silencio mientras se reproduce.

---

### 7.3. `stop_ahootsa_dance`

**Finalidad:** detener inmediatamente movimiento y audio.

**Comportamiento:**

```text
stop_sound
+
clear_move_queue
+
limpiar estado de la actividad
```

**Respuesta interna prevista:**

```json
{
  "status": "stopped",
  "previous_dance_id": "las-ketchup"
}
```

**Configuración:**

```text
needs_response = true
```

Después de parar, Ahootsa puede responder:

```text
Vale, lo paro.
```

La parada no debe requerir confirmación adicional.

---

## 8. Cargador local

El módulo utilizará:

```text
external_content\activities\vamos_a_bailar\
local_recorded_moves.py
```

No utilizará:

```python
RecordedMoves("D:\\ruta\\local")
```

porque en `reachy-mini 1.9.0` esa clase interpreta el texto como un identificador de Hugging Face.

La carga local correcta es:

```text
JSON local
+
audio local
+
RecordedMove del SDK
```

El módulo externo localizará la actividad mediante una ruta relativa calculada desde `__file__`.

Esquema:

```python
TOOLS_DIR = Path(__file__).resolve().parent
EXTERNAL_CONTENT_DIR = TOOLS_DIR.parent
ACTIVITY_DIR = (
    EXTERNAL_CONTENT_DIR
    / "activities"
    / "vamos_a_bailar"
)
```

No se escribirán rutas absolutas como:

```text
D:\ritxi\...
C:\Users\Alumno\...
```

---

## 9. Reproducción del movimiento

El objeto local obtenido debe ser compatible con:

```python
deps.movement_manager.queue_move(recorded_move)
```

`MovementManager` se encargará de:

- ejecutar un único movimiento primario;
- evaluar la trayectoria;
- enviar posiciones al robot;
- mantener la secuencia;
- volver después al comportamiento normal.

No se llamará directamente a `set_target` desde la herramienta.

Esto mantiene un único punto de control del movimiento.

---

## 10. Reproducción del audio

La herramienta usará el sistema multimedia disponible en:

```python
deps.reachy_mini.media
```

Operaciones previstas:

```text
play_sound(ruta_audio)
stop_sound()
```

En MuJoCo:

```text
audio
└── salida predeterminada de Windows
```

En el robot físico:

```text
audio
└── altavoz gestionado por Reachy Mini
```

La herramienta registrará por separado:

- instante de encolado del movimiento;
- instante de inicio del audio;
- duración estimada;
- finalización o parada.

En esta fase no se aplicará una compensación artificial fija.

La sincronización fina se validará más adelante con el robot físico.

---

## 11. Estado compartido de la actividad

El módulo mantendrá un estado interno mínimo:

```text
active_dance_id
active_dance_name
started_at_monotonic
duration_seconds
audio_path
```

También utilizará un bloqueo para impedir dos inicios simultáneos.

Reglas:

```text
sin baile activo
└── iniciar normalmente

baile activo + nueva elección explícita
└── detener el anterior y comenzar el nuevo

petición de parada
└── detener sonido y movimiento inmediatamente

baile ya terminado
└── limpiar estado cuando se detecte una nueva operación
```

No se guardará este estado en la memoria de usuario.

No debe persistir entre reinicios de la aplicación.

---

## 12. Cambios en `tools.txt`

Archivo:

```text
external_content\external_profiles\ahootsa\tools.txt
```

Configuración recomendada al finalizar la Fase 6:

```text
move_head
play_emotion
stop_emotion
idle_do_nothing
remember
forget
go_to_sleep
ahootsa_dances
```

### Herramientas oficiales de baile

Comentar o retirar:

```text
dance
stop_dance
```

Motivos:

- evitar dos sistemas de baile distintos;
- impedir el baile aleatorio oficial;
- evitar que la política de inactividad seleccione `dance`;
- garantizar que Ahootsa utilice el catálogo local;
- mantener control sobre audio y parada.

### Cámara

Puede mantenerse comentada durante la simulación:

```text
# camera
```

Se reactivará cuando se pruebe el robot físico.

### Herramientas de sistema

No escribir manualmente:

```text
task_status
task_cancel
```

La aplicación las añade automáticamente.

En la versión actual presentan el error conocido de `call_id`, por lo que las instrucciones deben evitar que el modelo las use.

---

## 13. Bloque para `instructions.txt`

Añadir al final:

```text
ACTIVIDAD VAMOS A BAILAR

Cuando la persona pregunte qué bailes sabes hacer, utiliza
list_ahootsa_dances.

No leas toda la lista de una vez.

Ofrece como máximo dos o tres opciones por turno.

Haz una sola pregunta breve para que la persona elija.

Utiliza play_ahootsa_dance únicamente después de que la persona haya elegido
un baile de forma clara.

Antes de iniciar el baile puedes decir una frase muy breve, por ejemplo:
“¡Vamos a bailar!”.

Después de iniciar play_ahootsa_dance, no hables mientras suena la música.

No inicies bailes automáticamente.

No inicies bailes por inactividad.

No elijas un baile al azar cuando la persona no haya expresado una preferencia.

Si la persona dice “para”, “detén el baile”, “basta” o una expresión equivalente,
utiliza inmediatamente stop_ahootsa_dance.

La parada no necesita confirmación.

No utilices las herramientas oficiales dance ni stop_dance.

No utilices task_status ni task_cancel para comprobar el estado de esta
actividad.
```

---

## 14. Nombres naturales y alias

El catálogo de la Fase 5 ya contiene alias.

Ejemplos:

```text
“Aserejé”
└── las-ketchup

“Thriller”
└── michael-jackson-thriller

“Happy”
└── pharrell-williams-happy

“We Will Rock You”
└── queen-we-will-rock-you

“Seven Nation Army”
└── the-white-stripes-seven-nation-army

“Cumpleaños feliz”
└── happy-birthday

“El rey león”
└── the-lion-king

“Baile secreto”
└── secret-dance
```

La descripción de `play_ahootsa_dance` debe incorporar estos nombres para facilitar la elección correcta del identificador.

---

## 15. Arranque después de aplicar la Fase 6

### Terminal 1 — daemon

```powershell
cd D:\ritxi\AHOOTSA8\reachy_mini_conversation_app

.\.venv\Scripts\reachy-mini-daemon.exe `
    --sim `
    --scene minimal
```

### Terminal 2 — aplicación

```powershell
cd D:\ritxi\AHOOTSA8\reachy_mini_conversation_app

.\.venv\Scripts\reachy-mini-conversation-app.exe `
    --ui `
    --debug
```

No es necesario reinstalar los datasets.

No es necesario volver a ejecutar la Fase 4.

---

## 16. Logs esperados durante la carga

Deberán aparecer mensajes equivalentes a:

```text
Loading external profile 'ahootsa'
Loading tools for profile: ahootsa
Found ... tools to load: [..., 'ahootsa_dances', ...]
Loaded external tool: ahootsa_dances
tool registered: list_ahootsa_dances
tool registered: play_ahootsa_dance
tool registered: stop_ahootsa_dance
```

La línea:

```text
Found ... tools to load
```

contará módulos solicitados desde `tools.txt`.

Las líneas:

```text
tool registered
```

mostrarán las tres herramientas reales definidas en el módulo.

---

## 17. Pruebas de validación

### Prueba 1 — Compilación

```powershell
.\.venv\Scripts\python.exe -m py_compile `
    .\external_content\external_tools\ahootsa_dances.py
```

Resultado esperado:

```text
sin salida
código de retorno 0
```

---

### Prueba 2 — Verificación previa de Fase 5

```powershell
.\.venv\Scripts\python.exe `
    .\external_content\activities\vamos_a_bailar\
verificar_biblioteca_local.py
```

Debe terminar con:

```text
RESULTADO: OK
```

No iniciar la aplicación si esta comprobación falla.

---

### Prueba 3 — Carga de herramientas

Arrancar la aplicación y comprobar:

```text
list_ahootsa_dances
play_ahootsa_dance
stop_ahootsa_dance
```

No debe aparecer:

```text
Missing dependency
Tool file not found
Duplicate Tool.name
```

---

### Prueba 4 — Consultar catálogo

Decir:

```text
¿Qué bailes sabes hacer?
```

Resultado esperado:

```text
llamada a list_ahootsa_dances
+
respuesta breve
+
dos o tres opciones
+
una sola pregunta
```

No debe enumerar oralmente las 16 canciones.

---

### Prueba 5 — Baile corto

Decir:

```text
Pon el Baile 1.
```

Esperado:

```text
tool_name='play_ahootsa_dance'
dance_id='dance1'
movimiento visible
audio audible
sin voz posterior superpuesta
```

---

### Prueba 6 — Las Ketchup

Decir:

```text
Pon el Aserejé.
```

Esperado:

```text
dance_id='las-ketchup'
```

---

### Prueba 7 — Thriller

Decir:

```text
Quiero bailar Thriller.
```

Esperado:

```text
dance_id='michael-jackson-thriller'
```

---

### Prueba 8 — Parada

Durante un baile largo, decir:

```text
Para.
```

Esperado:

```text
tool_name='stop_ahootsa_dance'
audio detenido
movimiento detenido
cola limpiada
respuesta breve de confirmación
```

---

### Prueba 9 — Sustitución

Durante un baile, decir:

```text
Pon ahora Star Wars.
```

Esperado:

```text
baile anterior detenido
+
nuevo movimiento iniciado
+
sin solapamiento de audio
```

---

### Prueba 10 — Nombre inexistente

Decir:

```text
Pon el baile de Macarena.
```

Esperado:

- no inventar un identificador;
- no ejecutar ningún archivo;
- explicar brevemente que no está disponible;
- ofrecer dos alternativas del catálogo.

---

### Prueba 11 — Inactividad

Dejar la aplicación sin interacción durante más de 180 segundos.

Esperado:

```text
no se inicia ningún baile local
no se inicia el dance oficial
```

Puede ejecutarse:

```text
idle_do_nothing
```

---

## 18. Logs funcionales previstos

Inicio:

```text
Tool call: play_ahootsa_dance dance_id=las-ketchup
Ahootsa local dance started
move=las-ketchup
duration=...
audio=...
```

Parada:

```text
Tool call: stop_ahootsa_dance
Ahootsa local dance stopped
previous_move=las-ketchup
```

Listado:

```text
Tool call: list_ahootsa_dances
Ahootsa dance catalog returned
count=16
```

Error:

```text
Unknown Ahootsa dance id
Missing local movement file
Missing local audio file
Local dance library unavailable
```

Los logs no deben incluir el contenido binario del audio.

---

## 19. Limitaciones conocidas

### `clear_move_queue`

La parada de la Fase 6 utilizará:

```text
movement_manager.clear_move_queue()
```

Esto detiene el movimiento primario actual y vacía la cola completa.

Por tanto, también puede detener una emoción que se hubiera iniciado simultáneamente.

Esta limitación es aceptable porque Ahootsa no debe ejecutar otra emoción mientras baila.

### `stop_sound`

Detiene el sonido reproducido por el sistema multimedia.

No distingue entre una canción de la actividad y otro sonido iniciado al mismo tiempo.

La regla será:

```text
durante Vamos a bailar
└── no iniciar otros sonidos
```

### Sincronización

Movimiento y audio se inician desde dos subsistemas.

La sincronización se considerará válida inicialmente si resulta natural en MuJoCo.

El ajuste fino se hará con el robot físico.

### Estado tras un reinicio

El estado del baile activo no se conserva.

Al reiniciar la aplicación se considera:

```text
ningún baile activo
```

---

## 20. Recuperación ante errores

### El módulo externo no carga

Comprobar:

```text
REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY
ruta external_content/external_tools
nombre ahootsa_dances.py
línea ahootsa_dances en tools.txt
```

### No encuentra la actividad

Comprobar:

```text
external_content/activities/vamos_a_bailar
```

La herramienta no debe buscarla en la caché.

### El catálogo no es válido

Ejecutar:

```powershell
.\.venv\Scripts\python.exe `
    .\external_content\activities\vamos_a_bailar\
verificar_biblioteca_local.py
```

### Se mueve, pero no hay audio

Comprobar:

- archivo local asociado;
- salida de audio predeterminada;
- volumen;
- avisos de GStreamer;
- bloqueo del dispositivo de Windows.

### Se oye audio, pero no se mueve

Comprobar:

- carga de `RecordedMove`;
- `movement_manager.queue_move`;
- daemon;
- MuJoCo;
- errores al evaluar la trayectoria.

### Habla encima de la canción

Comprobar:

```text
PlayAhootsaDance.needs_response = False
```

y las instrucciones del perfil.

### Empieza a bailar por inactividad

Comprobar que `tools.txt` no contenga:

```text
dance
```

---

## 21. Marcha atrás

Para desactivar temporalmente la Fase 6:

1. comentar en `tools.txt`:

```text
# ahootsa_dances
```

2. reiniciar la aplicación.

No es necesario borrar:

```text
external_content\activities\vamos_a_bailar
external_content\external_tools\ahootsa_dances.py
```

La Fase 5 permanecerá intacta.

---

## 22. Criterios de aceptación

La Fase 6 se considera completada cuando:

- [ ] Existe `external_content/external_tools/ahootsa_dances.py`.
- [ ] `.env` define `REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY`.
- [ ] `AUTOLOAD_EXTERNAL_TOOLS=false`.
- [ ] `tools.txt` contiene `ahootsa_dances`.
- [ ] `tools.txt` no contiene `dance`.
- [ ] El módulo compila.
- [ ] La verificación de la Fase 5 termina con `RESULTADO: OK`.
- [ ] Se registran las tres herramientas.
- [ ] `list_ahootsa_dances` devuelve 16 entradas.
- [ ] Ahootsa ofrece como máximo tres opciones oralmente.
- [ ] `play_ahootsa_dance` reproduce movimiento local.
- [ ] `play_ahootsa_dance` reproduce el audio asociado.
- [ ] Ahootsa no habla encima de la canción.
- [ ] `stop_ahootsa_dance` detiene audio y movimiento.
- [ ] Un segundo baile no se solapa con el primero.
- [ ] Los alias `Aserejé`, `Thriller`, `Happy` y `Star Wars` se resuelven.
- [ ] Un nombre inexistente no inicia ningún movimiento.
- [ ] La inactividad no inicia un baile.
- [ ] No se modifica el código oficial.
- [ ] No se consulta Hugging Face durante la reproducción.
- [ ] Los errores quedan registrados de forma comprensible.

---

## 23. Qué no forma parte de esta fase

La Fase 6 no incorpora todavía:

- botones táctiles;
- pantalla visual de selección;
- imágenes o carátulas;
- clasificación por dificultad;
- control de volumen desde la actividad;
- favoritos por persona;
- listas personalizadas;
- calibración física definitiva;
- publicación de audios;
- instalación como aplicación independiente de Desktop.

Estas funciones corresponden a fases posteriores.

---

## 24. Resultado esperado

```text
Conversación Ahootsa
└── ahotsa_dances.py
    ├── list_ahootsa_dances
    ├── play_ahootsa_dance
    └── stop_ahootsa_dance
        │
        └── actividad local Vamos a bailar
            ├── catálogo
            ├── 16 movimientos
            └── 16 audios
```

La Fase 6 deja operativo el backend conversacional de «Vamos a bailar».

La siguiente fase podrá convertirlo en una actividad accesible y visible desde la interfaz táctil.

---

## 25. Fase siguiente

```text
Fase 7
└── actividad accesible “Vamos a bailar”
    ├── panel táctil
    ├── selección visual
    ├── botones grandes
    ├── reproducción
    ├── parada
    └── retorno a la conversación
```
