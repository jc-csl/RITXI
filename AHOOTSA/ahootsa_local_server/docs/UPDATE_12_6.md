# Update 12.6 — Ejecución anónima o identificada

La ejecución deja de estar fijada siempre a `ahootsa_session`.

## Selección automática

`2_lanzar_app_ahootsa.ps1` consulta el servidor local:

- si no hay sesión activa, establece `REACHY_MINI_CUSTOM_PROFILE=ahootsa`;
- si existe una sesión activa, utiliza `ahootsa_session`.

La aplicación oficial carga `.env` con prioridad, por lo que el lanzador
actualiza ese valor antes de iniciar la aplicación y lo restaura a `ahootsa`
al finalizar.

## Sesión identificada

Al cerrar la Conversation App:

1. termina el transcript de PowerShell;
2. reconstruye las líneas partidas;
3. importa los turnos desde la primera intervención del usuario;
4. evita duplicados mediante una clave estable;
5. finaliza la sesión si sigue activa;
6. genera informe HTML, JSON y texto.

## Sesión anónima

No crea registros asociados a una persona ni genera informe.
