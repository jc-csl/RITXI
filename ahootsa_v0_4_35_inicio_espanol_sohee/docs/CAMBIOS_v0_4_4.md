# Cambios v0.4.35 - Safe Local Emotions Motion

- Prioridad absoluta para la carpeta local `D:\RITXI\reachy-mini-emotions-library`.
- `RecordedMoves` recibe la ruta local si existe `dance1.json` y `dance1.ogg`.
- Se conservan los nombres oficiales de la librería: `dance1`, `dance2`, `success1`, `proud1`, etc.
- Añadidas variables de entorno:
  - `AHOOTSA_EMOTIONS_LIBRARY_DIR`
  - `REACHY_MINI_EMOTIONS_LIBRARY_DIR`
- Añadidos scripts:
  - `04_configurar_libreria_emociones_local.ps1`
  - `06_comprobar_libreria_descargada.ps1`
  - `07_probar_libreria_local_con_python.ps1`
- Diagnóstico ampliado en `official_performance.py`:
  - carpeta local usada
  - fuente pasada a `RecordedMoves`
  - recuento de pares JSON+OGG
  - existencia de `dance1` y `success1`
