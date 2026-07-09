# Fix 5_0_6: instalador compatible con PowerShell 5.1

## Problema

En 5.0.5 el instalador fallaba al parsear en Windows PowerShell:

```text
Token 'BLOQUE' inesperado
Falta el parentesis de cierre
Token 'OK]' inesperado
```

## Causa

El script tenia una mezcla peligrosa para PowerShell 5.1:

- UTF-8 sin BOM.
- Texto con caracteres especiales.
- Bloques multilinea complejos dentro del instalador.

## Solucion 5.0.6

El instalador se ha reescrito de forma segura:

- archivo `.ps1` guardado como UTF-8 con BOM;
- cadenas ASCII en las zonas criticas;
- sin here-strings complejos;
- instalacion del modulo Ahootsa mantenida;
- copia de perfiles mantenida;
- identidad Ahootsa y castellano mantenidos.

## Comando

```powershell
cd D:\RITXI\5_0_6_ahootsa_mujoco_web_fix_instalador_ps51
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_SINTAXIS_PS1.ps1
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

## Esperado

```text
IMPORT_OK ... ahootsa_realtime_ollama_desktop_app
Daemon started successfully
App ahootsa_realtime_ollama_app is running
Uvicorn running on http://localhost:7860
```

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
