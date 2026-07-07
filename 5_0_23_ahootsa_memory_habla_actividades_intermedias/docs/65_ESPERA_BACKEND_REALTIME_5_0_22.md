# Ahootsa 5.0.23 - esperar backend realtime conectado

## Diagnóstico

El diagnóstico muestra:

```text
/mic -> {"muted":false}
/status -> backend_connected=false
/status -> backend_connection_state="connecting"
```

Eso significa que el micro no está silenciado, pero la sesión realtime todavía no está conectada. En ese estado no escucha/responde correctamente.

## Cambios

Se añade:

```text
ESPERAR_5_BACKEND_REALTIME_LISTO.ps1
DIAGNOSTICAR_5_HUGGINGFACE_CONEXION.ps1
```

El lanzador espera a que `/status` pase a:

```text
backend_connected=true
```

antes de considerar que se puede hablar.

## Comandos

```powershell
cd D:\RITXI\5_0_23_ahootsa_espera_backend_realtime
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_SINTAXIS_PS1.ps1
powershell -ExecutionPolicy Bypass -File .\VALIDAR_5_SCRIPT_DAEMON_GENERADO.ps1
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_LOGS_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

Si se queda en connecting:

```powershell
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_5_HUGGINGFACE_CONEXION.ps1
powershell -ExecutionPolicy Bypass -File .\REINICIAR_5_SESION_CONVERSACION.ps1
```
