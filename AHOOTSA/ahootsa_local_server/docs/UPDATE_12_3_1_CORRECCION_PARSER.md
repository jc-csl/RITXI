# Update 12.3.1 — Corrección del parser de Windows PowerShell

## Problema

Windows PowerShell interpreta una expresión como:

```powershell
"$ServiceName: texto"
```

como si se intentase acceder a una variable o unidad llamada
`$ServiceName:`. Por eso aparecía:

```text
La referencia de variable no es válida.
El carácter ':' no va seguido de un carácter de nombre de variable válido.
```

El mismo problema afectaba a `$processId:`.

## Corrección

Las cadenas se han sustituido por expresiones seguras con el operador de
formato:

```powershell
"{0}: port {1} is free." -f $ServiceName, $Port
```

Esto es compatible con Windows PowerShell 5.1 y PowerShell 7.

## Alcance

Solo se modifica:

```text
D:\RITXI\AHOOTSA8\scripts\ahootsa_process_utils.ps1
```

No se modifica:

- servidor Python;
- SQLite;
- perfiles;
- `.env`;
- aplicación oficial;
- `src/`;
- lanzadores 1, 2 y 3.

## Nuevas pruebas

- `COMPROBAR_SINTAXIS_POWERSHELL_12_3_1.ps1`
- `PROBAR_UTILIDAD_PROCESOS_12_3_1.ps1`
