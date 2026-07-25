# Update 12.1 — Corrección del test PowerShell

## Problema

El script original del Update 12 estaba guardado como UTF-8 sin BOM.

Windows PowerShell 5.1 interpreta normalmente esos archivos mediante la página
de códigos de Windows. La secuencia UTF-8 de una letra acentuada en mayúscula
podía convertirse en un carácter de comillas y provocar errores falsos como:

- `Falta la cadena en el terminador`
- `Falta la llave de cierre`

El servidor y el panel no causaban ese error; el fallo ocurría durante el
análisis sintáctico del script.

## Corrección

`PROBAR_PANEL_MVP_12_1.ps1`:

- está guardado con BOM UTF-8 y finales de línea CRLF;
- utiliza únicamente caracteres ASCII en su código fuente;
- conserva `Invoke-RestMethod`, compatible con Windows PowerShell 5.1;
- evita cambiar el servidor, SQLite y el panel;
- valida la versión de servidor 0.12.0;
- preserva una sesión activa existente.

## Resultado esperado

```text
UPDATE 12.1 VALIDATED: PANEL MVP, TEMPORARY PROFILE AND TRACKING WORK.
```

El servidor continúa en versión `0.12.0`, porque este paquete solo corrige la
prueba de validación.
