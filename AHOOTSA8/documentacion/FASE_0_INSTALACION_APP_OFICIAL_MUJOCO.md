# Ahootsa 8 — Fase 0  
## Instalación de la aplicación oficial con entorno virtual propio y simulación MuJoCo

**Documento:** Fase 0  
**Proyecto:** Ahootsa 8  
**Sistema descrito:** Windows 10/11 + PowerShell  
**Aplicación base:** `reachy_mini_conversation_app` oficial, versión `0.9.0`  
**SDK:** `reachy-mini 1.9.0`  
**MuJoCo:** `3.3.0`

---

## 1. Objetivo de la fase

El objetivo de esta fase es instalar y ejecutar la aplicación oficial de conversación de Reachy Mini en un equipo nuevo, sin incorporar todavía ninguna funcionalidad específica de Ahootsa.

Al finalizar deben funcionar conjuntamente:

```text
Fase 0
├── aplicación oficial sin modificaciones funcionales
├── entorno virtual propio
├── SDK 1.9.0
├── MuJoCo 3.3.0
├── daemon ejecutado manualmente desde .venv
├── simulación 3D visible
└── interfaz oficial ejecutada manualmente desde .venv
```

La aplicación y el daemon se ejecutarán desde el mismo entorno virtual del proyecto. En esta ruta de desarrollo no se utilizará el entorno Python interno de Reachy Mini Desktop Control.

---

## 2. Hoja de ruta general

```text
Fase 0
├── aplicación oficial sin modificaciones funcionales
├── entorno virtual propio
├── SDK 1.9.0
├── MuJoCo 3.3.0
├── daemon ejecutado manualmente desde .venv
├── simulación 3D visible
└── interfaz oficial ejecutada manualmente desde .venv

Fase 1
└── creación del perfil externo Ahootsa

Fase 2
└── configuración de personalidad, idioma y voz

Fase 3
└── comprobación de herramientas oficiales

Fase 4
└── incorporación progresiva de funciones de Ahootsa
```

---

## 3. Principios de trabajo

1. Se parte de la aplicación oficial.
2. No se reutiliza el antiguo fork local como base.
3. No se crean scripts automáticos de instalación o arranque.
4. Todos los comandos se ejecutan manualmente en PowerShell.
5. Se crea un `.venv` propio dentro del proyecto.
6. El daemon y la aplicación se ejecutan desde ese mismo `.venv`.
7. Desktop Control debe permanecer cerrado durante estas pruebas para evitar un segundo daemon en el puerto `8000`.
8. En la Fase 0 no se modifica el comportamiento conversacional ni la interfaz.
9. El único ajuste del proyecto es la dependencia necesaria para activar MuJoCo.
10. Cada comprobación debe superarse antes de continuar con la siguiente fase.

---

## 4. Estructura final esperada

```text
D:\ritxi\AHOOTSA8\
└── reachy_mini_conversation_app\
    ├── .venv\
    ├── .env.example
    ├── README.md
    ├── pyproject.toml
    ├── uv.lock
    ├── external_content\
    ├── profiles\
    ├── src\
    └── docs\
```

### Elementos principales

| Elemento | Función |
|---|---|
| `.venv` | Entorno Python aislado de Ahootsa 8. |
| `pyproject.toml` | Dependencias y configuración del proyecto. |
| `uv.lock` | Versiones resueltas por `uv`. No se edita manualmente. |
| `profiles` | Perfiles internos oficiales. |
| `external_content` | Perfiles y herramientas externas. Se utilizará desde la Fase 1. |
| `src` | Código oficial de la aplicación. No se modifica en la Fase 0. |
| `docs` | Documentación del proyecto. |

---

## 5. Requisitos previos del equipo nuevo

### 5.1. Sistema

- Windows 10 u 11.
- Conexión a Internet durante la instalación.
- PowerShell.
- Micrófono y altavoces o auriculares configurados como dispositivos predeterminados.
- Tarjeta gráfica compatible con OpenGL para mostrar la ventana 3D de MuJoCo.

> El SDK de Reachy Mini admite Windows. El README de esta versión de la aplicación de conversación advierte que su soporte en Windows puede ser experimental; por eso conviene mantener activado `--debug` durante las primeras pruebas.

### 5.2. Instalar `uv`

Opción mediante `winget`:

```powershell
winget install --id=astral-sh.uv -e
```

Opción mediante el instalador oficial de PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Cerrar y abrir PowerShell y comprobar:

```powershell
uv --version
```

### 5.3. Instalar Python 3.12 mediante `uv`

```powershell
uv python install 3.12
```

Comprobar:

```powershell
uv python list
```

Debe aparecer una instalación de Python `3.12`.

---

## 6. Preparar la aplicación oficial desde el ZIP

Para reproducir esta instalación se utiliza el ZIP oficial de referencia.

1. Copiar `reachy_mini_conversation_app.zip` al equipo nuevo.
2. Crear la carpeta de trabajo:

```powershell
New-Item -ItemType Directory -Force D:\ritxi\AHOOTSA8
```

3. Extraer el ZIP dentro de esa carpeta.
4. Confirmar que el resultado es:

```text
D:\ritxi\AHOOTSA8\reachy_mini_conversation_app
```

5. Entrar en la raíz del proyecto:

```powershell
cd D:\ritxi\AHOOTSA8\reachy_mini_conversation_app
```

### Comprobaciones del código base

Comprobar la versión declarada de la aplicación:

```powershell
Select-String -Path .\pyproject.toml -Pattern '^version ='
```

Resultado esperado:

```text
version = "0.9.0"
```

Comprobar que existen los archivos y carpetas principales:

```powershell
Test-Path .\pyproject.toml
Test-Path .\uv.lock
Test-Path .\README.md
Test-Path .\src
Test-Path .\profiles
Test-Path .\external_content
```

Todos deben devolver:

```text
True
```

---

## 7. Crear el entorno virtual propio

Desde la raíz del proyecto:

```powershell
cd D:\ritxi\AHOOTSA8\reachy_mini_conversation_app
```

Crear `.venv` con Python 3.12:

```powershell
uv venv --python 3.12 .venv
```

Activar:

```powershell
.\.venv\Scripts\Activate.ps1
```

El prompt debe comenzar con:

```text
(.venv)
```

Si PowerShell bloquea temporalmente la activación:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

Esta modificación solo afecta a la terminal actual.

### Comprobaciones del entorno

```powershell
python --version
```

Resultado esperado:

```text
Python 3.12.x
```

```powershell
python -c "import sys; print(sys.executable)"
```

La ruta debe ser:

```text
D:\ritxi\AHOOTSA8\reachy_mini_conversation_app\.venv\Scripts\python.exe
```

No debe apuntar al Python interno de Desktop Control ni a otro proyecto.

---

## 8. Activar la dependencia de MuJoCo

La aplicación oficial declara inicialmente:

```toml
"reachy-mini>=1.9.0",
```

Para disponer de la simulación 3D, editar manualmente:

```text
D:\ritxi\AHOOTSA8\reachy_mini_conversation_app\pyproject.toml
```

Sustituir únicamente esa línea por:

```toml
"reachy-mini[mujoco]==1.9.0",
```

No modificar las líneas:

```toml
"reachy-mini" = false
"reachy-mini-dances-library" = false
"reachy-mini-toolbox" = false
```

Estas líneas pertenecen a la configuración de `uv` y no representan dependencias duplicadas.

### Instalar y actualizar el bloqueo

Con `.venv` activado:

```powershell
uv sync
```

No utilizar `--frozen` en esta primera sincronización, porque `pyproject.toml` acaba de cambiar y `uv.lock` debe incorporar MuJoCo.

### Comprobaciones de dependencias

Comprobar la declaración:

```powershell
Select-String -Path .\pyproject.toml -Pattern "reachy-mini"
```

Debe aparecer:

```text
"reachy-mini[mujoco]==1.9.0",
```

Comprobar que MuJoCo está en el bloqueo:

```powershell
Select-String -Path .\uv.lock -Pattern 'name = "mujoco"'
```

Comprobar las versiones instaladas:

```powershell
.\.venv\Scripts\python.exe -c "from importlib.metadata import version; print('Conversation App:', version('reachy-mini-conversation-app')); print('SDK:', version('reachy-mini')); print('MuJoCo:', version('mujoco'))"
```

Resultado esperado:

```text
Conversation App: 0.9.0
SDK: 1.9.0
MuJoCo: 3.3.0
```

Comprobar la importación:

```powershell
.\.venv\Scripts\python.exe -c "import mujoco; print('MuJoCo:', mujoco.__version__)"
```

Resultado esperado:

```text
MuJoCo: 3.3.0
```

Si aparece:

```text
ModuleNotFoundError: No module named 'mujoco'
```

ejecutar de nuevo:

```powershell
uv sync
```

Como corrección excepcional:

```powershell
uv pip install --python .\.venv\Scripts\python.exe "reachy-mini[mujoco]==1.9.0"
```

y repetir la comprobación.

---

## 9. Preparar el arranque manual

Para trabajar serán necesarias dos terminales:

```text
Terminal 1
└── daemon Reachy Mini + MuJoCo

Terminal 2
└── aplicación oficial de conversación
```

Desktop Control debe estar completamente cerrado.

### Comprobar que el puerto 8000 está libre

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
```

Si no devuelve nada, el puerto está libre.

Si aparece un proceso escuchando:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen |
    Select-Object LocalAddress,LocalPort,OwningProcess
```

Consultar el proceso:

```powershell
Get-Process -Id <PID>
```

No continuar hasta saber qué proceso está usando el puerto.

---

## 10. Arrancar el daemon con MuJoCo visible

### Terminal 1

```powershell
cd D:\ritxi\AHOOTSA8\reachy_mini_conversation_app
.\.venv\Scripts\Activate.ps1
```

Arranque recomendado:

```powershell
.\.venv\Scripts\reachy-mini-daemon.exe --sim --scene minimal
```

También puede usarse:

```powershell
reachy-mini-daemon --sim --scene minimal
```

### Escenas disponibles

| Escena | Contenido |
|---|---|
| `empty` | Solo el robot. Es la escena predeterminada. |
| `minimal` | Robot, mesa y varios objetos. |

Para mostrar únicamente Reachy:

```powershell
reachy-mini-daemon --sim --scene empty
```

### Opciones que no se utilizan en esta fase

```text
--mockup-sim
```

Ejecuta una simulación ligera sin MuJoCo visible.

```text
--headless
```

Ejecuta MuJoCo sin ventana gráfica.

```text
--no-media
```

Desactiva los servicios multimedia; no interesa para comprobar conversación y audio.

```text
--desktop-app-daemon
```

Está relacionado con la gestión desde Desktop Control y no es necesario en este flujo manual.

### Resultado esperado

1. Se abre una ventana 3D de MuJoCo.
2. Se muestra el modelo de Reachy Mini.
3. El daemon permanece ejecutándose en la terminal.
4. El servicio queda disponible en `localhost:8000`.

### Comprobaciones del daemon

En otra terminal:

```powershell
Test-NetConnection 127.0.0.1 -Port 8000
```

Resultado esperado:

```text
TcpTestSucceeded : True
```

Comprobar la documentación REST:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/docs -UseBasicParsing |
    Select-Object StatusCode
```

Resultado esperado:

```text
StatusCode
----------
200
```

También puede abrirse en el navegador:

```text
http://127.0.0.1:8000/docs
```

---

## 11. Arrancar la aplicación oficial

Mantener abierta la Terminal 1.

### Terminal 2

```powershell
cd D:\ritxi\AHOOTSA8\reachy_mini_conversation_app
.\.venv\Scripts\Activate.ps1
```

Comprobar el ejecutable:

```powershell
Get-Command reachy-mini-conversation-app
```

La ruta debe apuntar a:

```text
D:\ritxi\AHOOTSA8\reachy_mini_conversation_app\.venv\Scripts\reachy-mini-conversation-app.exe
```

Arrancar la aplicación con interfaz y logs detallados:

```powershell
.\.venv\Scripts\reachy-mini-conversation-app.exe --ui --debug
```

O, con el entorno activado:

```powershell
reachy-mini-conversation-app --ui --debug
```

Abrir:

```text
http://127.0.0.1:7860
```

### Comprobaciones de la aplicación

```powershell
Test-NetConnection 127.0.0.1 -Port 7860
```

Resultado esperado:

```text
TcpTestSucceeded : True
```

```powershell
Invoke-WebRequest http://127.0.0.1:7860/ -UseBasicParsing |
    Select-Object StatusCode
```

Resultado esperado:

```text
StatusCode
----------
200
```

---

## 12. FastAPI y documentación de todas las rutas

Al arrancar la aplicación con:

```powershell
reachy-mini-conversation-app --ui --debug
```

se ejecuta una aplicación FastAPI en el puerto `7860`.

### 12.1. Documentación de la aplicación de conversación

| Recurso | Dirección |
|---|---|
| Interfaz principal | `http://127.0.0.1:7860/` |
| Swagger UI | `http://127.0.0.1:7860/docs` |
| ReDoc | `http://127.0.0.1:7860/redoc` |
| Especificación OpenAPI | `http://127.0.0.1:7860/openapi.json` |

La dirección principal para consultar y probar las opciones es:

```text
http://127.0.0.1:7860/docs
```

Swagger permite:

- consultar los endpoints disponibles;
- ver parámetros y cuerpos JSON;
- ejecutar peticiones desde el navegador;
- comprobar perfiles, voces, micrófono, conexión y estado;
- conocer la respuesta prevista de cada operación.

### 12.2. Documentación del daemon

El daemon utiliza otra aplicación FastAPI independiente en el puerto `8000`.

| Recurso | Dirección |
|---|---|
| Swagger UI del daemon | `http://127.0.0.1:8000/docs` |
| ReDoc del daemon | `http://127.0.0.1:8000/redoc` |
| Especificación OpenAPI | `http://127.0.0.1:8000/openapi.json` |

Diferencia:

```text
Puerto 7860
└── aplicación de conversación, perfiles, voces, micrófono y backend

Puerto 8000
└── daemon, robot, simulación, movimientos, audio, cámara y hardware
```

### 12.3. Comprobar que Swagger está disponible

```powershell
Invoke-WebRequest http://127.0.0.1:7860/docs -UseBasicParsing |
    Select-Object StatusCode

Invoke-WebRequest http://127.0.0.1:8000/docs -UseBasicParsing |
    Select-Object StatusCode
```

Ambas consultas deben devolver:

```text
StatusCode
----------
200
```

### 12.4. Mostrar automáticamente todas las rutas de la aplicación

```powershell
$apiApp = Invoke-RestMethod http://127.0.0.1:7860/openapi.json

$apiApp.paths.PSObject.Properties | ForEach-Object {
    $ruta = $_.Name
    $_.Value.PSObject.Properties.Name |
        Where-Object {
            $_ -in @("get", "post", "put", "patch", "delete")
        } |
        ForEach-Object {
            "{0,-7} {1}" -f $_.ToUpper(), $ruta
        }
} | Sort-Object
```

Este comando obtiene las rutas de la versión realmente ejecutada. Es preferible a mantener una lista manual que podría quedar desactualizada.

### 12.5. Mostrar automáticamente todas las rutas del daemon

```powershell
$apiDaemon = Invoke-RestMethod http://127.0.0.1:8000/openapi.json

$apiDaemon.paths.PSObject.Properties | ForEach-Object {
    $ruta = $_.Name
    $_.Value.PSObject.Properties.Name |
        Where-Object {
            $_ -in @("get", "post", "put", "patch", "delete")
        } |
        ForEach-Object {
            "{0,-7} {1}" -f $_.ToUpper(), $ruta
        }
} | Sort-Object
```

### 12.6. Comprobación mínima de OpenAPI

```powershell
$appOpenApi = Invoke-RestMethod http://127.0.0.1:7860/openapi.json
$daemonOpenApi = Invoke-RestMethod http://127.0.0.1:8000/openapi.json

@{
    App_titulo = $appOpenApi.info.title
    App_rutas = @($appOpenApi.paths.PSObject.Properties).Count
    Daemon_titulo = $daemonOpenApi.info.title
    Daemon_rutas = @($daemonOpenApi.paths.PSObject.Properties).Count
}
```

Los dos recuentos deben ser superiores a cero.

---

## 13. Prueba funcional de la Fase 0

Mantener el perfil oficial predeterminado y comprobar:

### 13.1. Interfaz

- La web carga sin errores.
- Aparecen los controles de personalidad, micrófono y configuración.
- La sesión no se cierra inmediatamente.
- No aparecen errores de conexión al daemon.

### 13.2. Audio

- El navegador o la aplicación solicita acceso al micrófono.
- El micrófono predeterminado recibe voz.
- La respuesta se reproduce por el dispositivo de salida predeterminado.
- No hay dos aplicaciones hablando simultáneamente.

### 13.3. Conversación

Probar:

```text
Hello, can you hear me?
```

Después:

```text
Please speak Spanish.
```

Comprobar:

- reconocimiento de voz;
- respuesta del backend;
- reproducción de audio;
- continuidad de la conversación.

### 13.4. Movimiento en MuJoCo

Durante la conversación comprobar:

- movimiento de cabeza;
- movimiento de antenas;
- cambios de postura o emociones, cuando proceda;
- sincronización entre la aplicación y el robot 3D.

### 13.5. Prueba sin cámara, solo para diagnóstico

Si la aplicación falla por la cámara, detener únicamente la aplicación con `Ctrl + C` y ejecutar:

```powershell
reachy-mini-conversation-app --ui --no-camera --debug
```

La ventana de MuJoCo debe permanecer abierta. Esta prueba permite separar un problema de cámara de un problema general de aplicación.

---

## 14. Comprobaciones finales de la Fase 0

Ejecutar:

```powershell
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
```

Debe apuntar a `.venv`.

```powershell
.\.venv\Scripts\python.exe -c "from importlib.metadata import version; print(version('reachy-mini-conversation-app')); print(version('reachy-mini')); print(version('mujoco'))"
```

Debe devolver:

```text
0.9.0
1.9.0
3.3.0
```

```powershell
Test-NetConnection 127.0.0.1 -Port 8000
Test-NetConnection 127.0.0.1 -Port 7860
```

Ambos deben devolver:

```text
TcpTestSucceeded : True
```

Comprobar manualmente que los únicos archivos de configuración actualizados en esta fase son:

```text
pyproject.toml
uv.lock
```

No se modifica el contenido funcional de:

```text
src\
profiles\
static\
external_content\
```

---

## 15. Criterios de aceptación

La Fase 0 se considera terminada cuando se cumplen todos los puntos:

- [ ] Python 3.12 está instalado.
- [ ] `uv` funciona.
- [ ] La aplicación oficial está en `D:\ritxi\AHOOTSA8\reachy_mini_conversation_app`.
- [ ] Existe `.venv` dentro del proyecto.
- [ ] El Python activo pertenece a ese `.venv`.
- [ ] La aplicación es la versión `0.9.0`.
- [ ] El SDK es la versión `1.9.0`.
- [ ] MuJoCo es la versión `3.3.0`.
- [ ] El daemon se inicia manualmente desde `.venv`.
- [ ] La ventana 3D de MuJoCo es visible.
- [ ] El puerto `8000` responde.
- [ ] La aplicación se inicia manualmente desde `.venv`.
- [ ] La interfaz en `http://127.0.0.1:7860` responde.
- [ ] Swagger de la aplicación responde en el puerto `7860`.
- [ ] Swagger del daemon responde en el puerto `8000`.
- [ ] Se escucha al usuario.
- [ ] Se reproduce la respuesta.
- [ ] Los movimientos aparecen en MuJoCo.
- [ ] No se ha modificado ninguna funcionalidad de la aplicación oficial.

---

## 16. Cierre correcto

### Detener la aplicación

En la Terminal 2:

```text
Ctrl + C
```

### Detener el daemon

En la Terminal 1:

```text
Ctrl + C
```

Comprobar que los puertos quedan libres:

```powershell
Get-NetTCPConnection -LocalPort 8000,7860 -State Listen -ErrorAction SilentlyContinue
```

No debe devolver procesos.

---

## 17. Problemas frecuentes

### `ModuleNotFoundError: No module named 'mujoco'`

Comprobar:

```powershell
Select-String -Path .\pyproject.toml -Pattern "reachy-mini"
```

Debe contener:

```toml
"reachy-mini[mujoco]==1.9.0",
```

Después:

```powershell
uv sync
```

### `TimeoutError` al arrancar la aplicación

El daemon no está disponible.

```powershell
Test-NetConnection 127.0.0.1 -Port 8000
```

### El puerto 8000 ya está ocupado

Cerrar Desktop Control y localizar el proceso:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen
```

### No se abre la ventana 3D

Comprobar que se usa:

```powershell
reachy-mini-daemon --sim
```

y no:

```powershell
reachy-mini-daemon --mockup-sim
```

Comprobar también:

```powershell
python -c "import mujoco; print(mujoco.__version__)"
```

### La aplicación usa otro Python

Comprobar:

```powershell
Get-Command python
Get-Command reachy-mini-conversation-app
```

Ambos deben apuntar a `.venv\Scripts`.

---

## 18. Archivos modificados en esta fase

### Modificados

```text
pyproject.toml
uv.lock
```

### Creado automáticamente

```text
.venv\
```

### No modificados

```text
.env.example
README.md
profiles\
external_content\
src\
static\
```

---

## 19. Referencias oficiales

- README incluido en `reachy_mini_conversation_app 0.9.0`.
- Documentación oficial del SDK Reachy Mini: instalación.
- Documentación oficial de simulación con MuJoCo.
- Documentación oficial de `uv`.
- Código oficial de `reachy_mini_conversation_app` incluido en el ZIP de referencia.
- SDK oficial `reachy-mini` instalado mediante las dependencias del proyecto.

---

## 20. Siguiente fase

Cuando todas las comprobaciones anteriores sean correctas, continuar con:

```text
Fase 1
└── creación del perfil externo Ahootsa
```

No se debe comenzar la Fase 1 mientras la aplicación oficial, el audio, el daemon y MuJoCo no funcionen correctamente.
