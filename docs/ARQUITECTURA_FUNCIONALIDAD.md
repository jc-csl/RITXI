# Ahootsa 5.0.26 - Arquitectura y funcionalidad

## Objetivo de esta versión

Versión correctiva sobre Ahootsa 5.0.25 para evitar errores `404 Not Found` en rutas usadas por el frontend/Desktop:

- `/voices/current`
- `/status`
- `/mic`
- `/voices`

## Estructura de carpetas

```text
5_0_26_ahootsa_endpoints_compatibilidad/
├─ 0_APLICAR_CORRECCION_5_0_26.ps1
├─ LANZAR_5_0_26_AHOOTSA_MUJOCO_WEB.ps1
├─ 1_COMPROBAR_ENDPOINTS_5_0_26.ps1
├─ instrucciones.txt
├─ tools/
│  └─ patch_ahootsa_endpoints_5_0_26.py
└─ docs/
   ├─ ARQUITECTURA_FUNCIONALIDAD.md
   └─ CORRECCION_ENDPOINTS_5_0_26.md
```

## Qué se reutiliza de la app oficial / versión anterior

Esta versión no sustituye el backend completo. Reutiliza:

- El entorno `apps_venv` de Reachy Mini Control.
- El paquete instalado `ahootsa_realtime_ollama_desktop_app`.
- El lanzador original `LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1` de la versión 5.0.25.
- La integración MuJoCo web backend realtime ya existente.
- Las funcionalidades previas de actividades, bailes, Ollama, fichas y paneles, siempre que ya estuvieran presentes en la 5.0.25 instalada.

## Qué carpetas/código son nuevos

Nuevo código incluido:

- `tools/patch_ahootsa_endpoints_5_0_26.py`: parche Python que localiza `app = FastAPI(...)` y añade endpoints.
- `0_APLICAR_CORRECCION_5_0_26.ps1`: ejecuta el parche con el Python correcto de `apps_venv`.
- `LANZAR_5_0_26_AHOOTSA_MUJOCO_WEB.ps1`: lanzador auxiliar que aplica el parche y busca el lanzador original.
- `1_COMPROBAR_ENDPOINTS_5_0_26.ps1`: comprobador de endpoints HTTP.

## Herramientas activas

- PowerShell para instalación/parche/lanzamiento.
- Python del entorno oficial:

```text
C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe
```

- FastAPI como backend HTTP de la app.
- MuJoCo para backend realtime si está instalado en `apps_venv`.

## IA remota

Esta versión correctiva no añade IA remota nueva.

## IA local / Ollama

Esta versión no modifica la lógica de Ollama. Si Ahootsa 5.0.25 ya usaba Ollama mediante funciones como `ask_ollama`, se mantiene igual.

## Criterio de llamada a Ollama

El parche no cambia el criterio de llamada a Ollama. Su único objetivo es evitar 404 en endpoints auxiliares de voz, estado y micrófono.

## Logs

Se mantiene la filosofía de logs simples de la 5.0.25:

- Log de pantalla.
- Log de eventos `.jsonl`.
- Log runtime.

Esta versión no añade logs verbosos nuevos; solo imprime en consola el resultado del parche y la ruta del backup.

## Funcionalidad corregida

Antes, el frontend repetía:

```text
GET /voices/current HTTP/1.1 404 Not Found
GET /status HTTP/1.1 404 Not Found
GET /mic HTTP/1.1 404 Not Found
```

Después del parche, esas rutas deben responder `200 OK`.

## Modo de proceder

1. Ejecutar `0_APLICAR_CORRECCION_5_0_26.ps1`.
2. Si falta MuJoCo, repetir con `-InstallMujoco`.
3. Lanzar la app original de 5.0.25 o usar el lanzador auxiliar 5.0.26.
4. Revisar que ya no aparecen 404 repetidos en `/voices/current`, `/status` y `/mic`.
