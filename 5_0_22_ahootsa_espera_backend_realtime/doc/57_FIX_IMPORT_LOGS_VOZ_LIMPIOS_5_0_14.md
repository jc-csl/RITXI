# Ahootsa 5.0.14 - import, logs y voz limpios

## Correcciones sobre 5.0.13

1. El instalador ya no usa `python -c` para comprobar `IMPORT_OK`.
   Ahora crea un pequeño `.py` temporal en `D:\RITXI\logs` y lo ejecuta.
   Esto evita el error:

```text
NameError: name 'IMPORT_OK' is not defined
```

2. `COMPROBAR_5_LOGS_AHOOTSA.ps1` fija tambien la variable de usuario:

```text
AHOOTSA_LOG_DIR=D:\RITXI\logs
```

3. `FORZAR_5_VOZ_SOHEE_COMPLETA.ps1` ya no prueba cuerpos invalidos.
   Usa solo el endpoint correcto:

```json
{"voice":"Sohee"}
```

4. El script temporal del daemon evita el `NativeCommandError` causado por redirigir stderr con `*>&1 | Tee-Object`.
   Ahora usa `Start-Process` con redireccion a logs stdout/stderr.

## Comandos

```powershell
cd D:\RITXI\5_0_14_ahootsa_import_logs_voz_limpios
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_SINTAXIS_PS1.ps1
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_LOGS_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

Despues:

```powershell
powershell -ExecutionPolicy Bypass -File .\RESUMIR_5_LOGS_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_5_LOGS_Y_VOZ.ps1
```
