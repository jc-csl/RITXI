# 13 — Fix rutas voz Sohee v0.4.45

## Problema

El script `FORZAR_VOZ_SOHEE_TOTAL.ps1` de la versión anterior incluía un carácter de control en rutas con `ahootsa` / `reachy`. En PowerShell aparecía como:

```text
Caracteres no válidos en la ruta de acceso
```

Por eso no podía escribir `voice.txt` en todos los perfiles.

## Corrección

```text
- Se reconstruye FORZAR_VOZ_SOHEE_TOTAL.ps1 sin caracteres de control.
- Se usa Join-Many para construir rutas por segmentos.
- Se corrige DIAGNOSTICAR_BAILES_PANEL_AHOOTSA.ps1.
- Se revisan todos los .ps1 para asegurar que no quedan caracteres de control.
```

## Reparación

```powershell
powershell -ExecutionPolicy Bypass -File .\FORZAR_VOZ_SOHEE_TOTAL.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_VOZ_SOHEE_TOTAL.ps1
```
