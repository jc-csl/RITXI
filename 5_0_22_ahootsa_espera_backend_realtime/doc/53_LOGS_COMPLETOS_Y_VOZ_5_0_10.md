# Ahootsa 5.0.10 - logs completos y diagnostico de voz

Todos los logs nuevos se escriben SOLO en:

```text
D:\RITXI\logs
```

## Comandos recomendados

```powershell
cd D:\RITXI\5_0_10_ahootsa_logs_completos_voz_sohee
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_SINTAXIS_PS1.ps1
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_LOGS_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\LIMPIAR_5_OLLAMA_COMO_CEREBRO.ps1
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\FORZAR_5_VOZ_SOHEE_COMPLETA.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_5_LOGS_Y_VOZ.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

## Prueba para descubrir donde se guarda la voz manual

```powershell
powershell -ExecutionPolicy Bypass -File .\VOZ_1_INICIAR_MONITORIZACION_CAMBIO_MANUAL.ps1
```

Despues cambia manualmente la voz a Sohee en la interfaz y ejecuta:

```powershell
powershell -ExecutionPolicy Bypass -File .\VOZ_2_ANALIZAR_CAMBIOS_MANUALES.ps1
```

El informe se genera en:

```text
D:\RITXI\logs\voice_probe_report_*.txt
D:\RITXI\logs\voice_probe_report_*.json
```

## Que se registra

- scripts ejecutados y rutas;
- arranque/parada de daemon;
- arranque/parada de Ahootsa;
- variables de perfil, idioma, voz y modelo;
- logs JSONL de eventos Python;
- entradas a herramientas principales;
- respuesta de ask_ollama cuando se use;
- estado de voz en archivos, variables y endpoint `/voices/current`.
