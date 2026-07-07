# Ahootsa 5.0.21 - fluidez, herramientas reducidas y daemon sin NativeCommandError

## Diagnóstico del log

El daemon sí arranca correctamente. El mensaje `NativeCommandError` sale porque PowerShell 5 trata una línea de stderr del ejecutable nativo como error, aunque el daemon continúa y acaba mostrando:

```text
Daemon started successfully
Uvicorn running on http://127.0.0.1:8000
App ahootsa_realtime_ollama_app is running
```

También se ve que al principio `/status` y `/conversation_events` devuelven 404 hasta que la app termina de cargar. Después pasan a 200.

## Cambios

1. Daemon:
   - se elimina la ejecución `& $Daemon ... 1>> ... 2>> ...`;
   - se usa `Start-Process -NoNewWindow -PassThru`;
   - se conserva `--log-file`;
   - se evita el `NativeCommandError` falso.

2. Fluidez:
   - `tools.txt` se reduce de 33 herramientas a 17.
   - se eliminan de carga por defecto herramientas lentas o duplicadas.
   - `ask_ollama` queda fuera por defecto para no frenar la conversación.
   - sigue existiendo como archivo, pero no se carga en el perfil rápido.

3. Perfil:
   - mantiene instrucciones cortas.
   - conversación normal = respuesta directa.
   - herramientas solo cuando hagan falta.

## Comandos

```powershell
cd D:\RITXI\5_0_21_ahootsa_fluidez_tools_limpios_daemon_sin_error
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_SINTAXIS_PS1.ps1
powershell -ExecutionPolicy Bypass -File .\VALIDAR_5_SCRIPT_DAEMON_GENERADO.ps1
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_LOGS_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_5_TOOLS_FLUIDEZ.ps1
powershell -ExecutionPolicy Bypass -File .\LIMPIAR_5_VOZ_SOHEE_SIN_BOM.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_5_VOZ_SIN_BOM.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

En el arranque esperamos ver algo parecido a:

```text
Found 17 tools to load
```

Si escucha pero no contesta:

```powershell
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_5_CONVERSACION_FLUIDA.ps1
```
