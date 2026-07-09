# 02 — Estructura del programa

## Carpetas principales

```text
ahootsa_v0_4_36_docs_limpieza_tests/
├─ INSTALAR_AHOOTSA_COMPLETO.ps1
├─ FORZAR_INICIO_CASTELLANO_SOHEE.ps1
├─ REPARAR_*.ps1
├─ CAMBIAR_VOZ_AHOOTSA.ps1
├─ test/
├─ docs/
├─ scripts/
├─ src/
│  └─ ahootsa_realtime_ollama_desktop_app/
│     ├─ main.py
│     ├─ assets/
│     ├─ games/
│     └─ profiles/
│        └─ ahootsa_realtime_es/
└─ pyproject.toml
```

## Raíz del proyecto

En la raíz se dejan solo scripts operativos:

- `CAMBIAR_VOZ_AHOOTSA.ps1`
- `FORZAR_INICIO_CASTELLANO_SOHEE.ps1`
- `INSTALAR_AHOOTSA_COMPLETO.ps1`
- `INSTALAR_AUDIO_EMOCIONES_PYGAME.ps1`
- `INSTALAR_CAMARA_PC.ps1`
- `RECREAR_MODELO_OLLAMA_AHOOTSA.ps1`
- `REPARAR_HTML_JUEGO_PAREJAS.ps1`
- `REPARAR_JUEGOS_PAREJAS_JSON.ps1`
- `REPARAR_MEMORY_START_SERVER.ps1`
- `REPARAR_PANEL_INTEGRADO_DESKTOP.ps1`
- `REPARAR_PERFIL_ASK_OLLAMA.ps1`

Los scripts de prueba ya no están en la raíz. Están en:

```text
test/
```

## Paquete Python

```text
src/ahootsa_realtime_ollama_desktop_app/
```

Contiene la app instalable para Reachy Mini Desktop.

Archivos/carpetas relevantes:

```text
main.py
assets/
games/
profiles/ahootsa_realtime_es/
```

## Perfil Ahootsa

```text
src/ahootsa_realtime_ollama_desktop_app/profiles/ahootsa_realtime_es/
```

Archivos actuales del perfil:

- `actividades_disponibles.txt`
- `alimentos.json`
- `animales.json`
- `ask_ollama.py`
- `camera_pc.py`
- `choose_memory_cards.py`
- `ciudades.json`
- `greeting.txt`
- `hint_memory_pairs_game.py`
- `instructions.txt`
- `list_memory_pairs_games.py`
- `memory_pairs_animales.html`
- `memory_pairs_game_server.py`
- `memory_pairs_game_status.py`
- `memory_pairs_generic.html`
- `play_emotion.py`
- `reset_memory_pairs_game.py`
- `start_memory_pairs_game.py`
- `tools.txt`
- `voice.txt`

## Juegos

```text
src/ahootsa_realtime_ollama_desktop_app/games/
```

Archivos actuales de juegos:

- `alimentos.json`
- `animales.json`
- `ciudades.json`
- `memory_pairs_animales.html`
- `memory_pairs_game_server.py`
- `memory_pairs_generic.html`

## ¿Se necesita `ahootsa_realtime_ollama_desktop_app.egg-info`?

No para esta entrega.

`egg-info` es metadato generado por herramientas de empaquetado/instalación de Python. No es código fuente útil para editar ni entender Ahootsa.

En esta versión se elimina si aparece dentro del ZIP fuente. Se volverá a generar automáticamente si Python lo necesita durante instalación.

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
