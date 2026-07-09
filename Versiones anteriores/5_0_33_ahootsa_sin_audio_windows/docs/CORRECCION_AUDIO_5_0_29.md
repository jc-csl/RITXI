# Ahootsa 5.0.30 - audio único Ahootsa

## Problema detectado

En el juego de parejas se escuchaban dos voces a la vez:

1. la voz/audio propio de Ahootsa;
2. la voz del navegador o de Windows.

Esto puede ocurrir cuando una actividad reutiliza código del frontend que llama a la API Web Speech del navegador:

```javascript
window.speechSynthesis.speak(...)
```

o crea objetos del tipo:

```javascript
new SpeechSynthesisUtterance(...)
```

En Windows, esa API usa las voces instaladas en el sistema. Por eso el resultado se percibe como “audio Windows”.

## Decisión de diseño

A partir de la versión 5.0.30 se aplica esta regla global:

> En actividades, juegos y pantallas de Ahootsa solo debe hablar Ahootsa. La voz del navegador/Windows queda bloqueada.

Esto afecta al juego de parejas y a cualquier otra actividad que intente usar `speechSynthesis`.

## Qué se bloquea

Se bloquea:

```javascript
window.speechSynthesis.speak(...)
```

También se cancela cualquier cola de voz activa del navegador mediante:

```javascript
window.speechSynthesis.cancel()
```

## Qué no se bloquea

No se bloquean de forma general las etiquetas:

```html
<audio>
```

Motivo: el audio propio de Ahootsa podría llegar al navegador como audio normal generado por el backend, TTS propio, fichero temporal o stream. Si se bloqueara todo `<audio>`, se podría silenciar también Ahootsa.

## Dónde se aplica la corrección

El parche busca el paquete instalado:

```text
%LOCALAPPDATA%\Reachy Mini Control\apps_venv\Lib\site-packages\ahootsa_realtime_ollama_desktop_app
```

y añade un guardia JavaScript en HTML/JS relevantes.

También puede parchear la carpeta de proyecto original:

```text
D:\RITXI\5_0_25_ahootsa_logs_simples_actividades_recuperadas
```

## Archivo principal del parche

```text
tools/patch_browser_audio_guard_5_0_29.py
```

Este script:

1. localiza el paquete Python `ahootsa_realtime_ollama_desktop_app`;
2. revisa archivos `.html`, `.js`, `.mjs`, `.jsx`, `.ts`, `.tsx`, `.vue` y `.svelte`;
3. inserta un bloque JavaScript marcado como:

```text
Ahootsa 5.0.30 - audio unico Ahootsa
```

4. crea copias de seguridad antes de modificar archivos:

```text
.bak_5_0_30_YYYYMMDD_HHMMSS
```

## Guardia JavaScript añadido

El guardia define una política global:

```javascript
window.AHOOTSA_AUDIO_POLICY.onlyAhootsaVoice = true;
window.AHOOTSA_AUDIO_POLICY.blockWindowsSpeechSynthesis = true;
```

Después sustituye `speechSynthesis.speak` por una función vacía que descarta la voz Windows/navegador.

Además reaplica la protección durante los primeros segundos porque algunas librerías pueden reescribir la función después de cargar la página.

## Cómo aplicar la corrección

Desde la carpeta descomprimida:

```powershell
powershell -ExecutionPolicy Bypass -File .\0_APLICAR_CORRECCION_5_0_30.ps1
```

Si además falta MuJoCo:

```powershell
powershell -ExecutionPolicy Bypass -File .\0_APLICAR_CORRECCION_5_0_30.ps1 -InstallMujoco
```

## Cómo lanzar

Después de aplicar el parche, se puede lanzar la versión original:

```powershell
powershell -ExecutionPolicy Bypass -File D:\RITXI\5_0_25_ahootsa_logs_simples_actividades_recuperadas\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

O usar el wrapper:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_0_30_AHOOTSA_MUJOCO_WEB.ps1
```

## Comprobación funcional

La comprobación real es auditiva:

1. abrir la app desde Reachy Mini Control/Desktop Control;
2. entrar en el juego de parejas;
3. iniciar la actividad;
4. confirmar que solo se oye la voz de Ahootsa;
5. confirmar que no se superpone la voz Windows/navegador.

También se incluye:

```powershell
powershell -ExecutionPolicy Bypass -File .\2_DIAGNOSTICO_AUDIO_5_0_30.ps1
```

Ese script lista los archivos en los que aparece el marcador de la corrección.

## Si sigue sonando la voz Windows

Pruebas recomendadas:

1. cerrar completamente Reachy Mini Control/Desktop Control;
2. volver a abrirlo para evitar caché de frontend;
3. ejecutar de nuevo `0_APLICAR_CORRECCION_5_0_30.ps1`;
4. revisar con `2_DIAGNOSTICO_AUDIO_5_0_30.ps1` que el guardia está insertado;
5. buscar si existe otra copia instalada del frontend Ahootsa fuera de `apps_venv`.

## Relación con versiones anteriores

La 5.0.30 acumula las correcciones previas:

- 5.0.27: endpoints de compatibilidad `/status`, `/mic`, `/voices/current`, `/voices`.
- 5.0.28: escritura robusta de logs para evitar bloqueos de `pantalla.log`.
- 5.0.30: audio único Ahootsa, sin voz Windows/navegador en actividades.
