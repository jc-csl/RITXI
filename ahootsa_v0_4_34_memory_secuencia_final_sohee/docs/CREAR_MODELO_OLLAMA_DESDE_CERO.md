# Crear modelo local ahootsa-local:latest con Ollama

Este documento resume solo la creación del modelo local.

## 1. Descargar modelo base

```powershell
ollama pull hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest
```

Comprobar:

```powershell
ollama list
```

## 2. Crear carpeta del Modelfile

```powershell
$ModelDir = "$env:LOCALAPPDATA\Ahootsa\ollama_ahootsa"
New-Item -ItemType Directory -Force -Path $ModelDir | Out-Null
$Modelfile = Join-Path $ModelDir "Modelfile"
```

## 3. Crear Modelfile

```powershell
@'
FROM hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest

PARAMETER temperature 0.6
PARAMETER top_p 0.9
PARAMETER num_ctx 2048

SYSTEM """
Eres Ahootsa, un asistente educativo amable, claro y paciente.
Respondes siempre en español.
Usas frases cortas.
Das instrucciones sencillas.
Eres positivo y animas al usuario.
No dices que eres ChatGPT.
No controlas directamente el robot.
Si te consultan desde Reachy Mini, ayudas con explicaciones, ideas, actividades y reformulaciones sencillas.
"""
'@ | Set-Content -Encoding UTF8 $Modelfile
```

## 4. Crear modelo

```powershell
ollama create ahootsa-local -f $Modelfile
```

## 5. Comprobar

```powershell
ollama list
ollama run ahootsa-local
```

## 6. Probar API

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:11434/api/chat" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{
    "model": "ahootsa-local:latest",
    "stream": false,
    "messages": [
      {
        "role": "user",
        "content": "Hola Ahootsa, ¿me respondes en español?"
      }
    ]
  }'
```
