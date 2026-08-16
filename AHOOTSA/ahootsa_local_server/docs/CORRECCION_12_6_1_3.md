# Corrección 12.6.1.3

## Diagnóstico

La instalación con uv terminó correctamente:

```text
reportlab==4.5.1
pillow==12.3.0
charset-normalizer==3.4.9
```

El aviso sobre hardlinks no es un error. uv utilizó copia de archivos y completó
la instalación.

La verificación falló por el comportamiento de salida de las funciones de
PowerShell. La función emitía al mismo tiempo:

1. la salida estándar `REPORTLAB_OK 4.5.1`;
2. el entero `0`.

La variable recibía un `System.Object[]`, no un entero. Por ello la condición
`$VerifyExit -ne 0` resultaba verdadera.

## Solución

Toda la salida del programa nativo se envía ahora a `Out-Host`. El único objeto
devuelto por la función es el código de salida entero.

```powershell
& $FilePath @Arguments 2>&1 | Out-Host
$ExitCode = [int]$LASTEXITCODE
return [int]$ExitCode
```

Así se mantiene visible la información de uv y Python, pero las comparaciones se
realizan siempre con un entero.
