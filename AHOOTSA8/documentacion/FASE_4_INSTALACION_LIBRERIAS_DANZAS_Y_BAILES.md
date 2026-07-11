# Ahootsa 8 — Fase 4
## Instalación en el sistema de bibliotecas de danzas y bailes adicionales

**Documento:** Fase 4  
**Proyecto:** Ahootsa 8  
**Requisito previo:** Fases 0, 1, 2 y 3 completadas  
**Aplicación:** `reachy_mini_conversation_app 0.9.0`  
**SDK y daemon:** `reachy-mini 1.9.0`  
**Entorno:** Windows, `.venv` del proyecto y daemon manual en MuJoCo  
**Objetivo:** descargar, registrar en caché y comprobar bibliotecas oficiales y comunitarias antes de integrarlas en actividades de Ahootsa

---

## 1. Alcance

Esta fase prepara el sistema de movimientos, pero todavía no crea una actividad conversacional ni una herramienta externa nueva.

```text
Fase 4
├── confirmar el daemon manual
├── diferenciar aplicaciones y datasets
├── instalar datasets oficiales
├── instalar datasets comunitarios
├── comprobar la caché de Hugging Face
├── enumerar movimientos desde el daemon
├── probar movimiento sin audio
├── probar movimientos con audio
├── detener movimientos mediante UUID
└── generar el inventario funcional
```

No se modifica:

```text
src\
profiles\
external_tools\
pyproject.toml
uv.lock
```

No se añaden todavía estos datasets a `tools.txt`.

---

## 2. Daemon utilizado

El árbol de procesos observado es:

```text
D:\RITXI\AHOOTSA8\reachy_mini_conversation_app\.venv\Scripts\python.exe
└── D:\RITXI\AHOOTSA8\reachy_mini_conversation_app\.venv\Scripts\reachy-mini-daemon.exe
    └── --sim --scene minimal
```

Esto confirma que el daemon se ha iniciado manualmente desde la `.venv` de Ahootsa.

`pyvenv.cfg` contiene:

```text
home = C:\Users\Alumno\AppData\Local\Reachy Mini Control\cpython-3.12-windows-x86_64-none
```

Esto indica que la `.venv` se creó utilizando como intérprete base el Python de Reachy Mini Control. No significa que Desktop Control haya iniciado el daemon actual.

Para esta fase se conserva el entorno porque:

- el daemon arranca correctamente;
- MuJoCo funciona;
- los movimientos funcionan;
- las dependencias están aisladas en `.venv`;
- recrear el entorno no es necesario para instalar datasets.

La independencia total del intérprete base se tratará más adelante durante el despliegue reproducible.

---

## 3. Qué significa “instalar una biblioteca”

Las bibliotecas de movimientos no se instalan mediante:

```text
POST /api/apps/install
```

Ese endpoint instala aplicaciones de Hugging Face Spaces.

Las danzas y emociones son datasets de Hugging Face con archivos como:

```text
movimiento.json
movimiento.wav
movimiento.ogg
```

El daemon usa `RecordedMoves`:

1. busca el dataset en la caché local;
2. si no existe, lo descarga;
3. analiza los JSON de la raíz y de `data/`;
4. busca un audio con el mismo nombre;
5. registra los movimientos;
6. permite listarlos y reproducirlos mediante la API.

En esta fase:

```text
instalar dataset
=
descargar en caché
+
listar desde el daemon
+
reproducir una muestra
```

---

## 4. FastAPI del daemon

Abrir:

```text
http://127.0.0.1:8000/docs
```

Endpoints utilizados:

```text
GET  /api/move/recorded-move-datasets/list/{dataset_name}
POST /api/move/play/recorded-move-dataset/{dataset_name}/{move_name}
GET  /api/move/running
POST /api/move/stop
```

El parámetro del dataset admite una ruta con `/`, por ejemplo:

```text
pollen-robotics/reachy-mini-emotions-library
Anne-Charlotte/music
```

En PowerShell se codifica con:

```powershell
[uri]::EscapeDataString($Dataset)
```

---

## 5. Datasets incluidos

### Oficiales

```text
pollen-robotics/reachy-mini-dances-library
pollen-robotics/reachy-mini-emotions-library
```

Características:

```text
reachy-mini-dances-library
└── movimientos sin audio

reachy-mini-emotions-library
├── emociones
├── dance1
├── dance2
├── dance3
└── audio asociado en la mayoría de movimientos
```

### Comunitarios

```text
Anne-Charlotte/music
Anne-Charlotte/reachy-songs
Anne-Charlotte/pollen-dance
apirrone/marionette-moves
ShivanshVikram/happy-dance
```

Estas bibliotecas siguen el formato de movimientos grabados de Reachy Mini y utilizan la etiqueta comunitaria:

```text
reachy_mini_community_moves
```

---

## 6. Inventario aportado

El CSV original tenía:

```text
150 filas
```

Siete filas correspondían a JSON internos de la caché con nombres SHA de 40 caracteres. No eran movimientos.

Inventario corregido:

```text
143 movimientos reales
122 con audio
21 sin audio
```

| Dataset | Movimientos | Con audio | Sin audio |
|---|---:|---:|---:|
| `Anne-Charlotte/music` | 16 | 16 | 0 |
| `Anne-Charlotte/pollen-dance` | 8 | 8 | 0 |
| `Anne-Charlotte/reachy-songs` | 10 | 10 | 0 |
| `ShivanshVikram/happy-dance` | 4 | 3 | 1 |
| `apirrone/marionette-moves` | 1 | 1 | 0 |
| `pollen-robotics/reachy-mini-dances-library` | 19 | 0 | 19 |
| `pollen-robotics/reachy-mini-emotions-library` | 85 | 84 | 1 |

El daemon no recorre toda la caché de manera recursiva. `RecordedMoves` solo analiza:

```text
raíz del dataset
data\
```

Por eso los JSON internos de descarga no deberían aparecer en el listado funcional del daemon.

Archivos generados:

```text
catalogo_bailes_descargados_limpio.csv
resumen_librerias_bailes_fase4.csv
```

---

## 7. Preparación

Detener únicamente la aplicación conversacional:

```text
Ctrl + C
```

Mantener abiertos:

```text
reachy-mini-daemon
MuJoCo
```

Entrar en la raíz:

```powershell
cd D:\ritxi\AHOOTSA8\reachy_mini_conversation_app
```

Activar:

```powershell
.\.venv\Scripts\Activate.ps1
```

Comprobar el daemon:

```powershell
Test-NetConnection 127.0.0.1 -Port 8000
```

Debe mostrar:

```text
TcpTestSucceeded : True
```

Comprobar salud:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health-check
```

Comprobar conexión con Hugging Face:

```powershell
Test-NetConnection huggingface.co -Port 443
```

---

## 8. Confirmar que el puerto pertenece al daemon de Ahootsa

```powershell
$conexion = Get-NetTCPConnection `
    -LocalPort 8000 `
    -State Listen

$daemonPid = $conexion.OwningProcess

Get-CimInstance Win32_Process `
    -Filter "ProcessId = $daemonPid" |
    Select-Object ProcessId,ParentProcessId,ExecutablePath,CommandLine |
    Format-List
```

La línea de comandos debe contener:

```text
D:\ritxi\AHOOTSA8\reachy_mini_conversation_app\.venv\Scripts\reachy-mini-daemon.exe
--sim
--scene minimal
```

---

## 9. Función manual para instalar y listar un dataset

Copiar en PowerShell:

```powershell
function Install-ReachyMoveDataset {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Dataset
    )

    $encoded = [uri]::EscapeDataString($Dataset)
    $uri = "http://127.0.0.1:8000/api/move/recorded-move-datasets/list/$encoded"

    Write-Host ""
    Write-Host "============================================================"
    Write-Host "Dataset: $Dataset"
    Write-Host "============================================================"

    try {
        $moves = Invoke-RestMethod `
            -Method Get `
            -Uri $uri `
            -TimeoutSec 600

        Write-Host "Estado: OK"
        Write-Host "Movimientos:" @($moves).Count

        $moves | Sort-Object
    }
    catch {
        Write-Host "Estado: ERROR"
        Write-Host $_.Exception.Message
    }
}
```

El endpoint de listado descarga el dataset si aún no está en la caché y después devuelve sus movimientos.

---

## 10. Instalar bibliotecas oficiales

```powershell
Install-ReachyMoveDataset `
    "pollen-robotics/reachy-mini-dances-library"

Install-ReachyMoveDataset `
    "pollen-robotics/reachy-mini-emotions-library"
```

El daemon `1.9.0` intenta precargar estas dos bibliotecas al iniciar, por lo que pueden estar ya disponibles.

---

## 11. Instalar bibliotecas comunitarias

```powershell
Install-ReachyMoveDataset "Anne-Charlotte/music"

Install-ReachyMoveDataset "Anne-Charlotte/reachy-songs"

Install-ReachyMoveDataset "Anne-Charlotte/pollen-dance"

Install-ReachyMoveDataset "apirrone/marionette-moves"

Install-ReachyMoveDataset "ShivanshVikram/happy-dance"
```

La primera llamada puede tardar varios minutos si el dataset contiene audio.

No cerrar el daemon mientras descarga.

---

## 12. Instalar los siete datasets en una secuencia

Después de definir `Install-ReachyMoveDataset`:

```powershell
$datasetsFase4 = @(
    "pollen-robotics/reachy-mini-dances-library",
    "pollen-robotics/reachy-mini-emotions-library",
    "Anne-Charlotte/music",
    "Anne-Charlotte/reachy-songs",
    "Anne-Charlotte/pollen-dance",
    "apirrone/marionette-moves",
    "ShivanshVikram/happy-dance"
)

foreach ($dataset in $datasetsFase4) {
    Install-ReachyMoveDataset $dataset
}
```

No se crea ningún script permanente; son comandos manuales de PowerShell.

---

## 13. Comprobar la caché

Ubicación normal:

```text
C:\Users\Alumno\.cache\huggingface\hub
```

Comprobar:

```powershell
Get-ChildItem `
    "$env:USERPROFILE\.cache\huggingface\hub" `
    -Directory |
    Where-Object {
        $_.Name -match "reachy|Anne-Charlotte|ShivanshVikram|apirrone"
    } |
    Select-Object Name,FullName
```

Carpetas esperadas:

```text
datasets--pollen-robotics--reachy-mini-dances-library
datasets--pollen-robotics--reachy-mini-emotions-library
datasets--Anne-Charlotte--music
datasets--Anne-Charlotte--reachy-songs
datasets--Anne-Charlotte--pollen-dance
datasets--apirrone--marionette-moves
datasets--ShivanshVikram--happy-dance
```

No modificar manualmente:

```text
blobs\
refs\
snapshots\
.cache\huggingface\download\
```

---

## 14. Crear el inventario funcional del daemon

```powershell
New-Item `
    -ItemType Directory `
    -Path D:\ritxi\AHOOTSA8\recursos_bailes `
    -Force

$datasetsFase4 = @(
    "pollen-robotics/reachy-mini-dances-library",
    "pollen-robotics/reachy-mini-emotions-library",
    "Anne-Charlotte/music",
    "Anne-Charlotte/reachy-songs",
    "Anne-Charlotte/pollen-dance",
    "apirrone/marionette-moves",
    "ShivanshVikram/happy-dance"
)

$inventario = foreach ($dataset in $datasetsFase4) {
    $encoded = [uri]::EscapeDataString($dataset)

    $moves = Invoke-RestMethod `
        -Method Get `
        -Uri "http://127.0.0.1:8000/api/move/recorded-move-datasets/list/$encoded" `
        -TimeoutSec 600

    foreach ($move in $moves) {
        [pscustomobject]@{
            Dataset = $dataset
            Movimiento = $move
        }
    }
}

$inventario |
    Sort-Object Dataset,Movimiento |
    Export-Csv `
        D:\ritxi\AHOOTSA8\recursos_bailes\inventario_daemon_fase4.csv `
        -Delimiter ";" `
        -NoTypeInformation `
        -Encoding UTF8
```

Abrir:

```powershell
Start-Process `
    D:\ritxi\AHOOTSA8\recursos_bailes\inventario_daemon_fase4.csv
```

Resumen:

```powershell
$inventario |
    Group-Object Dataset |
    Sort-Object Name |
    Select-Object Name,Count |
    Format-Table -AutoSize
```

La lista del daemon es la referencia funcional definitiva.

---

## 15. Función manual para reproducir

```powershell
function Start-ReachyRecordedMove {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Dataset,

        [Parameter(Mandatory = $true)]
        [string]$Move
    )

    $datasetEncoded = [uri]::EscapeDataString($Dataset)
    $moveEncoded = [uri]::EscapeDataString($Move)

    $uri = (
        "http://127.0.0.1:8000" +
        "/api/move/play/recorded-move-dataset" +
        "/$datasetEncoded/$moveEncoded"
    )

    Invoke-RestMethod `
        -Method Post `
        -Uri $uri `
        -TimeoutSec 600
}
```

La respuesta contiene un UUID. Guardarlo para poder detener el movimiento.

---

## 16. Prueba oficial sin audio

```powershell
$moveActual = Start-ReachyRecordedMove `
    -Dataset "pollen-robotics/reachy-mini-dances-library" `
    -Move "chicken_peck"

$moveActual
```

Resultado esperado:

- movimiento visible en MuJoCo;
- sin audio;
- UUID devuelto;
- finalización sin error.

Comprobar:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/move/running
```

---

## 17. Probar `dance1`, `dance2` y `dance3`

```powershell
$moveActual = Start-ReachyRecordedMove `
    -Dataset "pollen-robotics/reachy-mini-emotions-library" `
    -Move "dance1"
```

Después de finalizar:

```powershell
$moveActual = Start-ReachyRecordedMove `
    -Dataset "pollen-robotics/reachy-mini-emotions-library" `
    -Move "dance2"
```

Después:

```powershell
$moveActual = Start-ReachyRecordedMove `
    -Dataset "pollen-robotics/reachy-mini-emotions-library" `
    -Move "dance3"
```

Resultado esperado:

- movimiento en MuJoCo;
- audio por la salida predeterminada de Windows;
- UUID diferente en cada ejecución;
- sin solapamiento entre movimientos.

---

## 18. Probar Las Ketchup

```powershell
$moveActual = Start-ReachyRecordedMove `
    -Dataset "Anne-Charlotte/music" `
    -Move "las-ketchup"

$moveActual
```

Comprobar:

- movimiento;
- audio;
- sincronización;
- ausencia de nueva descarga si ya estaba en caché.

---

## 19. Probar Michael Jackson

El catálogo aportado incluye:

```text
michael-jackson-thriller
michael-jackson-thriller-official-video-shortene
```

Comprobar los nombres reales:

```powershell
$dataset = [uri]::EscapeDataString("Anne-Charlotte/music")

Invoke-RestMethod `
    "http://127.0.0.1:8000/api/move/recorded-move-datasets/list/$dataset" |
    Where-Object { $_ -match "michael|thriller" }
```

Probar la entrada principal:

```powershell
$moveActual = Start-ReachyRecordedMove `
    -Dataset "Anne-Charlotte/music" `
    -Move "michael-jackson-thriller"

$moveActual
```

---

## 20. Detener un movimiento

`POST /api/move/stop` necesita el UUID.

```powershell
$body = @{
    uuid = $moveActual.uuid
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri http://127.0.0.1:8000/api/move/stop `
    -ContentType "application/json" `
    -Body $body
```

Resultado esperado:

```text
Stopped move with UUID: ...
```

Comprobar activos:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/move/running
```

Si el movimiento ya terminó, su UUID ya no podrá cancelarse.

---

## 21. Audio reconocido por el SDK

El SDK busca un archivo de audio con el mismo nombre base que el JSON.

Ejemplo:

```text
las-ketchup.json
las-ketchup.wav
```

Extensiones admitidas por `reachy-mini 1.9.0`:

```text
.wav
.mp3
.ogg
.oga
.opus
.flac
.m4a
.aac
```

`.wav` tiene prioridad si hay varias extensiones.

Ejemplos:

```text
dance1.json + dance1.ogg
secret-dance.json + secret-dance.wav
```

La biblioteca oficial de danzas es solo movimiento.

La biblioteca oficial de emociones incluye audio asociado en la mayoría de entradas.

---

## 22. Comprobar audio en Windows

En simulación no existe el dispositivo USB de Reachy Mini. Se utiliza la salida predeterminada de Windows.

Consultar volumen:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/volume/current
```

La prueba de sonido está disponible en Swagger:

```text
POST /api/volume/test-sound
```

Si no se escucha:

- revisar la salida predeterminada;
- cerrar aplicaciones con audio exclusivo;
- comprobar `AUDCLNT_E_DEVICE_IN_USE`;
- revisar si existe el archivo de audio asociado;
- probar `dance1`, que tiene audio conocido.

---

## 23. Buscar archivos descargados

Las Ketchup y Thriller:

```powershell
Get-ChildItem `
    "$env:USERPROFILE\.cache\huggingface\hub" `
    -Recurse `
    -File `
    -ErrorAction SilentlyContinue |
    Where-Object {
        $_.BaseName -match "las-ketchup|michael-jackson-thriller"
    } |
    Select-Object FullName,Length
```

`dance1`, `dance2` y `dance3`:

```powershell
Get-ChildItem `
    "$env:USERPROFILE\.cache\huggingface\hub" `
    -Recurse `
    -File `
    -ErrorAction SilentlyContinue |
    Where-Object {
        $_.BaseName -in @("dance1","dance2","dance3")
    } |
    Select-Object FullName,Length
```

---

## 24. Validación adicional con Python

Ejecutar desde la raíz del proyecto:

```powershell
@'
from reachy_mini.motion.recorded_move import RecordedMoves

datasets = [
    "pollen-robotics/reachy-mini-dances-library",
    "pollen-robotics/reachy-mini-emotions-library",
    "Anne-Charlotte/music",
    "Anne-Charlotte/reachy-songs",
    "Anne-Charlotte/pollen-dance",
    "apirrone/marionette-moves",
    "ShivanshVikram/happy-dance",
]

for dataset in datasets:
    print()
    print("=" * 80)
    print(dataset)
    print("=" * 80)

    library = RecordedMoves(dataset)
    names = sorted(library.list_moves())

    print("Movimientos:", len(names))

    for name in names:
        move = library.get(name)
        audio = move.sound_path
        print(
            f"{name:55} "
            f"audio={'SI' if audio else 'NO'} "
            f"{audio or ''}"
        )
'@ | .\.venv\Scripts\python.exe -
```

La salida debe ser compatible con el inventario del daemon.

---

## 25. Ejemplos destacados disponibles

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

---

## 26. Qué no se hace todavía

Esta fase no:

- crea una herramienta de conversación;
- añade el catálogo a la interfaz;
- permite seleccionar mediante botones;
- cambia la política de inactividad;
- incorpora música propia;
- incluye canciones comerciales en el ZIP;
- prueba los movimientos en el robot físico.

Los datasets quedan preparados para el daemon, pero Ahootsa todavía no los ofrece como actividad.

---

## 27. Licencias y audios comerciales

La licencia del dataset y los derechos de una canción comercial pueden ser cuestiones distintas.

Durante esta fase:

```text
prueba técnica local
└── conservar los archivos en el equipo de desarrollo

ZIP distribuible
└── no incluir audio comercial sin autorización

documentación
└── registrar autor, dataset y licencia

publicación
└── revisar cada pista por separado
```

Descargar un dataset no concede automáticamente permiso para redistribuir cualquier canción incluida.

---

## 28. Problemas frecuentes

### No encuentra `.venv\Scripts\python.exe`

```powershell
cd D:\ritxi\AHOOTSA8\reachy_mini_conversation_app
```

### Error 404

Comprobar:

- nombre exacto;
- conexión;
- dataset público;
- codificación del `/`.

### Primera llamada lenta

Está descargando datos y audio. Utilizar:

```powershell
-TimeoutSec 600
```

### Nombre SHA de 40 caracteres

No debería aparecer en el endpoint. En el CSV original procedía del escaneo recursivo de la caché.

### Movimiento sin audio

Comprobar:

- mismo nombre base;
- extensión compatible;
- misma carpeta;
- que el dataset incluya realmente sonido.

### Movimiento con audio pero no se oye

Revisar:

- salida predeterminada;
- volumen;
- bloqueo exclusivo;
- archivo asociado;
- logs del daemon.

### `/api/move/stop` falla

Enviar:

```json
{
  "uuid": "UUID_DEVUELTO_AL_INICIAR"
}
```

### Dos movimientos se solapan

Esperar hasta que:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/move/running
```

devuelva una lista vacía.

---

## 29. Criterios de aceptación

- [ ] El puerto `8000` pertenece al daemon manual del proyecto.
- [ ] El daemon usa `--sim --scene minimal`.
- [ ] Swagger responde.
- [ ] Se entiende que `/api/apps/install` no instala datasets.
- [ ] Las dos bibliotecas oficiales están en caché.
- [ ] Las cinco comunitarias están en caché.
- [ ] El daemon lista los siete datasets.
- [ ] Se genera `inventario_daemon_fase4.csv`.
- [ ] Se prueba un movimiento oficial sin audio.
- [ ] Se prueba `dance1`.
- [ ] Se prueba `dance2`.
- [ ] Se prueba `dance3`.
- [ ] Se prueba `las-ketchup`.
- [ ] Se comprueba `michael-jackson-thriller`.
- [ ] Se comprueba el audio de Windows.
- [ ] Se obtiene un UUID.
- [ ] Se detiene un movimiento con `/api/move/stop`.
- [ ] No se modifica código oficial.
- [ ] No se añaden todavía actividades nuevas.
- [ ] No se incluyen audios comerciales en un ZIP distribuible.

---

## 30. Fases posteriores

```text
Fase 5
└── catálogo funcional de bailes para Ahootsa

Fase 6
└── herramienta externa para reproducir y detener bailes

Fase 7
└── actividad accesible “Vamos a bailar”

Fase 8 y siguientes
└── migración de las demás actividades de Ahootsa 7, una a una
```

La Fase 5 utilizará únicamente movimientos aprobados durante esta fase.

---

## 31. Fuentes técnicas

- SDK oficial Reachy Mini, clase `RecordedMoves` y formatos de audio.
- Router oficial del daemon para listar, reproducir y detener movimientos.
- Dataset oficial `pollen-robotics/reachy-mini-dances-library`.
- Dataset oficial `pollen-robotics/reachy-mini-emotions-library`.
- Datasets comunitarios etiquetados `reachy_mini_community_moves`.


---

## Nota de continuidad hacia la Fase 5

La Fase 4 deja los datasets descargados y validados en la caché o carpeta de
recursos del equipo.

La Fase 5 no vuelve a descargar todo el catálogo: copia únicamente los 16
movimientos seleccionados a:

```text
external_content/activities/vamos_a_bailar/dataset/data
```

Por tanto:

```text
Fase 4 = adquisición, caché, inventario y validación
Fase 5 = biblioteca local reducida dentro de Ahootsa
```
