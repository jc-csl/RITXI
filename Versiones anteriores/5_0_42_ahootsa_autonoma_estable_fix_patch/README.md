# Ahootsa 5.0.42 autónoma estable

Versión completa para conservar como carpeta única de trabajo.

Corrige el fallo de la 5.0.41 en `tools/patch_ahootsa_5_0_41.py`, donde una cadena HTML cerraba por error el bloque Python y provocaba `SyntaxError` alrededor de la línea 199.

## Ejecutar con Ollama

Desde esta carpeta:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_42.ps1 -Provider ollama -OllamaModel llama3.2:3b
```

O con el CMD:

```cmd
LANZAR_AHOOTSA_OLLAMA_5_0_42.cmd
```

## Ejecutar con Hugging Face local

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_42.ps1 -Provider hf_local -HFModelPath "D:\RITXI\models\TU_MODELO"
```

## Comprobar

```powershell
powershell -ExecutionPolicy Bypass -File .\1_COMPROBAR_5_0_42.ps1
```

## Cámara PC

Cuando la app esté lanzada:

```text
http://127.0.0.1:7860/camera/page
```

Las fotos se guardan en:

```text
D:\RITXI\logs\camera
```

## Sobre Desktop Control

La carpeta 5.0.42 ya no depende de carpetas antiguas de Ahootsa, pero sí necesita que exista el entorno oficial de Reachy Mini Control:

```text
%LOCALAPPDATA%\Reachy Mini Control\apps_venv
```

También necesita que el paquete/app `ahootsa_realtime_ollama_desktop_app` esté instalado o registrado en ese entorno, porque el daemon arranca la app por nombre:

```text
ahootsa_realtime_ollama_app
```

En un PC nuevo, primero debe estar instalado Reachy Mini Control/Desktop Control y la app Ahootsa/Reachy conversation app al menos una vez. Después, esta carpeta 5.0.42 aplica los parches autónomos y ya no necesita las carpetas 5.0.25-5.0.41.
