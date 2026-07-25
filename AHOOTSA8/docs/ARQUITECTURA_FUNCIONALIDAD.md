# ARQUITECTURA Y FUNCIONALIDAD — AHOOTSA 0.12.7.2

## Arquitectura principal

La aplicación oficial `reachy_mini_conversation_app` mantiene la conversación,
el audio, el modelo realtime, la voz y los movimientos.

El servidor `ahootsa_local_server` mantiene:

- personas y perfiles;
- actividades y niveles;
- sesiones y eventos;
- seguimiento profesional;
- informes PDF, HTML, JSON y texto.

No se modifica el directorio oficial `src`.

## Panel profesional

URL recomendada:

```text
http://127.0.0.1:8100/panel-12-7-2
```

Archivo:

```text
app/static/panel/panel_inline_12_7_2.html
```

El CSS y el JavaScript se integran dentro de ese HTML. Esto elimina la
dependencia de caché entre varios archivos.

## Distribución

En escritorio:

1. persona y ficha editable;
2. actividad, preparación y seguimiento;
3. finalización, informe y recuperación.

Cada columna dispone de desplazamiento interno. La página principal no se
desplaza verticalmente.

## Gestión de personas

- nueva persona mediante formulario visible;
- usuario de ejemplo separado;
- edición mediante doble clic;
- botones pequeños Guardar, Vaciar y Cancelar;
- borrado seguro;
- conservación del historial.

## Sesiones

- preparación por persona, actividad y nivel;
- inicio de Conversation App;
- marcas profesionales;
- cierre completo desde el panel;
- recuperación de bloqueos;
- generación de informes.
