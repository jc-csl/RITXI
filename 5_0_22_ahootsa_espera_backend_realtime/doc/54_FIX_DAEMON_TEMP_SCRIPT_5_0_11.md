# Ahootsa 5.0.11 - fix script temporal del daemon

Corrige el error de 5.0.10 en:

```text
D:\RITXI\logs\start_daemon_mujoco_*.ps1
```

El problema era que PowerShell expandia variables `$env:...`, `$Name`, `$script:...` demasiado pronto al generar el script temporal. Por eso aparecian lineas rotas como:

```text
param([string])
if (-not 20260702_112528)
```

## Solucion

El script temporal del daemon ahora se genera con plantilla segura y placeholders:

```text
__SESSION__
__LOGROOT__
__DAEMON__
```

Asi no se expanden variables internas antes de ejecutar el script.

## Logs

Todos los logs nuevos siguen en:

```text
D:\RITXI\logs
```

## Comandos

```powershell
cd D:\RITXI\5_0_11_ahootsa_fix_daemon_script_logs
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_SINTAXIS_PS1.ps1
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_LOGS_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\FORZAR_5_VOZ_SOHEE_COMPLETA.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_5_LOGS_Y_VOZ.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```
