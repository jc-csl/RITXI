# Ahootsa Realtime Ollama — v0.4.42

Corrección del diagnóstico de voz Sohee.

## Reparar voz

```powershell
powershell -ExecutionPolicy Bypass -File .\FORZAR_VOZ_SOHEE_TOTAL.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_VOZ_SOHEE_TOTAL.ps1
```

## Bailes del panel

El diagnóstico de bailes ya funciona:

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_BAILES_PANEL_AHOOTSA.ps1
```

Movimientos esperados:

```text
dance1
dance2
dance3
welcoming1
welcoming2
success1
electric1
```

## Instalación

```powershell
cd D:\RITXI\ahootsa_v0_4_42_fix_diagnostico_voz_bailes_ok
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```
