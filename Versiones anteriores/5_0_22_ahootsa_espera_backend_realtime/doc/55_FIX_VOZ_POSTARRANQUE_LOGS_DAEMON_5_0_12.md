# Ahootsa 5.0.12 - voz post-arranque y logs de daemon completos

## Problemas vistos en los logs de 5.0.11

1. Los logs ya se escriben correctamente en:

```text
D:\RITXI\logs
```

2. El daemon y la app se arrancan, pero el endpoint de voz se consulta demasiado pronto:

```text
voices/current -> 404 Not Found
```

3. Durante instalacion, `/voices/apply` falla porque la app 7860 todavia no esta arrancada. Eso no significa que los archivos de voz fallen; significa que la API de voz no existe aun.

## Cambios 5.0.12

- `FORZAR_5_VOZ_SOHEE_COMPLETA.ps1` ahora tiene modo `-NoApi` para instalacion.
- En el arranque, despues de iniciar Ahootsa, espera a que `http://127.0.0.1:7860` y `/status` respondan.
- Despues aplica Sohee por API con reintentos y registra `/voices/current`.
- El daemon temporal ahora guarda tambien:
  - `ahootsa_5_mujoco_daemon_console_<session>.log`
  - `ahootsa_5_mujoco_daemon_transcript_<session>.log`
- Nuevo resumen:
  - `RESUMIR_5_LOGS_AHOOTSA.ps1`

## Comandos

```powershell
cd D:\RITXI\5_0_12_ahootsa_logs_voz_postarranque
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_SINTAXIS_PS1.ps1
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_LOGS_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

Despues de probar:

```powershell
powershell -ExecutionPolicy Bypass -File .\RESUMIR_5_LOGS_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_5_LOGS_Y_VOZ.ps1
```
