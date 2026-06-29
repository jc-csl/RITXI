# v0.4.14 — Perfil Ahootsa forzado al arranque

## Problema detectado

El diagnóstico ya confirma:

```text
- Ollama funciona.
- ahootsa-local:latest existe.
- /api/chat responde.
- ask_ollama.py y tools.txt existen en user_personalities.
- Pero no existe ask_ollama.log.
```

Esto indica que la herramienta no se está ejecutando. La causa más probable es que la app oficial no esté arrancando con el perfil Ahootsa y, por tanto, cargue otro `tools.txt`.

La app oficial carga herramientas desde el perfil al arrancar. Cambiar la personalidad desde la UI puede actualizar instrucciones, pero las herramientas no se recargan en caliente.

## Corrección v0.4.14

Esta versión hace tres cosas:

```text
1. Fuerza REACHY_MINI_CUSTOM_PROFILE=ahootsa_realtime_es en el proceso de Ahootsa.
2. Copia el perfil Ahootsa a user_personalities, profiles y al directorio de perfiles del paquete oficial.
3. Mantiene intactas las herramientas originales y añade solo ask_ollama.
```

No modifica perfiles oficiales existentes. Solo añade una carpeta nueva:

```text
profiles/ahootsa_realtime_es
```

## Instalación

Con Reachy Mini Desktop cerrado:

```powershell
cd D:\RITXI\ahootsa_v0_4_14_perfil_forzado_ask_ollama
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
powershell -ExecutionPolicy Bypass -File .\REPARAR_PERFIL_ASK_OLLAMA.ps1
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_ASK_OLLAMA.ps1
```

Después abre Desktop y arranca Ahootsa.

## Prueba por voz

```text
usa la herramienta ask_ollama con este prompt: dame una actividad sencilla en español
```

Debe crearse:

```text
%LOCALAPPDATA%\Reachy Mini Control\ahootsa_logs\ask_ollama.log
```
