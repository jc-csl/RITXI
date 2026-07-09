# Ahootsa 5.0.32 — reparación del lanzador y logs limpios

Esta versión corrige el fallo introducido al parchear los logs en 5.0.31:

```text
LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1: [int]$Port = 8000,
La expresión de asignación no es válida.
InvalidLeftHandSide
```

## Causa

En PowerShell, el bloque `param(...)` debe aparecer al principio efectivo del archivo. La versión 5.0.31 podía insertar código antes de `param(...)`, y por eso PowerShell interpretaba líneas como:

```powershell
[int]$Port = 8000,
[string]$HostAddress = "127.0.0.1",
```

como si fueran código normal, no parámetros.

## Qué hace la 5.0.32

- Elimina bloques inyectados que puedan haber quedado antes de `param(...)`.
- No vuelve a insertar código ejecutable antes de `param(...)`.
- Repara el lanzador original `LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1`.
- Mantiene un timestamp nuevo por ejecución mediante `$env:AHOOTSA_SESSION`.
- Reconstruye `ESPERAR_5_BACKEND_REALTIME_LISTO.ps1` con una versión segura.
- Protege `Add-Content` contra bloqueos de `pantalla.log`.
- Mantiene el audio único de Ahootsa, bloqueando `speechSynthesis` del navegador/Windows.
- Mantiene los endpoints de compatibilidad `/status`, `/mic`, `/voices/current`, `/voices`.

## Ejecutar

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_0_32_AHOOTSA_MUJOCO_WEB.ps1
```

Si falta MuJoCo:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_0_32_AHOOTSA_MUJOCO_WEB.ps1 -InstallMujoco
```

## Si vuelve a fallar el lanzador

Ejecuta:

```powershell
powershell -ExecutionPolicy Bypass -File .\2_DIAGNOSTICO_LANZADOR_5_0_32.ps1
```

y copia las primeras 80 líneas que muestre.

## Resumen limpio de la última ejecución

Después de reproducir un problema:

```powershell
powershell -ExecutionPolicy Bypass -File .\1_RESUMIR_ULTIMA_EJECUCION_5_0_32.ps1
```

Archivo útil para enviar:

```text
D:\RITXI\logs\ULTIMA_EJECUCION_AHOOTSA_CORRECCION.log
```
