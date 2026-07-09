# 01 — Instalación en un equipo nuevo

Este documento describe la instalación necesaria para usar Ahootsa en un PC nuevo, diferenciando qué aporta Reachy Mini Control, qué instala Ahootsa y qué debe estar disponible para IA local.

## 1. Requisitos previos

### Sistema

```text
Windows 10/11
PowerShell 5.1 o superior
Conexión a Internet para instalar Reachy Mini Control y descargar modelos
Permisos de usuario para escribir en D:\RITXI y %LOCALAPPDATA%
```

### Software base

Debe estar instalado **Reachy Mini Control / Desktop Control**. Ahootsa utiliza su entorno Python y su daemon:

```text
%LOCALAPPDATA%\Reachy Mini Control\apps_venv
%LOCALAPPDATA%\Reachy Mini Control\apps_venv\Scripts\python.exe
%LOCALAPPDATA%\Reachy Mini Control\apps_venv\Scripts\reachy-mini-daemon.exe
```

Ahootsa no sustituye el Desktop Control. Puede lanzarse sin abrir visualmente el Desktop, pero necesita el daemon, `apps_venv` y el sistema de apps instalado por Reachy Mini Control.

### App base

En un equipo nuevo conviene haber descargado o instalado al menos una vez la app oficial:

```text
reachy_mini_conversation_app
```

Ahootsa se apoya en su estructura de conversación, perfiles, herramientas y ejecución realtime.

## 2. Instalación de Ollama local

Ollama es necesario si se quiere usar la opción de IA local auxiliar.

Instalar Ollama desde su instalador oficial y comprobar:

```powershell
ollama list
```

Modelo conversacional recomendado:

```powershell
ollama pull llama3.2:3b
```

Comprobación esperada:

```text
NAME
llama3.2:3b
nomic-embed-text:latest
```

Importante:

```text
llama3.2:3b             -> modelo conversacional
nomic-embed-text:latest -> embeddings / búsqueda semántica, no conversación general
```

## 3. Instalar o actualizar Ahootsa

En las versiones actuales se recomienda usar una carpeta completa, por ejemplo:

```text
D:\RITXI\5_0_43_ahootsa_completa_ollama_estable
```

Ejemplo de ejecución:

```powershell
cd D:\RITXI\5_0_43_ahootsa_completa_ollama_estable
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_43.ps1 -Provider ollama -OllamaModel llama3.2:3b
```

El script debe hacer:

```text
1. Crear logs de ejecución con timestamp.
2. Localizar apps_venv de Reachy Mini Control.
3. Comprobar Python del entorno oficial.
4. Comprobar MuJoCo.
5. Comprobar Ollama y modelo configurado.
6. Aplicar instalación/parche autónomo en el paquete Ahootsa instalado.
7. Arrancar reachy-mini-daemon.exe en 127.0.0.1:8000.
8. Lanzar la app ahootsa_realtime_ollama_app por API.
9. Abrir la interfaz en 127.0.0.1:7860.
```

## 4. Instalación histórica 5.0.25 sobre la app oficial

La versión 5.0.25 instalaba Ahootsa como una capa sobre `reachy_mini_conversation_app`.

Script principal:

```text
INSTALAR_5_COMPLETO_SOBRE_CONVERSATION_APP.ps1
```

Ese instalador copiaba perfiles y herramientas a varias ubicaciones:

```text
%LOCALAPPDATA%\Reachy Mini Control\user_personalities\ahootsa_realtime_es
%LOCALAPPDATA%\Reachy Mini Control\profiles\ahootsa_realtime_es
apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es
apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\default
apps_venv\Lib\site-packages\reachy_talk_data\profiles\ahootsa_realtime_es
apps_venv\Lib\site-packages\ahootsa_realtime_ollama_desktop_app
```

También copiaba herramientas Python a ubicaciones compartidas:

```text
reachy_mini_conversation_app\tools
reachy_mini_conversation_app\external_content\external_tools
reachy_talk_data\tools
reachy_talk_data\external_content\external_tools
```

La idea era garantizar que la app oficial encontrase el perfil Ahootsa y sus herramientas aunque leyera desde distintas rutas.

## 5. Variables `.env` creadas históricamente

La 5.0.25 generaba `.env` en varias rutas con valores como:

```text
REACHY_MINI_CUSTOM_PROFILE=ahootsa_realtime_es
REACHY_MINI_PROFILE=ahootsa_realtime_es
AHOOTSA_NAME=Ahootsa
ASSISTANT_NAME=Ahootsa
ROBOT_NAME=Ahootsa
REALTIME_TRANSCRIPTION_LANGUAGE=es
AHOOTSA_VOICE=Sohee
VOICE=Sohee
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=ahootsa-local:latest
```

Problema detectado:

```text
OLLAMA_MODEL=ahootsa-local:latest
```

En el equipo actual ese modelo no existe. El modelo correcto disponible es:

```text
llama3.2:3b
```

Por eso las versiones actuales deben usar `llama3.2:3b` por defecto o detectar automáticamente modelos disponibles.

## 6. MuJoCo

Si falta MuJoCo en `apps_venv`, instalar en el Python correcto:

```powershell
$py = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv\Scripts\python.exe"
& $py -m pip install -U mujoco
```

No usar `pip install mujoco` sin ruta, porque puede instalarlo en otro Python.

## 7. Cámara del PC

La cámara oficial de Reachy/MuJoCo no es la webcam del portátil. Para cámara PC se necesita integración propia de Ahootsa.

Prueba:

```text
http://127.0.0.1:7860/camera/page
```

Si no funciona, revisar:

```text
Permisos de cámara en Windows
Permiso de cámara del navegador/WebView
Uso de localhost
Que no haya otra app usando la webcam
```

## 8. Checklist de instalación nueva

```text
[ ] Instalar Reachy Mini Control.
[ ] Descargar/instalar reachy_mini_conversation_app desde Desktop Control.
[ ] Comprobar que existe apps_venv.
[ ] Instalar Ollama.
[ ] Ejecutar ollama pull llama3.2:3b.
[ ] Descomprimir versión completa Ahootsa actual en D:\RITXI.
[ ] Ejecutar LANZAR_AHOOTSA_5_0_xx.ps1.
[ ] Comprobar logs en D:\RITXI\logs.
[ ] Probar conversación principal.
[ ] Probar “Preguntar IA local”.
[ ] Probar juego Memory.
[ ] Probar cámara PC.
[ ] Probar movimientos/emociones.
```
