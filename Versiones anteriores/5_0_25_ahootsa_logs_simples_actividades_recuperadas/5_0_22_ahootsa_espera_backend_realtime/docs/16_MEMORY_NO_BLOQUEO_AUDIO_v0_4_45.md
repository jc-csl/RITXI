# 16 — Memory estable sin bloqueo de audio v0.4.57

## Problema

El juego Memory podía quedarse parado y dejar de responder al audio.

## Evidencia

En el log se veía que el wrapper intentaba copiar perfiles mientras la app estaba en marcha y algunos archivos estaban bloqueados por Windows. También se veía que el arranque usaba el perfil desde la carpeta del proyecto editable.

## Corrección

```text
- Ya no se copian perfiles durante el arranque de la app.
- La copia de perfiles se hace solo con scripts de instalación/reparación.
- choose_memory_cards ya no ejecuta movimiento ni audio interno.
- Memory queda en modo visual + voz normal para no bloquear el micrófono.
- Se mantiene protección anti-duplicado.
```

## Reparación directa

Con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_MEMORY_ESTABLE_SIN_BLOQUEO.ps1
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_MEMORY_NO_BLOQUEO.ps1
```

Debe mostrar:

```text
sin await emotion = True
sin play_emotion interno = True
visual_only_no_blocking_audio = True
```

## Secuencia esperada

```text
Usuario: uno y tres
1. Las cartas se giran.
2. Ahootsa habla la frase.
3. El micrófono sigue activo.
4. No se lanza movimiento ni sonido interno desde la jugada.
```

Las emociones y bailes siguen disponibles fuera del juego.

---

## Actualización 5_0: modo MuJoCo web sin Desktop

Esta documentación pertenece ahora al paquete `5_0_ahootsa_mujoco_web_sin_desktop`.

Modo recomendado para esta versión:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

Reglas de uso:

```text
- No abrir Reachy Mini Desktop en este modo.
- Usar el panel web http://127.0.0.1:8000.
- Mantener ON solo ahotsa_realtime_ollama_app.
- Mantener OFF reachy_mini_conversation_app.
```

Documentos principales añadidos:

```text
39_MODO_MUJOCO_WEB_SIN_DESKTOP_5_0.md
40_COMANDOS_5_AHOOTSA_MUJOCO_WEB.md
41_API_REST_USADA_5_AHOOTSA_MUJOCO_WEB.md
42_NO_USAR_DESKTOP_EN_MODO_MUJOCO_WEB.md
43_CHANGELOG_5_0.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0 -->

---

## Actualización 5_0_1: fix rutas con espacios

Se corrige el error de PowerShell provocado por la ruta:

```text
Reachy Mini Control
```

El script principal `LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1` ahora genera un `.ps1` temporal y llama al daemon mediante variable, no mediante una cadena inline.

Documento nuevo:

```text
44_FIX_RUTAS_CON_ESPACIOS_5_0_1.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_1 -->

---

## Actualización 5_0_2: limpieza de scripts antiguos

Se han eliminado scripts anteriores que ya no son necesarios para el modo actual.

Scripts actuales:

```text
INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
LANZAR_SOLO_DAEMON_5_MUJOCO.ps1
PARAR_5_AHOOTSA_MUJOCO_WEB.ps1
test\DIAGNOSTICAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

Documento nuevo:

```text
45_LIMPIEZA_SCRIPTS_5_0_2.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_2 -->

---

## Actualización 5_0_3: fix profile=default

En modo daemon web, el log puede mostrar:

```text
Loading tools for profile: default
```

Desde 5.0.3, `INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1` copia el perfil Ahootsa también sobre `default` y `starter_profile`, para que las herramientas de Ahootsa carguen aunque el motor interno use el perfil `default`.

Documento nuevo:

```text
46_FIX_PROFILE_DEFAULT_5_0_3.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_3 -->

---

## Actualización 5_0_4: identidad Ahootsa y castellano

Se corrige el caso en que la app arranca diciendo que es Reachy Mini o hablando en inglés.

Cambios:
- greeting en castellano;
- instrucciones reforzadas;
- perfil copiado también sobre `default`, `starter_profile` y `external_content/external_profiles`;
- `.env` con identidad Ahootsa;
- variables de proceso en el launcher;
- runtime copy activado en `main.py`.

Documento nuevo:

```text
47_FIX_IDENTIDAD_CASTELLANO_5_0_4.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_4 -->

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
