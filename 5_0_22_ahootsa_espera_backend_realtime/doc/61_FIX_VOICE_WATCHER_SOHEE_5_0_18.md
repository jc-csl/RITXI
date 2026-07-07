# Ahootsa 5.0.18 - watcher de voz Sohee

## Diagnostico

Los logs muestran que la configuracion queda en Sohee, pero la sesion activa puede seguir sonando Aiden hasta pulsar manualmente Aplicar.

Tambien se ve que `/voices/current` puede estar disponible, pero la aplicacion aun no tiene lista la parte interactiva (`/conversation_events` y `/mic`) o se reinicia mientras el navegador crea la sesion. Por eso un unico `POST /voices/apply` no basta.

## Cambio

Se añade:

```text
MANTENER_5_VOZ_SOHEE_WATCHER.ps1
```

El lanzador ahora:

```text
1. Arranca daemon.
2. Arranca app.
3. Espera /status.
4. Escribe variables y voice.txt en Sohee.
5. Abre navegador.
6. Ejecuta un watcher 45 segundos aplicando Sohee repetidamente.
7. Deja otro watcher minimizado 180 segundos por si la sesion realtime se recrea.
```

El watcher genera logs pequeños en:

```text
D:\RITXI\logs\ahootsa_voice_watcher_*.log
D:\RITXI\logs\ahootsa_voice_watcher_events_*.jsonl
```

## Comandos

```powershell
cd D:\RITXI\5_0_18_ahootsa_voice_watcher_sohee
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_SINTAXIS_PS1.ps1
powershell -ExecutionPolicy Bypass -File .\VALIDAR_5_SCRIPT_DAEMON_GENERADO.ps1
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_LOGS_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

Si suena Aiden:

```powershell
powershell -ExecutionPolicy Bypass -File .\VALIDAR_5_VOZ_SESION_SOHEE.ps1
```
