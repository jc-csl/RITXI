# Update 12.6.1 - Informe de sesión en PDF

## Formatos generados

Cada sesión identificada genera ahora:

```text
informe_sesion.pdf
informe_sesion.html
informe_sesion.json
transcripcion_sesion.txt
```

El JSON conserva los datos estructurados para el panel y para análisis
posteriores. El PDF es la versión legible, imprimible y compartible.

## Contenido del PDF

- identificación de la sesión;
- persona, actividad y nivel;
- fecha y duración;
- contadores registrados;
- resumen automático cuando exista;
- conversación completa;
- observaciones automáticas;
- aviso de control profesional;
- numeración de páginas.

## Tecnología

El PDF se genera localmente mediante ReportLab dentro del entorno virtual de
`ahootsa_local_server`.

No se utiliza ningún servicio remoto para crear el documento.

## Privacidad

Solo se genera PDF para sesiones identificadas. El modo anónimo no crea
informes personales.
