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
