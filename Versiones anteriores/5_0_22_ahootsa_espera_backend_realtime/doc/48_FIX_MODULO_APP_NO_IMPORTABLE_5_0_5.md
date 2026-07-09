# Fix 5_0_5: ModuleNotFoundError de Ahootsa

## Problema observado

En el log de 5.0.3 aparece:

```text
Could not load app 'ahootsa_realtime_ollama_app' from entry point:
No module named 'ahootsa_realtime_ollama_desktop_app'
```

y después:

```text
Error while finding module specification for
'ahootsa_realtime_ollama_desktop_app.main'
(ModuleNotFoundError: No module named 'ahootsa_realtime_ollama_desktop_app')
```

Por eso `http://127.0.0.1:7860/` no se abre: la app se intenta lanzar, pero el proceso Python termina con código 1.

## Solución 5.0.5

El instalador ahora hace tres cosas:

1. Copia directamente:

```text
src/ahootsa_realtime_ollama_desktop_app
```

a:

```text
%LOCALAPPDATA%/Reachy Mini Control/apps_venv/Lib/site-packages/ahootsa_realtime_ollama_desktop_app
```

2. Crea un `.pth` para que el `src` local sea importable.

3. Intenta además:

```powershell
python -m pip install --no-deps --force-reinstall .
```

## Verificación

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

Debe salir:

```text
IMPORT_OK ... ahootsa_realtime_ollama_desktop_app
puerto 7860 abierto = True
```

cuando la app esté arrancada.

## Comando recomendado

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

---

## Actualización 5_0_5: reinstalación del módulo Python de Ahootsa

Se corrige el error:

```text
No module named 'ahootsa_realtime_ollama_desktop_app'
```

El instalador copia el módulo Python a `apps_venv\Lib\site-packages`, crea un `.pth` y verifica `IMPORT_OK`.

Documento nuevo:

```text
48_FIX_MODULO_APP_NO_IMPORTABLE_5_0_5.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_5 -->

---

## Actualizacion 5_0_6: instalador PowerShell 5.1 safe

Se corrige el error de parseo del instalador en Windows PowerShell:

```text
Token 'BLOQUE' inesperado
```

El instalador se ha reescrito con codificacion UTF-8 con BOM y cadenas seguras.

Documento nuevo:

```text
49_FIX_INSTALADOR_POWERSHELL51_5_0_6.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_6 -->

---

## Actualizacion 5_0_7: actividades directas sin bloqueo post-tool

Se corrige el bloqueo al iniciar una actividad de comunicacion. Las herramientas de actividades pasan de `needs_response = True` a `needs_response = False`, para que devuelvan la respuesta directamente sin esperar una segunda generacion del backend realtime.

Documento nuevo:

```text
50_FIX_ACTIVIDADES_DIRECTAS_5_0_7.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_7 -->
