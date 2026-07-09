# Fix 5_0_7: actividades de comunicacion directas

## Problema

Ahootsa 5.0.6 ya arranca correctamente:

```text
Uvicorn running on http://localhost:7860
Loading tools for profile: ahootsa_realtime_es
Found 33 tools to load
```

Pero al iniciar una actividad de comunicacion, por ejemplo nivel normal actividad 3, puede quedarse esperando y no contestar.

## Causa probable

Las herramientas de actividades estaban con:

```python
needs_response = True
```

Eso obliga al backend realtime a hacer una segunda respuesta despues de ejecutar la herramienta. En este modo se esta usando el backend realtime Hugging Face, y esa segunda fase puede bloquearse.

## Solucion 5.0.7

Las herramientas de comunicacion pasan a respuesta directa:

```python
needs_response = False
```

Herramientas cambiadas:

```text
actividades_comunicacion
listar_actividades_comunicacion
iniciar_actividad_comunicacion
list_communication_activity_levels
list_communication_activities
start_communication_activity
```

Tambien se aplica el mismo criterio a las herramientas principales del juego de parejas para reducir bloqueos similares.

## Reiniciar solo Ahootsa

Si se queda parado, no hace falta cerrar MuJoCo:

```powershell
powershell -ExecutionPolicy Bypass -File .\REINICIAR_5_APP_AHOOTSA.ps1
```

## Comprobar

```powershell
powershell -ExecutionPolicy Bypass -File .\test\PROBAR_5_ACTIVIDADES_DIRECTAS.ps1
```

Debe salir:

```text
start_communication_activity.py direct = True
actividades_comunicacion.py direct = True
```

---

## Actualizacion 5_0_7: actividades directas sin bloqueo post-tool

Se corrige el bloqueo al iniciar una actividad de comunicacion. Las herramientas de actividades pasan de `needs_response = True` a `needs_response = False`, para que devuelvan la respuesta directamente sin esperar una segunda generacion del backend realtime.

Documento nuevo:

```text
50_FIX_ACTIVIDADES_DIRECTAS_5_0_7.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_7 -->
