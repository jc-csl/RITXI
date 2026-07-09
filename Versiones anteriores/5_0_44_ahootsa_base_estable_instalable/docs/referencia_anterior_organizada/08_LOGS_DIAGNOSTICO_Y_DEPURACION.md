# 08 — Logs, diagnóstico y depuración

## 1. Ubicación de logs

```text
D:\RITXI\logs
```

Archivos por ejecución:

```text
ahootsa5_YYYYMMDD_HHMMSS_pantalla.log
ahootsa5_YYYYMMDD_HHMMSS_runtime.log
ahootsa5_YYYYMMDD_HHMMSS_eventos.jsonl
```

Otros:

```text
ULTIMA_EJECUCION_AHOOTSA_INFO.txt
ULTIMA_EJECUCION_AHOOTSA_CORRECCION.log
camera/
```

## 2. Qué debe aparecer en un arranque correcto

```text
IMPORT_OK ...
MUJOCO_OK ...
Daemon disponible en http://127.0.0.1:8000
POST /api/apps/start-app/ahootsa_realtime_ollama_app -> OK
/status en 7860 -> HTTP 200
Interfaz: http://127.0.0.1:7860
```

## 3. Diagnóstico de Ollama

Comprobar modelos:

```powershell
ollama list
```

Comprobar API:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

Prueba directa:

```powershell
$body = @{
  model = "llama3.2:3b"
  prompt = "Di hola en una frase."
  stream = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/generate" -Method Post -ContentType "application/json" -Body $body
```

Errores típicos:

```text
HTTP 404 + model=ahootsa-local:latest -> modelo inexistente
connection refused -> Ollama no está arrancado
timeout -> modelo pesado o PC lento
```

## 4. Diagnóstico de Hugging Face

Variables a registrar:

```text
HF_REALTIME_CONNECTION_MODE
HF_REALTIME_WS_URL
REALTIME_TRANSCRIPTION_LANGUAGE
HF_TOKEN presente: sí/no
```

Interpretación:

```text
deployed -> usa servidor remoto Hugging Face/Pollen
local -> usa WebSocket local configurado
```

## 5. Diagnóstico de app activa

Comprobar procesos:

```powershell
Get-CimInstance Win32_Process |
Where-Object {{ $_.CommandLine -match "ahootsa|reachy|conversation|uvicorn|python" }} |
Select-Object ProcessId, Name, CommandLine |
Format-List
```

Comprobar daemon:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/daemon/status
```

Comprobar app web:

```powershell
Invoke-RestMethod http://127.0.0.1:7860/status
```

## 6. Diagnóstico de cámara PC

Abrir:

```text
http://127.0.0.1:7860/camera/page
```

Revisar:

```text
Permisos de privacidad de Windows
Permiso de cámara en navegador/WebView
Otra aplicación usando la cámara
Consola del navegador si está disponible
D:\RITXI\logs\camera
```

## 7. Diagnóstico de Memory

Buscar en `eventos.jsonl`:

```text
start_memory_pairs_game
memory_reset
choose_memory_cards
memory_choose_result
duplicate_ignored
reaction_schedule
beep_result
```

Si hay doble audio, revisar:

```text
speak
say
tts_text
speechSynthesis
winsound
pyttsx3
```

## 8. Diagnóstico de audio

Errores habituales:

```text
pygame not installed or not importable
winsound backend ok
gstreamer skipped
speechSynthesis active
```

Interpretación:

```text
pygame error -> no suena audio .ogg de emociones
winsound ok -> está sonando beep Windows
speechSynthesis -> voz navegador/Windows no deseada
```

## 9. Errores PowerShell históricos

### `SwitchParameter`

Error:

```text
No se puede convertir el valor "System.String" al tipo SwitchParameter
```

Causa:

```powershell
-Force:$Force
```

Solución:

```powershell
$args = @()
if ($Force) { $args += "-Force" }
```

### `param(...)` roto

Error:

```text
La expresión de asignación no es válida
[int]$Port = 8000
```

Causa:

```text
código antes del bloque param(...)
```

Solución:

```text
param(...) debe ser el primer bloque ejecutable del script.
```

### `Add-Content` bloqueado

Error:

```text
El proceso no puede obtener acceso al archivo pantalla.log
```

Solución:

```text
cada ejecución con timestamp y escritura tolerante a bloqueo.
```

## 10. Qué enviar para depurar

Enviar siempre:

```text
ULTIMA_EJECUCION_AHOOTSA_INFO.txt
últimas 80 líneas de pantalla.log
últimas 80 líneas de runtime.log
últimas 80 líneas de eventos.jsonl
resultado de ollama list
captura de la interfaz si hay fallo visual
```
