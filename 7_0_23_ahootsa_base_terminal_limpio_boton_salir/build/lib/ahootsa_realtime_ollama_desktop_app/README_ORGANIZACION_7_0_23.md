# Organización interna Ahootsa 7.0.23

Esta versión no cambia el comportamiento visible. Ordena la app para que sea más mantenible:

- `tools/`: solo herramientas Python cargables por Reachy Mini y utilidades necesarias para ellas.
- `profiles/`: perfiles externos Ahootsa. `play_emotion.py` sigue aquí para evitar colisiones con la herramienta oficial.
- `data/memory/games/`: juegos de parejas JSON.
- `data/communication/`: catálogo de actividades de comunicación de tres niveles.
- `data/dances/`: catálogos de bailes, emociones y aliases en español.
- `config/`: configuración editable desde el panel.
- `routes/`: rutas del panel/API Ahootsa.
- `services/`: utilidades compartidas de rutas/herramientas.
- `templates/`: HTML reutilizable.
- `legacy/`: código histórico no cargado por el perfil principal.

Los endpoints públicos se mantienen: `/ahootsa`, `/memory/*`, `/communication/*`, `/camera_pc/*`, `/ollama/*`.
