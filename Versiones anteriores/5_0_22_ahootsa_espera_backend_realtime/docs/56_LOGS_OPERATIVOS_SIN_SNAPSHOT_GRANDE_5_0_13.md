# Ahootsa 5.0.13 - logs operativos sin snapshot grande

## Cambio principal

Se elimina la generacion de `voice_probe_before_*.json` grande.

A partir de esta version, la prueba de voz manual usa modo ligero:

```text
voice_probe_marker_light_*.json
voice_probe_report_light_*.txt
voice_probe_report_light_*.json
```

No se guarda un listado completo de todos los archivos. Solo se guarda un marcador temporal pequeño, y despues se buscan archivos candidatos de voz/configuracion modificados desde ese instante.

## Logs adecuados al funcionamiento

Los logs operativos normales se mantienen:

```text
D:\RITXI\logs\ahootsa_ps_*.log
D:\RITXI\logs\ahootsa_ps_events_*.jsonl
D:\RITXI\logs\ahootsa_events_*.jsonl
D:\RITXI\logs\ahootsa_5_mujoco_daemon_*.log
D:\RITXI\logs\ahootsa_5_mujoco_daemon_console_*.log
D:\RITXI\logs\ahootsa_5_mujoco_daemon_transcript_*.log
```

## Comandos normales

```powershell
cd D:\RITXI\5_0_13_ahootsa_logs_operativos_sin_snapshot_grande
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_SINTAXIS_PS1.ps1
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_LOGS_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

## Prueba de voz manual, solo si hace falta

```powershell
powershell -ExecutionPolicy Bypass -File .\VOZ_1_INICIAR_MONITORIZACION_CAMBIO_MANUAL.ps1
```

Cambias la voz manualmente a Sohee y luego:

```powershell
powershell -ExecutionPolicy Bypass -File .\VOZ_2_ANALIZAR_CAMBIOS_MANUALES.ps1
```

## Si hay snapshots antiguos grandes

`COMPROBAR_5_LOGS_AHOOTSA.ps1` los avisa. Se pueden borrar si ya no hacen falta para diagnostico historico.
