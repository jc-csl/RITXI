# v5.9.22 · Edición real de configuración y carácter

Cambios:
- `Configuración avanzada` ya no es solo lectura.
- Se puede seleccionar archivo, editar y guardar desde el navegador.
- Nuevo endpoint:
  - `POST /api/config/file?path=...`
- Se mantiene una lista blanca de archivos permitidos.
- `Editar carácter de Ritxi` carga el perfil actual antes de abrir.
- `Guardar carácter` muestra confirmación y guarda en `profiles/characters/*.json`.
- Nuevo botón: `Editar JSON del carácter`.
