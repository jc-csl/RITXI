# Ahootsa 5.0.19 - Sohee sin BOM

## Diagnostico

En el watcher de 5.0.18 aparece:

```text
current_body={"voice":"ï»¿Sohee"}
```

Ese prefijo `ï»¿` es un BOM UTF-8. La interfaz puede mostrar Sohee, pero el backend realtime puede no reconocer exactamente la voz y caer en la voz por defecto: Aiden.

## Correccion

5.0.19 reescribe todos los `voice.txt` como UTF-8 sin BOM usando:

```powershell
[System.Text.UTF8Encoding]($false)
```

Nuevos scripts:

```text
LIMPIAR_5_VOZ_SOHEE_SIN_BOM.ps1
test\DIAGNOSTICAR_5_VOZ_SIN_BOM.ps1
```

El instalador, el lanzador y el watcher limpian los `voice.txt` antes de abrir la app/navegador y durante la vigilancia de voz.

## Comandos

```powershell
cd D:\RITXI\5_0_19_ahootsa_voz_sohee_sin_bom
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_SINTAXIS_PS1.ps1
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_LOGS_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\LIMPIAR_5_VOZ_SOHEE_SIN_BOM.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_5_VOZ_SIN_BOM.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

Despues del arranque:

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_5_VOZ_SIN_BOM.ps1
```

Debe verse:

```text
has_bom=False
value=[Sohee]
API voices/current = {"voice":"Sohee"}
```
