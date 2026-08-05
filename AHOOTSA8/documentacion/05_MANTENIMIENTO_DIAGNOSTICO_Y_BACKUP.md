# Mantenimiento, diagnóstico y copias de seguridad

## 1. Diagnóstico habitual

```powershell
cd D:\RITXI\AHOOTSA8
.\COMPROBAR_AHOOTSA.ps1
```

Muestra:

- estado de 8000, 8100 y 7860;
- PID de cada servicio;
- modo detectado;
- versión del servidor local;
- sesión activa;
- existencia de `active_session.json`;
- scripts operativos.

## 2. Liberar procesos

```powershell
.\LIMPIAR_PROCESOS_AHOOTSA.ps1
```

Este script cierra procesos y libera puertos. No debe borrar usuarios,
sesiones, informes ni la base SQLite.

Comprobación manual:

```powershell
Get-NetTCPConnection `
    -LocalPort 8000,8100,7860 `
    -State Listen `
    -ErrorAction SilentlyContinue
```

## 3. Problemas frecuentes

### El puerto 8000 está ocupado

Causa frecuente: Reachy Mini Desktop Control u otro daemon.

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen |
    Select-Object LocalAddress,LocalPort,OwningProcess

Get-Process -Id <PID>
```

Cerrar conscientemente el proceso o ejecutar la limpieza.

### El panel no abre

```powershell
Test-NetConnection 127.0.0.1 -Port 8100
Invoke-RestMethod http://127.0.0.1:8100/health
```

Si falla, revisar el `.venv` del servidor y `scripts\iniciar_servidor_local.ps1`.

### No se crea PDF

```powershell
& D:\RITXI\AHOOTSA8\ahootsa_local_server\.venv\Scripts\python.exe `
    -c "import reportlab; print(reportlab.Version)"
```

Si falla:

```powershell
uv pip install `
    --python D:\RITXI\AHOOTSA8\ahootsa_local_server\.venv\Scripts\python.exe `
    "reportlab>=4,<5"
```

### No se puede preparar una nueva sesión

Comprobar:

```powershell
.\COMPROBAR_AHOOTSA.ps1
Test-Path .\ahootsa_local_server\data\active_session.json
```

Finalizar la sesión anterior:

```powershell
.\FINALIZAR_SESION_AHOOTSA.ps1
```

Después, si quedan procesos:

```powershell
.\LIMPIAR_PROCESOS_AHOOTSA.ps1
```

### La aplicación no escucha bien

1. comprobar dispositivos predeterminados de Windows;
2. cerrar dispositivos Bluetooth no utilizados;
3. reducir ruido ambiental;
4. revisar que el micrófono no esté silenciado en 7860;
5. no confundir transcripciones parciales con el turno final;
6. revisar `conversation_app.log`.

## 4. Copia de seguridad

Detener todo:

```powershell
.\FINALIZAR_SESION_AHOOTSA.ps1 -DetenerTodo
```

Crear copia:

```powershell
$fecha = Get-Date -Format "yyyyMMdd_HHmmss"
$destino = "D:\RITXI\BACKUPS\AHOOTSA8_$fecha"

New-Item -ItemType Directory -Force $destino

Copy-Item `
    D:\RITXI\AHOOTSA8\ahootsa_local_server\data `
    "$destino\data" `
    -Recurse -Force

Copy-Item `
    D:\RITXI\AHOOTSA8\reachy_mini_conversation_app\external_content `
    "$destino\external_content" `
    -Recurse -Force

Copy-Item `
    D:\RITXI\AHOOTSA8\documentacion `
    "$destino\documentacion" `
    -Recurse -Force
```

Elementos prioritarios:

```text
ahootsa.db
data\sessions
external_profiles
profile_defaults
external_tools
activities
documentacion
```

Los `.venv` no necesitan incluirse en la copia: pueden regenerarse con `uv`.

## 5. Actualizar desde Git

No ejecutar `git pull` durante una sesión.

```powershell
cd D:\RITXI
git status
```

Antes de actualizar:

1. detener todos los servicios;
2. realizar copia de `data`, `external_content` y `documentacion`;
3. comprobar cambios locales;
4. usar:

```powershell
git pull --ff-only
```

Si Git informa de conflictos, no forzar la actualización. Resolverlos primero.

## 6. Regenerar entornos

### Aplicación

```powershell
cd D:\RITXI\AHOOTSA8\reachy_mini_conversation_app
Remove-Item .\.venv -Recurse -Force
uv venv --python 3.12 .venv
uv sync --frozen
```

### Servidor

```powershell
cd D:\RITXI\AHOOTSA8\ahootsa_local_server
Remove-Item .\.venv -Recurse -Force
uv venv --python 3.12 .venv
uv pip install --python .\.venv\Scripts\python.exe -r requirements.txt
uv pip install --python .\.venv\Scripts\python.exe "reportlab>=4,<5"
```

## 7. Archivos históricos

Las carpetas `AHOOTSA_UPDATE_*`, los backups y los documentos de fases antiguas
sirven como trazabilidad. No deben ser el punto de entrada operativo de una
instalación actual.

La fuente operativa es:

```text
scripts de la raíz
scripts internos
ahootsa_local_server
reachy_mini_conversation_app
documentacion actual
```

## Fuentes verificadas

Documentación revisada el 5 de agosto de 2026:

- Repositorio del proyecto: https://github.com/jc-csl/RITXI
- Carpeta actual `AHOOTSA8`: https://github.com/jc-csl/RITXI/tree/main/AHOOTSA8
- Aplicación oficial incluida en el proyecto:
  https://github.com/jc-csl/RITXI/tree/main/AHOOTSA8/reachy_mini_conversation_app
- Aplicación oficial de Pollen Robotics:
  https://github.com/pollen-robotics/reachy_mini_conversation_app
- SDK Reachy Mini:
  https://github.com/pollen-robotics/reachy_mini
- Instalación oficial de `uv`:
  https://docs.astral.sh/uv/getting-started/installation/

La instalación descrita utiliza las versiones fijadas por el repositorio
AHOOTSA8. No debe sustituirse automáticamente por la última versión del
repositorio oficial de Pollen Robotics.
