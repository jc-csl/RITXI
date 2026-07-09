# Ahootsa 5.0.16 - fix redireccion daemon consola/stderr

## Problema corregido

En 5.0.14/5.0.15 podia aparecer en el script temporal:

```text
Start-Process : "RedirectStandardOutput" y "RedirectStandardError" son iguales
```

La causa era que los placeholders:

```text
__DAEMONCONSOLELOG__
__DAEMONTRANSCRIPTLOG__
```

no quedaban sustituidos en `start_daemon_mujoco_*.ps1`. Entonces stdout y stderr acababan apuntando al mismo valor.

## Solucion 5.0.16

El script temporal del daemon ya no usa `Start-Process -RedirectStandardOutput -RedirectStandardError`.

Ahora ejecuta el daemon directamente dentro de la ventana temporal y redirige de forma separada:

```powershell
& $Daemon @ArgsList 1>> $DaemonConsoleLog 2>> $DaemonErrorLog
```

Y crea estos logs en:

```text
D:\RITXI\logs
```

```text
ahootsa_5_mujoco_daemon_<session>.log
ahootsa_5_mujoco_daemon_console_<session>.log
ahootsa_5_mujoco_daemon_stderr_<session>.log
ahootsa_5_mujoco_daemon_transcript_<session>.log
```

## Comandos recomendados

```powershell
cd D:\RITXI\5_0_16_ahootsa_fix_daemon_console_redirect
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_SINTAXIS_PS1.ps1
powershell -ExecutionPolicy Bypass -File .\VALIDAR_5_SCRIPT_DAEMON_GENERADO.ps1
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_LOGS_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```
