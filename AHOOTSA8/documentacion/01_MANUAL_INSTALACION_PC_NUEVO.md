# Manual de instalación de AHOOTSA8 en un PC nuevo

**Versión de referencia:** 0.12.8.2  
**Fecha:** 5 de agosto de 2026  
**Sistema:** Windows 10 u 11 de 64 bits  
**Ruta de trabajo recomendada:** `D:\RITXI\AHOOTSA8`

## 1. Resultado esperado

Al terminar la instalación deben existir dos entornos Python independientes:

```text
D:\RITXI\AHOOTSA8\
├── reachy_mini_conversation_app\.venv
├── ahootsa_local_server\.venv
├── INICIAR_AHOOTSA_ANONIMO.ps1
├── INICIAR_AHOOTSA_SESION.ps1
├── FINALIZAR_SESION_AHOOTSA.ps1
├── COMPROBAR_AHOOTSA.ps1
└── LIMPIAR_PROCESOS_AHOOTSA.ps1
```

La aplicación de conversación utiliza su propio entorno. El servidor local
utiliza otro entorno. No deben mezclarse.

## 2. Requisitos previos

- Windows 10/11 de 64 bits.
- Conexión a Internet durante la instalación y para el backend desplegado.
- Unidad `D:` disponible, o adaptación consciente de todas las rutas.
- Micrófono y altavoces configurados como dispositivos predeterminados.
- PowerShell 5.1 o PowerShell 7.
- Git para Windows.
- `uv`.
- Python 3.12 administrado por `uv`.

Durante las pruebas con MuJoCo debe permanecer cerrado Reachy Mini Desktop
Control para evitar que otro daemon ocupe el puerto 8000.

## 3. Instalar Git

Opción mediante `winget`:

```powershell
winget install --id Git.Git -e
```

Cerrar y volver a abrir PowerShell. Comprobar:

```powershell
git --version
```

Recomendación para rutas largas:

```powershell
git config --global core.longpaths true
```

## 4. Instalar uv

Instalador oficial:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Cerrar y volver a abrir PowerShell. Comprobar:

```powershell
uv --version
```

## 5. Instalar Python 3.12 con uv

No es obligatorio instalar Python desde python.org. La opción recomendada es:

```powershell
uv python install 3.12
uv python list
```

Comprobar:

```powershell
uv run --python 3.12 python --version
```

Resultado esperado:

```text
Python 3.12.x
```

## 6. Descargar el proyecto desde Git

En un PC nuevo, `D:\RITXI` debe estar vacío antes de clonar:

```powershell
New-Item -ItemType Directory -Force D:\RITXI
cd D:\RITXI
git clone https://github.com/jc-csl/RITXI.git .
```

Este comando deja directamente:

```text
D:\RITXI\AHOOTSA8
```

Comprobar:

```powershell
Test-Path D:\RITXI\AHOOTSA8\reachy_mini_conversation_app
Test-Path D:\RITXI\AHOOTSA8\ahootsa_local_server
Test-Path D:\RITXI\AHOOTSA8\INICIAR_AHOOTSA_ANONIMO.ps1
Test-Path D:\RITXI\AHOOTSA8\INICIAR_AHOOTSA_SESION.ps1
```

Los cuatro resultados deben ser `True`.

> No ejecutar las carpetas `AHOOTSA_UPDATE_*` en una instalación nueva. El
> repositorio ya contiene el estado final. Esas carpetas son trazabilidad de
> actualizaciones anteriores.

## 7. Instalar la aplicación de conversación

```powershell
cd D:\RITXI\AHOOTSA8\reachy_mini_conversation_app
uv venv --python 3.12 .venv
uv sync --frozen
```

`uv sync --frozen` instala el conjunto exacto de `uv.lock`.

### El SDK no se instala globalmente

El proyecto declara:

```toml
"reachy-mini[mujoco]==1.9.0"
```

Por tanto, `uv sync --frozen` instala dentro de `.venv`:

- Reachy Mini Conversation App 0.9.0;
- Reachy Mini SDK 1.9.0;
- MuJoCo 3.3.0;
- librerías de baile y herramientas;
- dependencias del backend de conversación.

No ejecutar un `pip install reachy-mini` global adicional. Podría introducir
otra versión y crear conflictos.

### Comprobación de versiones

```powershell
& .\.venv\Scripts\python.exe -c "from importlib.metadata import version; print('App:', version('reachy-mini-conversation-app')); print('SDK:', version('reachy-mini')); print('MuJoCo:', version('mujoco'))"
```

Resultado de referencia:

```text
App: 0.9.0
SDK: 1.9.0
MuJoCo: 3.3.0
```

Comprobar ejecutables:

```powershell
Test-Path .\.venv\Scripts\reachy-mini-daemon.exe
Test-Path .\.venv\Scripts\reachy-mini-conversation-app.exe
```

## 8. Instalar el servidor local

```powershell
cd D:\RITXI\AHOOTSA8\ahootsa_local_server
uv venv --python 3.12 .venv
uv pip install --python .\.venv\Scripts\python.exe -r .\requirements.txt
uv pip install --python .\.venv\Scripts\python.exe "reportlab>=4,<5"
```

La instalación explícita de ReportLab es necesaria porque el generador de PDF
lo importa, aunque la versión actual de `requirements.txt` solo enumera
FastAPI, Uvicorn y SQLAlchemy.

Comprobar:

```powershell
& .\.venv\Scripts\python.exe -c "import fastapi, uvicorn, sqlalchemy, reportlab; print('SERVIDOR_OK', reportlab.Version)"
```

## 9. Configurar PowerShell

Los scripts están firmados únicamente como archivos locales. Para la terminal
actual:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

No es necesario cambiar permanentemente la política del equipo.

## 10. Revisar la configuración de la aplicación

```powershell
cd D:\RITXI\AHOOTSA8\reachy_mini_conversation_app
Get-Content .\.env
```

Deben existir estas líneas:

```env
REALTIME_TRANSCRIPTION_LANGUAGE="es"
HF_REALTIME_CONNECTION_MODE="deployed"
HF_TOKEN=
REACHY_MINI_CUSTOM_PROFILE=ahootsa
REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY=./external_content/external_profiles
REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY=./external_content/external_tools
AUTOLOAD_EXTERNAL_TOOLS=false
```

El modo `deployed` utiliza el backend gestionado por la aplicación y no exige
una clave API propia. `HF_TOKEN` puede permanecer vacío salvo que un recurso
específico de Hugging Face lo requiera.

## 11. Revisar el servidor local

```powershell
cd D:\RITXI\AHOOTSA8\ahootsa_local_server
Get-Content .\config\panel_config.json
```

Valores principales:

```text
servidor local       127.0.0.1:8100
daemon               127.0.0.1:8000
Conversation App     127.0.0.1:7860
perfil de sesión     ahootsa_session
base de datos        data\ahootsa.db
```

## 12. Primera validación sin iniciar una sesión

```powershell
cd D:\RITXI\AHOOTSA8
.\COMPROBAR_AHOOTSA.ps1
```

Inicialmente los tres servicios deben aparecer detenidos.

## 13. Primera prueba anónima

```powershell
.\INICIAR_AHOOTSA_ANONIMO.ps1 -DebugMode
```

Debe ocurrir:

```text
8000 activo
8100 detenido
7860 activo
perfil ahootsa
```

Abrir:

```text
http://127.0.0.1:7860
```

Finalizar:

```powershell
.\FINALIZAR_SESION_AHOOTSA.ps1 -DetenerTodo
```

## 14. Primera prueba con sesión local

```powershell
.\INICIAR_AHOOTSA_SESION.ps1
```

Abrir o comprobar:

```text
http://127.0.0.1:8100/panel-12-7-2
```

En el panel:

1. crear o seleccionar una persona;
2. elegir actividad y nivel;
3. pulsar `Preparar`;
4. pulsar `Iniciar conversación`;
5. conversar;
6. finalizar desde el panel o ejecutar:

```powershell
.\FINALIZAR_SESION_AHOOTSA.ps1
```

El informe debe aparecer dentro de:

```text
D:\RITXI\AHOOTSA8\ahootsa_local_server\data\sessions\session_XXXXXX
```

Archivos esperados:

```text
informe_sesion.pdf
informe_sesion.html
informe_sesion.json
transcripcion_sesion.txt
conversation_app.log
session_context.json
session_status.json
summary.json
```

## 15. Criterio de aceptación

La instalación queda validada cuando:

- `COMPROBAR_AHOOTSA.ps1` identifica correctamente los servicios;
- MuJoCo aparece y el daemon escucha en 8000;
- la interfaz de conversación escucha en 7860;
- el modo anónimo no abre 8100;
- el modo sesión abre 8100;
- se puede crear una persona;
- se puede preparar una sesión;
- al finalizar se genera un PDF;
- `LIMPIAR_PROCESOS_AHOOTSA.ps1` libera los tres puertos.

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
