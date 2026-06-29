# v0.4.18 — Cámara PC en modo simulación

## Objetivo

Añadir cámara en simulación sin alterar el código original de la app oficial.

La herramienta oficial `camera` se mantiene intacta.  
La nueva herramienta añadida es:

```text
camera_pc
```

## Qué hace camera_pc

```text
- Usa la webcam del ordenador.
- Está pensada para modo SIM / mockup-sim.
- Guarda la foto en:
  %LOCALAPPDATA%\Reachy Mini Control\ahootsa_captures
- Escribe log en:
  %LOCALAPPDATA%\Reachy Mini Control\ahootsa_logs\camera_pc.log
```

## Qué no hace

```text
- No modifica reachy_mini_conversation_app.
- No sustituye la cámara real del robot.
- No hace visión artificial.
- No describe automáticamente la imagen.
```

## Instalación

Con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```

El instalador ejecuta también:

```powershell
INSTALAR_CAMARA_PC.ps1
```

para instalar/verificar `opencv-python`.

## Prueba rápida

```powershell
powershell -ExecutionPolicy Bypass -File .\PROBAR_CAMARA_PC.ps1
```

Debe mostrar:

```text
OK
ruta_de_la_foto.jpg
```

## Prueba por voz

Con Ahootsa arrancado desde Desktop:

```text
haz una foto con la cámara del ordenador
```

o:

```text
estamos en simulación, usa camera_pc para hacer una foto
```

## Nota importante

Si el usuario pide "haz una foto" estando en SIM, el perfil indica que debe usarse `camera_pc`.
Si se está usando el robot físico real, debe mantenerse la herramienta oficial `camera`.
