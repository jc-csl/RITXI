# 01 — Instalación en un equipo nuevo

## 1. Requisitos

Sistema recomendado:

```text
Windows 10/11
PowerShell 5.1 o superior
Reachy Mini Control / Desktop Control instalado
Conexión a Internet para descargar dependencias y librería de emociones
Permisos de escritura en D:\RITXI y %LOCALAPPDATA%
```

Entorno que utiliza Ahootsa:

```text
%LOCALAPPDATA%\Reachy Mini Control\apps_venv
%LOCALAPPDATA%\Reachy Mini Control\apps_venv\Scripts\python.exe
%LOCALAPPDATA%\Reachy Mini Control\apps_venv\Scripts\reachy-mini-daemon.exe
```

Ahootsa no crea un Python propio para la app final. Se instala dentro de `apps_venv`, porque es el entorno que usa Reachy Mini Control para cargar apps.

## 2. Carpetas de trabajo

```text
D:\RITXI\7_0_19_ahootsa_base_endpoint_alias_voz_fix   versión instalable
D:\RITXI\logs                                          logs externos
D:\RITXI\fotos                                         fotos de cámara PC
D:\RITXI\reachy-mini-emotions-library                  librería local de emociones/bailes
```

Los ZIP de versión no deben incluir:

```text
docs
logs
fotos
```

## 3. Instalación de Ahootsa 7.0.19

Descomprimir el ZIP completo en:

```text
D:\RITXI\7_0_19_ahootsa_base_endpoint_alias_voz_fix
```

Ejecutar:

```powershell
cd D:\RITXI\7_0_19_ahootsa_base_endpoint_alias_voz_fix
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_7_0_19.ps1 -ForceInstall -RestartDaemon
```

El script debe:

```text
- localizar apps_venv;
- limpiar instalaciones Ahootsa antiguas/corruptas;
- evitar pip uninstall para no caer en uninstall-no-record-file;
- instalar el paquete Ahootsa con --ignore-installed;
- comprobar pygame;
- comprobar mujoco;
- comprobar opencv-python;
- comprobar entrypoint ahootsa_realtime_ollama_app;
- descargar/comprobar D:\RITXI\reachy-mini-emotions-library;
- reiniciar daemon si se usa -RestartDaemon;
- arrancar la app;
- abrir/mostrar http://127.0.0.1:7860/ahootsa.
```

## 4. Ejecución normal

Tras la primera instalación:

```powershell
cd D:\RITXI\7_0_19_ahootsa_base_endpoint_alias_voz_fix
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_7_0_19.ps1
```

## 5. Comprobaciones rápidas

Abrir:

```text
http://127.0.0.1:7860/ahootsa
http://127.0.0.1:7860/ahootsa/status
http://127.0.0.1:7860/memory/state
http://127.0.0.1:7860/memory/page?game_id=animales&reset=0
```

Si `/memory/state` o `/ahootsa/status` devuelven 404 durante unos segundos al arrancar, puede ser solo un sondeo demasiado temprano. Deben pasar a `200 OK` cuando el servidor de la app termina de inicializar.

## 6. Ollama

Modelos conocidos en el equipo de pruebas:

```text
llama3.2:3b              modelo conversacional local
nomic-embed-text:latest  embeddings, no chat principal
```

Ahootsa usa por defecto:

```text
OLLAMA_BASE=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:3b
```

Ollama se usa como extra desde `ask_ollama` o el panel. No sustituye Hugging Face Realtime.
