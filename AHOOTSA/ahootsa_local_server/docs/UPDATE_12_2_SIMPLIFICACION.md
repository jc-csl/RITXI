# Update 12.2 — Perfil fijo y sesiones simplificadas

## Objetivo

Eliminar la estructura temporal `runtime` y utilizar un único perfil externo
operativo:

```text
external_content/
├── external_profiles/
│   ├── ahootsa/
│   └── ahootsa_session/
└── profile_defaults/
    └── ahootsa_default/
```

## Función de cada carpeta

- `ahootsa`: perfil general actual, mantenido como referencia visible.
- `ahootsa_default`: copia estable creada durante la instalación.
- `ahootsa_session`: perfil fijo que el servidor personaliza antes de cada
  sesión.

La aplicación oficial siempre carga `ahootsa_session`. El nombre del perfil ya
no cambia entre sesiones.

## Datos de sesión

Los datos se guardan en:

```text
ahootsa_local_server/data/sessions/session_XXXXXX/
├── session_context.json
├── session_status.json
├── profile_snapshot/
├── conversation_app.log
└── summary.json
```

## Simplificación

Se eliminan:

- `runtime/generated_profiles`;
- perfiles numerados;
- lanzadores PowerShell por sesión;
- `runtime/imports`;
- `runtime/exports`.

La carpeta `runtime` anterior se copia al backup del servidor antes de
eliminarse.

## Arranque oficial

El script estable `2_lanzar_app_ahootsa.ps1` arranca la aplicación desde su
carpeta habitual. El `.env` queda configurado con:

```text
REACHY_MINI_CUSTOM_PROFILE=ahootsa_session
```

Esto corrige el problema observado en el Update 12: el `.env` oficial
sobrescribía las variables del lanzador temporal y hacía que se cargase
`ahootsa`.

## Duración

La duración se mide:

1. desde `running_at` cuando la Conversation App llegó a responder;
2. desde `prepared_at` cuando la app no se lanzó.

El resumen indica `duration_source` para no presentar una precisión falsa.

## Finalización

Al cerrar la sesión:

- se guarda `summary.json`;
- se actualiza `session_status.json`;
- se conserva `profile_snapshot`;
- se restaura `ahootsa_session` desde `ahootsa_default`;
- se elimina `data/active_session.json`.

## Pruebas

- `COMPROBAR_ESTRUCTURA_12_2.ps1`
- `PROBAR_SESION_SIMPLE_12_2.ps1`
- `PROBAR_ARRANQUE_OFICIAL_12_2.ps1`
