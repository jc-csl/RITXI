# Corrección 5.0.33 — Eliminar audio Windows y dejar solo audio Ahootsa

## Problema

En actividades como el juego de parejas sonaban dos voces a la vez:

1. La voz/audio propio de Ahootsa.
2. La voz de Windows/navegador, normalmente provocada por `speechSynthesis`, `SpeechSynthesisUtterance`, `pyttsx3` o SAPI de Windows.

La corrección 5.0.29 bloqueaba `speechSynthesis`, pero no cubría todos los posibles orígenes de TTS local.

## Solución aplicada

La versión 5.0.33 aplica una política global:

```text
Solo debe hablar Ahootsa.
No debe hablar Windows/navegador.
```

### Capa navegador/frontend

Se inyecta un guardia JavaScript en HTML/JS de:

- `ahootsa_realtime_ollama_desktop_app`
- `reachy_mini_conversation_app`
- `reachy_talk_data`
- carpetas `reachy*` y `ahootsa*` dentro de `site-packages`
- carpeta local del proyecto 5.0.25 si existe

El guardia bloquea:

- `window.speechSynthesis.speak(...)`
- `window.speechSynthesis.getVoices()`
- `window.SpeechSynthesisUtterance(...)`
- llamadas reactivadas por foco, recarga de pantalla, iframes o cambios DOM

No bloquea etiquetas `<audio>`, porque la salida Realtime/Ahootsa puede llegar como audio normal.

### Capa Python/Windows

Se instala/actualiza:

```text
apps_venv\Lib\site-packages\sitecustomize.py
```

Cuando el lanzador define:

```text
AHOOTSA_DISABLE_WINDOWS_TTS=1
```

se desactivan:

- `pyttsx3.init().say(...)`
- `pyttsx3.init().runAndWait()`
- `win32com.client.Dispatch("SAPI.SpVoice").Speak(...)`
- `comtypes.client.CreateObject("SAPI.SpVoice").Speak(...)`

Esto evita que el backend o módulos heredados de la app oficial disparen voz Windows.

## Uso

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_0_33_AHOOTSA_MUJOCO_WEB.ps1
```

Si falta MuJoCo:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_0_33_AHOOTSA_MUJOCO_WEB.ps1 -InstallMujoco
```

## Comprobación rápida

```powershell
powershell -ExecutionPolicy Bypass -File .\3_COMPROBAR_AUDIO_WINDOWS_5_0_33.ps1
```

Debe mostrar:

```text
pyttsx3_disabled= True
OK_NO_DEBERIA_HABER_SONADO_AUDIO_WINDOWS
```

y no debe sonar ninguna voz Windows.

## Importante sobre caché

Después de aplicar el parche hay que cerrar y volver a abrir la ventana/app de Desktop Control. Si el navegador mantiene una versión antigua del frontend en caché, podría seguir sonando la voz anterior hasta recargar completamente.

## Reversión

Los archivos modificados crean copias `.bak_5_0_33_<timestamp>`.

Para permitir temporalmente la voz Windows:

```powershell
$env:AHOOTSA_ALLOW_WINDOWS_TTS="1"
```

Pero para Ahootsa no se recomienda, porque puede volver el solapamiento de voces.
