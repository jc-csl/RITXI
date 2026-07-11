# 11 — Estado actual 7.0.19 y pruebas

## 1. Estado validado

La última prueba confirma que Ahootsa 7.0.19:

```text
- instala sobre una 7.0.17 previa;
- registra correctamente ahootsa_realtime_ollama_app;
- arranca daemon MuJoCo;
- arranca interfaz en http://127.0.0.1:7860/ahootsa;
- carga perfil externo ahootsa7_realtime_es;
- carga tools externas Ahootsa;
- tiene recursos dance1, dance2, dance3 y emociones principales;
- reproduce baile desde panel/prueba directa.
```

El hecho de que reproduzca baile valida la cadena:

```text
alias/panel
  ↓
play_panel_dance_activity
  ↓
play_emotion del perfil
  ↓
librería D:\RITXI\reachy-mini-emotions-library
  ↓
MuJoCo / Reachy daemon
```

## 2. Diagnóstico positivo esperado

Debe aparecer:

```text
package_version 7.0.19
tools/play_emotion.py: exists=False
profiles/ahootsa7_realtime_es/play_emotion.py: exists=True
choose_has_profile_loader True
choose_uses_missing_tools_play_emotion False
panel_loads_profiles True
contains dance1 dance2 dance3 True True True
RESOURCE dance1 json True ogg True
RESOURCE dance2 json True ogg True
RESOURCE dance3 json True ogg True
RESOURCE welcoming2 json True ogg True
RESOURCE success1 json True ogg True
RESOURCE calming1 json True ogg True
RESOURCE electric1 json True ogg True
```

## 3. Rutas funcionales esperadas

Tras terminar la carga:

```text
/ahootsa/status             200 OK
/ahootsa                    200 OK
/memory/state               200 OK
/memory/page?game_id=...     200 OK
/api/v1/conversation_events 200 OK
/api/v1/mic                 200 OK
/config/list                200 OK
```

En 7.0.19 también deben existir:

```text
/ahootsa/resolve_activity
/ahootsa/list_activities
/ahootsa/play_activity
```

## 4. 404 iniciales interpretados

Se han observado muchos `404 Not Found` justo al arrancar:

```text
/memory/state
/ahootsa/status
/ahootsa
/api/v1/conversation_events
```

Luego esas rutas pasan a `200 OK`. Interpretación:

```text
sondeos antes de que la app oficial/Ahootsa termine de registrar endpoints.
```

No considerarlos fallo si posteriormente hay 200 OK y la interfaz funciona.

## 5. Problema de logs con NUL

Se observó un archivo de diagnóstico abierto en Notepad++ con caracteres `NUL`.

Estado:

```text
- no invalida la app;
- afecta a legibilidad del diagnóstico;
- debe corregirse en scripts nuevos usando UTF-8 explícito y evitando redirección *> mezclada.
```

## 6. Prueba de voz pendiente

Aunque el panel reproduce baile, todavía conviene confirmar que el motor Hugging Face llama bien a las herramientas cuando el usuario lo pide por voz.

Script:

```powershell
powershell -ExecutionPolicy Bypass -File .\TRAZAR_PRUEBA_VOZ_AHOOTSA_7_0_19.ps1 -Seconds 120
```

Frases:

```text
lista de bailes
haz baile uno
haz baile dos
haz baile tres
haz un saludo
abre juego de parejas
```

Criterio:

```text
Si por panel funciona y por voz no:
  problema de selección de herramienta por Hugging Face/instructions.txt.

Si por panel tampoco funciona:
  problema de ejecución, recurso, play_emotion, pygame o daemon.
```

## 7. Próximas mejoras recomendadas

```text
1. Arreglar definitivamente logs NUL y codificación.
2. Reducir/filtrar 404 iniciales.
3. Añadir botones directos visibles para Memory y bailes como pruebas rápidas.
4. Mejorar trazas de llamadas de herramienta por voz.
5. Añadir estado visual “app cargando / app lista”.
6. Mantener docs separadas del ZIP de versión.
```
