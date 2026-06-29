# v0.4.21 — Recuperar respuesta sobre IA local

## Problema

Tras cambiar la voz, la app podía responder:

```text
no tengo conectada una IA local
```

aunque Ollama sí estaba funcionando.

Los logs confirman que:

```text
OLLAMA_BASE_URL = http://127.0.0.1:11434
OLLAMA_MODEL = ahootsa-local:latest
```

y que `ask_ollama` funcionó anteriormente.

El fallo no era la conexión. Era que la IA realtime respondía desde su memoria sin llamar a la herramienta `ask_ollama`.

## Corrección

v0.4.21 refuerza las instrucciones del perfil:

```text
- si el usuario dice IA local, Ollama, modelo local o ahootsa-local, debe llamar a ask_ollama;
- si pregunta si hay IA local conectada, debe comprobarlo con ask_ollama;
- no debe decir que no hay IA local conectada salvo que ask_ollama devuelva error;
- añade la pregunta de estado como caso explícito.
```

También se refuerza la descripción de la herramienta `ask_ollama`.

## Prueba

Con Desktop cerrado, instala:

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```

Después prueba desde la app:

```text
comprueba la IA local con ask_ollama
```

o:

```text
¿tienes conectada una IA local?
```

Debe llamar a `ask_ollama` y crear una entrada nueva en:

```text
%LOCALAPPDATA%\Reachy Mini Control\ahootsa_logs\ask_ollama.log
```

## Script de comprobación

```powershell
powershell -ExecutionPolicy Bypass -File .\PROBAR_IA_LOCAL_AHOOTSA.ps1
```
