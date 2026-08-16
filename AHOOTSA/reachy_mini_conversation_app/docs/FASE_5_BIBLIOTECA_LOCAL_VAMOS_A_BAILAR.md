# Ahootsa 8 — Fase 5
## Biblioteca local de la actividad «Vamos a bailar»

**Proyecto:** Ahootsa 8  
**Requisito previo:** Fase 4 completada  
**Objetivo:** copiar una selección de 16 bailes desde las descargas de la Fase 4
al interior de la aplicación, con rutas relativas y sin dependencia operativa
de la caché de Hugging Face.

---

## 1. Relación entre las fases 4 y 5

Sí: la Fase 4 ha servido principalmente para:

```text
descargar los datasets a la caché o carpeta local
+
comprobar que son compatibles con el daemon
+
inventariar movimientos y audios
+
seleccionar los recursos útiles
```

No ha sido trabajo perdido.

La Fase 4 actúa como fase de adquisición y validación. La Fase 5 utiliza esos
archivos como origen y crea una biblioteca reducida dentro de Ahootsa.

```text
Fase 4
Caché/descarga completa de varios datasets
        ↓
Fase 5
Selección local de 16 bailes dentro de la aplicación
        ↓
Fase 6
Herramientas conversacionales para listar, reproducir y detener
```

Después de completar la Fase 5, la futura actividad no necesitará consultar:

```text
C:\Users\Alumno\.cache\huggingface\hub
```

ni descargar de nuevo los datasets para reproducir estos 16 movimientos.

Conviene conservar la Fase 4 como fuente y copia de respaldo.

---

## 2. Qué se crea

Extraer el paquete de la Fase 5 en la raíz:

```text
D:\ritxi\AHOOTSA8\reachy_mini_conversation_app
```

La estructura nueva será:

```text
external_content\
└── activities\
    └── vamos_a_bailar\
        ├── actividad.json
        ├── catalogo_bailes.json
        ├── seleccion_bailes_fase5.csv
        ├── preparar_biblioteca_local.py
        ├── verificar_biblioteca_local.py
        ├── README.md
        ├── FUENTES_Y_LICENCIAS.md
        └── dataset\
            ├── README.md
            └── data\
                └── .gitkeep
```

Después de preparar la biblioteca:

```text
dataset\data\
├── 16 movimientos JSON
├── 15 audios OGG
└── 1 audio WAV
```

Total:

```text
32 recursos
```

---

## 3. Selección y orden

```text
1.  dance1
2.  dance2
3.  dance3
4.  las-ketchup
5.  michael-jackson-thriller
6.  spice-girls
7.  pharrell-williams-happy
8.  queen-we-will-rock-you
9.  the-white-stripes-seven-nation-army
10. bohemian-rhapsody
11. happy-birthday
12. harry-potter
13. star-wars
14. the-lion-king
15. titanic
16. secret-dance
```

El orden queda almacenado en:

```text
catalogo_bailes.json
```

---

## 4. Procedencia

```text
pollen-robotics/reachy-mini-emotions-library
├── dance1
├── dance2
└── dance3

Anne-Charlotte/music
├── las-ketchup
├── michael-jackson-thriller
├── spice-girls
├── pharrell-williams-happy
├── queen-we-will-rock-you
└── the-white-stripes-seven-nation-army

Anne-Charlotte/reachy-songs
├── bohemian-rhapsody
├── happy-birthday
├── harry-potter
├── star-wars
├── the-lion-king
└── titanic

apirrone/marionette-moves
└── secret-dance
```

---

## 5. Instalar los archivos de la Fase 5

Descomprimir el ZIP respetando su estructura dentro de:

```text
D:\ritxi\AHOOTSA8\reachy_mini_conversation_app
```

Comprobar:

```powershell
cd D:\ritxi\AHOOTSA8\reachy_mini_conversation_app

Get-ChildItem `
    .\external_content\activities\vamos_a_bailar
```

Deben aparecer:

```text
actividad.json
catalogo_bailes.json
preparar_biblioteca_local.py
verificar_biblioteca_local.py
```

---

## 6. Copiar los recursos desde la Fase 4

La carpeta de origen utilizada en las pruebas es:

```text
D:\ritxi\AHOOTSA8\recursos_bailes\datasets_hf
```

Ejecutar desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe `
    .\external_content\activities\vamos_a_bailar\preparar_biblioteca_local.py `
    --source-root "D:\ritxi\AHOOTSA8\recursos_bailes\datasets_hf"
```

La utilidad realiza primero una comprobación completa.

Si falta un archivo:

```text
no copia nada
+
muestra la ruta ausente
+
termina con error
```

Si todos existen:

```text
copia 16 JSON
+
copia 16 audios
+
crea inventario_recursos_locales.json
```

Resultado esperado:

```text
PREPARACIÓN COMPLETADA
Movimientos: 16
Archivos: 32
```

---

## 7. Repetir la preparación

Si los archivos locales ya son idénticos, la utilidad muestra:

```text
already_present
```

y no los duplica.

Si existe un archivo diferente, se detiene para evitar una sustitución
accidental.

Solo para sustituir conscientemente recursos locales:

```powershell
.\.venv\Scripts\python.exe `
    .\external_content\activities\vamos_a_bailar\preparar_biblioteca_local.py `
    --source-root "D:\ritxi\AHOOTSA8\recursos_bailes\datasets_hf" `
    --force
```

---

## 8. Comprobar el número de archivos

```powershell
$recursos = Get-ChildItem `
    .\external_content\activities\vamos_a_bailar\dataset\data `
    -File |
    Where-Object { $_.Name -ne ".gitkeep" }

$recursos.Count
```

Debe devolver:

```text
32
```

Comprobar por extensión:

```powershell
$recursos |
    Group-Object Extension |
    Select-Object Name,Count |
    Format-Table -AutoSize
```

Resultado esperado:

```text
.json  16
.ogg   15
.wav    1
```

---

## 9. Verificar la biblioteca con el SDK

```powershell
.\.venv\Scripts\python.exe `
    .\external_content\activities\vamos_a_bailar\verificar_biblioteca_local.py
```

La utilidad comprueba:

- los 16 JSON;
- los 16 audios;
- los tamaños;
- las huellas SHA-256;
- la carga mediante `LocalRecordedMoves`;
- la construcción de objetos oficiales `RecordedMove` del SDK;
- el registro de los 16 identificadores;
- la asociación de audio de cada movimiento;
- la duración, las marcas de tiempo y la trayectoria.

Resultado esperado:

```text
Catálogo: 16 movimientos
SDK RecordedMove: 16 movimientos construidos
RESULTADO: OK
```

Se genera:

```text
external_content\activities\vamos_a_bailar\
verificacion_biblioteca_local.json
```

---

## 10. Comprobar que la actividad usa una ruta local

El archivo:

```text
actividad.json
```

declara:

```json
{
  "runtime_dependency_on_huggingface_cache": false
}
```

La carpeta que se utilizará en ejecución será:

```text
external_content\activities\vamos_a_bailar\dataset
```

La Fase 6 calculará esta ruta a partir de la ubicación del archivo Python.

### Compatibilidad con `reachy-mini 1.9.0`

En esta versión, `RecordedMoves` recibe un nombre de dataset de Hugging Face.
No acepta una ruta local de Windows: una cadena como `D:\...\dataset` se envía
a `snapshot_download` y provoca `HFValidationError`.

Por ello, la Fase 5 incluye:

```text
local_recorded_moves.py
```

Este cargador:

1. lee los JSON locales;
2. localiza el audio con el mismo nombre;
3. construye objetos oficiales `RecordedMove`;
4. no llama a Hugging Face;
5. será reutilizable por las herramientas de la Fase 6.

No se escribirán rutas absolutas como:

```text
D:\ritxi\...
C:\Users\Alumno\...
```

en las herramientas de ejecución.

---

## 11. Qué ocurre con la caché de Windows

Tras una verificación correcta:

```text
la actividad Vamos a bailar
└── ya no necesita la caché para esos 16 bailes
```

Sin embargo, no se recomienda borrar todavía:

```text
C:\Users\Alumno\.cache\huggingface\hub
```

ni:

```text
D:\ritxi\AHOOTSA8\recursos_bailes\datasets_hf
```

porque:

- sirven como fuente de recuperación;
- contienen otros movimientos;
- pueden utilizarlos otras pruebas o herramientas oficiales;
- permiten reconstruir la biblioteca local.

---

## 12. Catálogo funcional

Cada entrada incluye:

```text
id
orden
nombre visible
nombre corto
grupo
alias de voz
dataset de origen
archivo original
archivo local
audio local
activo
```

Ejemplo:

```json
{
  "id": "las-ketchup",
  "name": "Las Ketchup",
  "short_name": "Las Ketchup",
  "group": "Música y fiesta",
  "aliases": ["aserejé", "asereje", "ketchup"],
  "order": 4,
  "enabled": true,
  "has_audio": true
}
```

Los alias se utilizarán en la Fase 6 para interpretar expresiones como:

```text
Pon el Aserejé.
Quiero bailar Thriller.
Haz el baile de Star Wars.
```

---

## 13. Seguridad prevista

`actividad.json` deja definidas estas reglas:

```text
autoplay = false
idle_autoplay = false
requires_explicit_user_choice = true
allow_stop = true
one_move_at_a_time = true
```

Por tanto, esta actividad no reutilizará el comportamiento aleatorio del
`dance` oficial durante la inactividad.

---

## 14. Qué no se modifica todavía

La Fase 5 no modifica:

```text
external_content\external_profiles\ahootsa\tools.txt
instructions.txt
greeting.txt
src\reachy_mini_conversation_app
```

Tampoco crea todavía:

```text
list_ahootsa_dances
play_ahootsa_dance
stop_ahootsa_dance
```

Estas herramientas corresponden a la Fase 6.

---

## 15. Audios comerciales

Los recursos multimedia no se incluyen en el ZIP generado por ChatGPT.

El ZIP contiene:

```text
estructura
catálogo
documentación
utilidades de copia y verificación
```

Los archivos se copian localmente desde las descargas ya realizadas en el
equipo del usuario.

Esto evita redistribuir directamente canciones comerciales.

La biblioteca local creada en el ordenador debe mantenerse para pruebas y uso
interno según las licencias y derechos aplicables.

---

## 16. Solución de problemas

### No existe la carpeta de origen

Comprobar:

```powershell
Test-Path `
    "D:\ritxi\AHOOTSA8\recursos_bailes\datasets_hf"
```

### Falta un JSON o un audio

La utilidad muestra la ruta exacta.

Volver a la Fase 4 y descargar o reconstruir el dataset correspondiente.

### Hay 31 archivos en lugar de 32

Ejecutar:

```powershell
.\.venv\Scripts\python.exe `
    .\external_content\activities\vamos_a_bailar\verificar_biblioteca_local.py
```

El informe identificará el movimiento incompleto.

### RecordedMoves no registra un movimiento

Comprobar:

- JSON válido;
- archivo dentro de `dataset/data`;
- nombre exacto;
- audio con el mismo nombre base;
- versión `reachy-mini 1.9.0`.

### Archivo local diferente

Revisar antes de usar:

```text
--force
```

La sustitución nunca se hace silenciosamente.

---

## 17. Criterios de aceptación

- [ ] La carpeta `external_content/activities/vamos_a_bailar` existe.
- [ ] `actividad.json` es válido.
- [ ] `catalogo_bailes.json` contiene 16 movimientos.
- [ ] El orden coincide con la selección acordada.
- [ ] La utilidad encuentra la carpeta de la Fase 4.
- [ ] Se copian 16 JSON.
- [ ] Se copian 15 OGG.
- [ ] Se copia 1 WAV.
- [ ] Existen 32 recursos locales.
- [ ] Se crea `inventario_recursos_locales.json`.
- [ ] `LocalRecordedMoves` registra los 16 movimientos.
- [ ] Los 16 objetos `RecordedMove` tienen audio asociado.
- [ ] Se crea `verificacion_biblioteca_local.json`.
- [ ] La verificación termina con `RESULTADO: OK`.
- [ ] No se ha modificado el código oficial.
- [ ] No se ha modificado `tools.txt`.
- [ ] La actividad no depende del Hub durante la ejecución.
- [ ] Los audios no se han incorporado al ZIP distribuido.

---

## 18. Resultado de la Fase 5

```text
Ahootsa
└── external_content
    └── activities
        └── vamos_a_bailar
            ├── catálogo de 16 bailes
            ├── dataset local
            ├── inventario con hashes
            ├── configuración de seguridad
            └── verificación mediante SDK
```

La biblioteca queda lista para que la Fase 6 añada las herramientas de
conversación y reproducción.


---

## 19. Corrección v1.1 — carga local en SDK 1.9.0

La primera versión del verificador utilizaba:

```python
RecordedMoves(str(dataset_root))
```

Esto no es válido en `reachy-mini 1.9.0`, porque `RecordedMoves` trata el
argumento como un identificador de Hugging Face.

El síntoma era:

```text
HFValidationError: Repo id must use alphanumeric chars...
```

La versión corregida incorpora:

```text
local_recorded_moves.py
```

y el verificador construye objetos oficiales:

```python
RecordedMove(move_data, sound_path=audio_path)
```

La biblioteca continúa completamente dentro de la aplicación y no depende de
la caché durante la ejecución.
