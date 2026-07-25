# Prueba 12.4.2.3 — Corrección del listado API en PowerShell

## Resultado ya confirmado

La ejecución anterior confirmó:

```text
SQLite contiene los 9 eventos en la sesión 10.
```

Por tanto, el registro de la conversación en SQLite funciona.

## Causa del nuevo error

En Windows PowerShell 5.1, `ConvertFrom-Json` puede devolver un array JSON como
un único objeto `System.Object[]`. En ese caso:

```powershell
$_.id
```

produce otro array con todos los identificadores. La conversión:

```powershell
[int]$_.id
```

intenta convertir `System.Object[]` en un único entero y falla.

## Corrección

La función `Get-AhootsaEventIds` aplana de forma explícita:

- un único evento;
- una lista normal;
- una lista `Object[]` anidada.

Después convierte cada `id` por separado.

## Alcance

Solo se añade una prueba corregida. No se modifica:

- servidor Python;
- SQLite;
- perfiles;
- `.env`;
- aplicación oficial.
