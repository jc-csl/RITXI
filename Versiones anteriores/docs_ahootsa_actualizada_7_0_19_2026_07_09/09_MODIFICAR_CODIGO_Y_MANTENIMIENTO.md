# 09 — Modificar código y mantenimiento

## 1. Capas que se pueden tocar

```text
PowerShell de instalación/lanzamiento
  → scripts LANZAR, INSTALAR, DIAGNOSTICAR, RESUMIR

Paquete Ahootsa
  → src/ahootsa_realtime_ollama_desktop_app

Perfiles
  → profiles/ahootsa7_realtime_es

Tools Ahootsa
  → tools/*.py

Panel HTML
  → endpoints y plantillas servidas por Ahootsa

Librería local de emociones
  → D:\RITXI\reachy-mini-emotions-library
```

No modificar como solución habitual:

```text
reachy_mini_conversation_app
reachy_talk_data
reachy_mini
```

salvo lectura/diagnóstico o limpieza de residuos Ahootsa antiguos.

## 2. Añadir una herramienta nueva

Pasos:

```text
1. Crear tools/nueva_herramienta.py.
2. Implementar clase Tool compatible con la app oficial.
3. Añadir el nombre a profiles/ahootsa7_realtime_es/tools.txt.
4. Añadir instrucciones claras en instructions.txt.
5. Añadir logs de tool_start/tool_result/tool_exception.
6. Añadir prueba directa en diagnóstico.
7. Validar compileall.
```

## 3. Cambiar comportamiento de voz

Modificar:

```text
profiles/ahootsa7_realtime_es/instructions.txt
```

Indicar de forma explícita:

```text
Si el usuario pide lista de bailes, llama a list_panel_dances_activities.
Si pide baile uno/dos/tres/saludo, llama a play_panel_dance_activity.
Si pide juego de parejas, llama a start_memory_pairs_game.
Si dice dos números durante Memory, llama a choose_memory_cards.
```

## 4. Cambiar alias de bailes

Modificar:

```text
tools/resources_bailes_emociones_es.json
```

Validar después:

```powershell
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_HERRAMIENTAS_DIRECTO_7_0_19.ps1
```

## 5. Cambiar tiempos del Memory

Modificar:

```text
tools/memory_timing_config.json
```

Ejemplo:

```json
{
  "reveal_seconds": 8.0,
  "flip_delay_seconds": 0.0,
  "refresh_interval_ms": 700,
  "iframe_height_px": 620
}
```

## 6. Crear una nueva versión

Regla:

```text
Cada versión debe ser completa e instalable.
No crear parches que dependan de versiones anteriores.
```

Proceso:

```text
1. Copiar la última versión estable.
2. Cambiar todas las cadenas 7.0.xx a 7.0.yy.
3. Actualizar __version__.
4. Actualizar nombres de scripts.
5. Revisar instalación limpia.
6. Ejecutar compileall.
7. Eliminar __pycache__ y .pyc.
8. Validar que el ZIP no contiene docs, logs ni fotos.
9. Crear zip final.
10. Actualizar docs aparte si la versión queda como referencia.
```

## 7. Prueba mínima antes de entregar ZIP

```text
- instalar con -ForceInstall -RestartDaemon;
- abrir /ahootsa;
- ejecutar diagnóstico directo;
- probar /memory/page;
- probar alias baile dos;
- probar botón/panel baile uno/dos/tres/saludo;
- si es posible, probar voz con traza.
```
