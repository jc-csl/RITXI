# Update 11.1 — Compatibilidad PowerShell

## Motivo

El test del Update 11 utilizaba `System.Net.Http.HttpClient`. Ese tipo no estaba
disponible en el entorno Windows PowerShell 5.1 utilizado para validar Ahootsa.

## Solución

El test vuelve a utilizar `Invoke-RestMethod`, compatible con Windows
PowerShell 5.1 y PowerShell 7.

## Validaciones incluidas

1. Versión 0.11.1.
2. Existencia de sesión activa.
3. Construcción del contexto unificado.
4. Catálogo con al menos dos actividades.
5. Presencia de `emotions` y `preferences`.
6. Creación física del snapshot.
7. Lectura y validación del JSON guardado.

## UTF-8

La prueba funcional no depende de cómo la consola de PowerShell represente los
acentos. Los snapshots se leen expresamente mediante `Get-Content -Encoding
UTF8`.

## Cambios funcionales

Ninguno. Este paquete es una actualización correctiva y de consolidación.
