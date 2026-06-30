# Cambios v0.4.35 - Original Tools Clean Start

- Corrige `NameError: DEFAULT_LOCAL_EMOTIONS_LIBRARY_DIR is not defined`.
- Elimina la configuración accidental de la librería local de emociones desde `main.py`.
- Limpia en el proceso las variables `AHOOTSA_EMOTIONS_LIBRARY_DIR` y `REACHY_MINI_EMOTIONS_LIBRARY_DIR`.
- Añade script `04_limpiar_variables_emociones_locales.ps1` para quitar variables persistentes de versiones anteriores.
- Mantiene solo herramientas originales de robot y la herramienta adicional `ask_ollama`.
