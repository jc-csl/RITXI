# Reparar perfil ask_ollama

## Diagnóstico detectado

Ollama funciona correctamente:

```text
/api/tags responde
/api/chat responde
ahootsa-local:latest existe
```

Pero el diagnóstico indica:

```text
No se ha encontrado ask_ollama.py copiado en perfiles de Desktop.
No se encontró tools.txt con ask_ollama.
```

Eso significa que el problema no está en Ollama.  
El problema es que la app realtime no está encontrando el perfil Ahootsa con la herramienta `ask_ollama`.

## Solución

Ejecutar con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_PERFIL_ASK_OLLAMA.ps1
```

Después volver a ejecutar:

```powershell
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_ASK_OLLAMA.ps1
```

Debe aparecer:

```text
ask_ollama.py encontrado
tools.txt con ask_ollama
```

## Prueba de voz

Prueba una orden explícita:

```text
usa la herramienta ask_ollama con este prompt: dame una actividad sencilla en español
```

Si no se crea el log:

```text
%LOCALAPPDATA%\Reachy Mini Control\ahootsa_logs\ask_ollama.log
```

entonces la IA remota sigue sin llamar a la herramienta.
