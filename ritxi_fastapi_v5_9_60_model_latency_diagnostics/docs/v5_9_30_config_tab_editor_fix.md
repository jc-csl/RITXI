# v5.9.30 · Configuración editable desde la pestaña

## Cambios

La pestaña `Configuración` deja de ser una pantalla casi estática y pasa a tener un editor directo de archivos.

## Archivos editables

- `app/prompts/system_prompt.txt`
- `app/core/config.py`
- `app/config/model_presets.json`
- `profiles/characters/ritxi_tutor_comunicacion_di.json`
- `.env.example`
- `app/config/stt_vocabularies/activity_mapping.json`
- `app/config/stt_vocabularies/language.json`
- `app/config/stt_vocabularies/social_communication.json`
- `app/config/stt_vocabularies/animals.json`

## Backend

Se amplía `CONFIG_FILE_MAP` y se validan los JSON antes de escribirlos.

## Frontend

Nuevos elementos:

- `inlineConfigEditor`
- `inlineConfigSaveBtn`
- `inlineConfigReloadBtn`
- botones `.config-quick-file`

Al abrir la pestaña Configuración se carga automáticamente el prompt del sistema.
