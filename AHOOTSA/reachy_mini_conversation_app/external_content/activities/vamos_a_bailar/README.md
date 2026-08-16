# Actividad `vamos_a_bailar`

Biblioteca local preparada en la **Fase 5** de Ahootsa 8.

Esta carpeta contiene:

```text
actividad.json
catalogo_bailes.json
seleccion_bailes_fase5.csv
preparar_biblioteca_local.py
verificar_biblioteca_local.py
local_recorded_moves.py
FUENTES_Y_LICENCIAS.md
dataset/data/
```

La preparación copia 16 archivos JSON de movimiento y 16 archivos de audio
desde las descargas realizadas en la Fase 4.

La Fase 5 no añade herramientas al perfil `ahootsa` y no modifica el código
oficial. La conexión con la conversación se realizará en la Fase 6.


## Compatibilidad con SDK 1.9.0

`RecordedMoves` no admite una ruta local en esta versión: interpreta cualquier
cadena como identificador de un dataset de Hugging Face. La actividad utiliza
`LocalRecordedMoves`, que lee los archivos locales y construye los objetos
oficiales `RecordedMove` del SDK.
