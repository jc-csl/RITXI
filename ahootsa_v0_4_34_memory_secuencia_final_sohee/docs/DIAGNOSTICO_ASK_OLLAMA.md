# Diagnóstico de ask_ollama

## Problema

Si al decir:

```text
usa la IA local
consulta Ollama
```

Ahootsa no responde, hay que distinguir dos casos:

```text
1. Ollama no responde.
2. Ollama sí responde, pero la IA remota no llama a la herramienta ask_ollama.
```

El aviso:

```text
reachy_mini.media.central_signaling_relay - ConnectionRefusedError
```

no es la API de Ollama. Ollama usa:

```text
http://127.0.0.1:11434
```

Ese aviso pertenece al sistema de media/signaling de Reachy Mini.

## Prueba rápida

Desde la raíz de Ahootsa:

```powershell
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_ASK_OLLAMA.ps1
```

## Interpretación

Si `/api/chat` funciona pero no existe `ask_ollama.log`, significa:

```text
La IA remota no ha llamado a ask_ollama.
```

En ese caso prueba una orden más explícita:

```text
usa la herramienta ask_ollama con este prompt: dame una actividad sencilla en español
```

Si existe `ask_ollama.log`, copia las últimas líneas.

## Log

El log queda en:

```powershell
%LOCALAPPDATA%\Reachy Mini Control\ahootsa_logs\ask_ollama.log
```
