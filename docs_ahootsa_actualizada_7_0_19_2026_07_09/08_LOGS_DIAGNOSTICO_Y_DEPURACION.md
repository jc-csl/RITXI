# 08 — Logs, diagnóstico y depuración

## 1. Ubicación

```text
D:\RITXI\logs
```

Nombres habituales:

```text
ahootsa7_YYYYMMDD_HHMMSS_pantalla.log
ahootsa7_YYYYMMDD_HHMMSS_runtime.log
AHOOTSA7_RESUMEN_YYYYMMDD_HHMMSS.log
AHOOTSA_DIAGNOSTICO_DIRECTO_7_0_19_YYYYMMDD_HHMMSS.log
AHOOTSA_TRAZA_VOZ_7_0_19_YYYYMMDD_HHMMSS.log
```

El resumen con timestamp evita bloquear o sobrescribir siempre:

```text
AHOOTSA7_ULTIMO_RESUMEN.log
```

Se recomienda mantener un puntero simple:

```text
AHOOTSA7_ULTIMO_RESUMEN_POINTER.txt
```

## 2. Diagnóstico directo 7.0.19

```powershell
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_HERRAMIENTAS_DIRECTO_7_0_19.ps1
```

Debe comprobar:

```text
package_version 7.0.19
tools/play_emotion.py: exists=False
profiles/ahootsa7_realtime_es/play_emotion.py: exists=True
contains dance1 dance2 dance3 True True True
RESOURCE dance1 json True ogg True
RESOURCE dance2 json True ogg True
RESOURCE dance3 json True ogg True
HTTP_OK /ahootsa/status
HTTP_OK /ahootsa
HTTP_OK /memory/state
HTTP_OK /memory/page
```

## 3. Diagnóstico de voz

```powershell
powershell -ExecutionPolicy Bypass -File .\TRAZAR_PRUEBA_VOZ_AHOOTSA_7_0_19.ps1 -Seconds 120
```

Frases:

```text
lista de bailes
haz baile dos
haz baile tres
haz un saludo
abre juego de parejas
```

Buscar en logs:

```text
list_panel_dances_activities
play_panel_dance_activity
start_memory_pairs_game
choose_memory_cards
```

## 4. Logs con NUL

Problema observado:

```text
Un diagnóstico puede abrirse en Notepad++ lleno de caracteres NUL.
```

Interpretación:

```text
No significa que Ahootsa esté rota.
Suele ser un problema de codificación o redirección PowerShell/Python.
```

Causa probable:

```text
- redirecciones tipo *> $RunOut;
- mezcla de stdout y stderr;
- salida UTF-16/bytes nulos interpretados como texto;
- PowerShell capturando avisos como NativeCommandError.
```

Criterio para scripts nuevos:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
Set-Content -Encoding UTF8
Add-Content -Encoding UTF8
```

Evitar:

```powershell
*> $RunOut
```

Preferir capturar stdout/stderr por separado o ejecutar Python con entorno UTF-8:

```powershell
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
```

## 5. 404 iniciales

Durante arranque pueden aparecer:

```text
GET /memory/state 404 Not Found
GET /ahootsa/status 404 Not Found
GET /ahootsa 404 Not Found
```

Si luego pasan a `200 OK`, son sondeos prematuros. Mejoras pendientes:

```text
- esperar más antes de sondear rutas Ahootsa;
- no registrar como error grave los 404 anteriores a Application startup complete;
- resumir solo la última ejecución y filtrar ruido de arranque.
```

## 6. Mensajes no críticos

En simulación sin robot físico:

```text
No Reachy Mini Audio USB device found
No Reachy Mini Audio Source card found
No Reachy Mini Audio Sink card found
```

No son errores críticos si se trabaja con MuJoCo/PC.

También puede aparecer:

```text
No .env file found, using environment variables
```

No es fallo si las variables se configuran desde el lanzador.
