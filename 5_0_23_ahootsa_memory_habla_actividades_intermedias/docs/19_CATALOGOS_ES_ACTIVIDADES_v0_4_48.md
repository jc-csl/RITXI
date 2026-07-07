---

# Anexo v0.4.57 — Catálogos españoles de emociones, dances y actividades

## Archivos nuevos

```text
profiles\ahootsa_realtime_es\emotions_catalog_es.json
profiles\ahootsa_realtime_es\dances_catalog_es.json
profiles\ahootsa_realtime_es\list_emotions.py
profiles\ahootsa_realtime_es\list_all_activities.py
REPARAR_CATALOGOS_ES_AHOOTSA.ps1
test\DIAGNOSTICAR_CATALOGOS_ES_AHOOTSA.ps1
docs\manual_archivos_config.md
```

## `emotions_catalog_es.json`

Función:

```text
Catálogo en español de emociones, reacciones y pequeños bailes de la librería de emociones.
```

Guarda:

```text
- id semántico
- technical_id real o probable
- nombre en español
- categoría
- herramienta recomendada
- alias en español
- ejemplos de petición por voz
```

Ejemplo:

```json
{
  "id": "calma",
  "technical_id": "calming1",
  "name_es": "calma",
  "category": "calma_apoyo",
  "tool": "play_emotion_with_audio",
  "aliases": ["calma", "tranquila", "relájate"]
}
```

Cómo pedirlo:

```text
haz una emoción de calma
ponte tranquila
relájate
```

## `dances_catalog_es.json`

Función:

```text
Catálogo en español de dances comunitarios de pollen-robotics/reachy-mini-dances-library.
```

Guarda:

```text
- id técnico del JSON
- nombre español
- categoría
- alias en español
- ejemplos de petición
```

Ejemplo:

```json
{
  "id": "chicken_peck",
  "name_es": "picoteo de gallina",
  "category": "animal",
  "aliases": ["gallina", "picoteo", "baile de gallina"]
}
```

Cómo pedirlo:

```text
haz el baile de gallina
haz el picoteo de gallina
```

## `list_emotions.py`

Invocación:

```text
list_emotions()
list_emotions(category="positivas")
list_emotions(only_available=true)
```

Función:

```text
Lista emociones disponibles con nombre español, id técnico, alias y disponibilidad de JSON/OGG local.
```

Peticiones por voz:

```text
dime tus emociones
qué emociones tienes
lista tus reacciones
```

## `list_all_activities.py`

Invocación:

```text
list_all_activities()
list_all_activities(detail="full")
```

Función:

```text
Lista todo lo que Ahootsa sabe hacer:
- juegos Memory
- emociones
- dances comunitarios
- actividades del panel
```

Peticiones por voz:

```text
qué sabes hacer
dime tus actividades
qué juegos y emociones tienes
lista todo lo que puedes hacer
```

## `tools.txt`

Se actualiza añadiendo:

```text
list_emotions
list_all_activities
```

## `instructions.txt`

Se actualiza con reglas:

```text
Si el usuario pregunta "¿qué sabes hacer?", usa list_all_activities.
Si pregunta "¿qué emociones tienes?", usa list_emotions.
Si pregunta "¿qué bailes o dances tienes?", usa list_community_dances o list_all_activities.
```

## Reparación directa

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_CATALOGOS_ES_AHOOTSA.ps1
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_CATALOGOS_ES_AHOOTSA.ps1
```

Resultado esperado:

```text
emotions_catalog_es.json = True
dances_catalog_es.json = True
list_emotions.py = True
list_all_activities.py = True
tool list_emotions = True
tool list_all_activities = True
```

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
