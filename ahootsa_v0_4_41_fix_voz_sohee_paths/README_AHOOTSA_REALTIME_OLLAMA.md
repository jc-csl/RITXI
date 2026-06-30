# Ahootsa Realtime Ollama — v0.4.41

Corrige el fallo de la v0.4.40 en `FORZAR_VOZ_SOHEE_TOTAL.ps1`:

```text
Caracteres no válidos en la ruta de acceso
```

## Instalación

```powershell
cd D:\RITXI\ahootsa_v0_4_41_fix_voz_sohee_paths
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```

## Reparar voz Sohee

```powershell
powershell -ExecutionPolicy Bypass -File .\FORZAR_VOZ_SOHEE_TOTAL.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_VOZ_SOHEE_TOTAL.ps1
```

## Bailes panel

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_BAILES_PANEL_AHOOTSA.ps1
```
