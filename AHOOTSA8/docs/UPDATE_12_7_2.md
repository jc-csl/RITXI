# Update 12.7.2 — Panel único sin caché

## Diagnóstico

La versión del servidor aparecía como 0.12.7.1, pero el navegador seguía
utilizando el HTML, CSS o JavaScript de versiones anteriores.

La evidencia funcional era:

- el diseño continuaba en una sola columna;
- los botones aparecían con estilo básico;
- `Nuevo` no abría el formulario;
- la ficha editable no se dibujaba.

## Solución definitiva

El panel se entrega ahora como un único archivo:

```text
panel_inline_12_7_2.html
```

El mismo archivo incluye:

- HTML;
- CSS;
- JavaScript.

No depende de `panel.css` ni de `panel.js`, de modo que el navegador no puede
combinar archivos de distintas versiones.

También se añade una URL completamente nueva:

```text
http://127.0.0.1:8100/panel-12-7-2
```

## Alta de personas

El formulario ya no utiliza una ventana `dialog`. Se abre dentro de la primera
columna y permite escribir, guardar o cancelar.

## Comprobación visual

La cabecera debe mostrar:

```text
Interfaz 12.7.2 activa
```

Ese texto confirma que el JavaScript integrado se ha ejecutado.
