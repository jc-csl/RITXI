# Corrección Ahootsa 5.0.33 — `param(...)` del lanzador PowerShell

## Problema corregido

El error detectado era:

```text
LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1: 20 Carácter: 18
[int]$Port = 8000,
La expresión de asignación no es válida.
InvalidLeftHandSide
```

Este error no pertenece al backend Python ni a MuJoCo. Es un error de sintaxis PowerShell producido porque el bloque `param(...)` del lanzador dejó de estar al principio del archivo.

## Por qué ocurre

PowerShell solo reconoce parámetros de script si el bloque `param(...)` aparece antes de instrucciones ejecutables. Una versión anterior insertó código para preparar `AHOOTSA_SESSION` antes de `param(...)` en algunos casos. Eso rompió el parseo.

## Estrategia de reparación

La 5.0.33 aplica un parche conservador:

1. Busca `LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1` en la carpeta 5.0.25.
2. Elimina bloques inyectados de 5.0.31/5.0.33 si aparecen antes de `param(...)`.
3. Si encuentra `param(...)` más abajo, lo recoloca como primer bloque efectivo.
4. Reemplaza asignaciones directas a `$Session` por una expresión compatible:

```powershell
$Session = if ($env:AHOOTSA_SESSION) { $env:AHOOTSA_SESSION } else { Get-Date -Format "yyyyMMdd_HHmmss" }
```

5. El wrapper `LANZAR_5_0_33_AHOOTSA_MUJOCO_WEB.ps1` crea un timestamp nuevo en `$env:AHOOTSA_SESSION` antes de llamar al lanzador original.

## Resultado esperado

Cada ejecución crea logs con un identificador nuevo:

```text
D:\RITXI\logs\ahootsa5_YYYYMMDD_HHMMSS_pantalla.log
D:\RITXI\logs\ahootsa5_YYYYMMDD_HHMMSS_runtime.log
D:\RITXI\logs\ahootsa5_YYYYMMDD_HHMMSS_eventos.jsonl
```

El último resumen queda en:

```text
D:\RITXI\logs\ULTIMA_EJECUCION_AHOOTSA_CORRECCION.log
```
