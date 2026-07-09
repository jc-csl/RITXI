# Ahootsa 5.0.15 - fix parametro -NoApi duplicado

## Problema corregido

En 5.0.14 la instalacion completa llegaba bien hasta el final, pero al forzar Sohee podia aparecer:

```text
No se puede enlazar el parametro porque se ha especificado mas de una vez el parametro 'NoApi'
```

## Causa

El instalador habia acumulado dos `-NoApi` en la misma llamada a:

```powershell
FORZAR_5_VOZ_SOHEE_COMPLETA.ps1
```

## Correccion

En 5.0.15 todas las llamadas quedan normalizadas a una sola vez:

```powershell
powershell -ExecutionPolicy Bypass -File (Join-Path $Root "FORZAR_5_VOZ_SOHEE_COMPLETA.ps1") -NoApi
```

## Comandos

```powershell
cd D:\RITXI\5_0_15_ahootsa_fix_noapi_duplicado
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_SINTAXIS_PS1.ps1
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_LOGS_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

## Script extra de reparacion

```powershell
powershell -ExecutionPolicy Bypass -File .\CORREGIR_5_NOAPI_DUPLICADO.ps1
```
