# Update 12 — Panel profesional MVP e inicio personalizado

## Objetivo

Validar un primer recorrido completo y sencillo:

```text
seleccionar usuario
→ seleccionar actividad y nivel
→ crear sesión
→ generar contexto y perfil temporal
→ lanzar la app oficial
→ registrar marcas profesionales
→ finalizar y guardar resumen
```

## Separación de responsabilidades

La `reachy_mini_conversation_app` oficial conserva:

- conversación realtime;
- reconocimiento de voz;
- respuesta del modelo;
- voz;
- herramientas;
- movimientos de Reachy.

`ahootsa_local_server` realiza:

- selección de usuario;
- selección de actividad y nivel;
- generación del perfil temporal;
- registro de sesión y eventos;
- seguimiento profesional básico;
- resumen final.

No se modifica `src/` de la aplicación oficial.

## Scripts actuales respetados

El proyecto utiliza:

```text
1_lanzar_daemon_mujoco.ps1
2_lanzar_app_ahootsa.ps1
3_abrir_paneles_control.ps1
```

El panel utiliza el primer script para iniciar el daemon. El segundo continúa
sirviendo para el arranque manual del perfil Ahootsa base.

Para una sesión personalizada, el servidor genera un script nuevo dentro de:

```text
runtime/sessions/session_XXXXXX/2_lanzar_app_ahootsa_sesion.ps1
```

Ese script reproduce el arranque actual, pero configura antes:

- perfil temporal;
- directorio de perfiles generados;
- tools externas oficiales de Ahootsa;
- identificador y contexto de la sesión.

## Panel

```text
http://127.0.0.1:8100/panel
```

Funciones:

- ver estado de los puertos 8000, 7860 y 8100;
- lanzar daemon/MuJoCo;
- seleccionar usuario;
- seleccionar la actividad «Expresar preferencias»;
- seleccionar Inicial, Intermedio o Avanzado;
- preparar la sesión;
- lanzar la Conversation App con el perfil temporal;
- registrar respuesta adecuada, parcial, incorrecta o sin respuesta;
- registrar pista, repetición o ejemplo;
- añadir observación final;
- guardar una decisión profesional.

## Actividad JSON

La primera actividad se configura en:

```text
config/activities/express_preferences.json
```

Los tres niveles se almacenan fuera del código Python. Esto permite añadir
nuevas actividades siguiendo el mismo formato.

## Datos reutilizados

No se crean tablas nuevas en esta versión. Se utilizan:

```text
users
user_profiles
sessions
session_events
```

Los niveles y las marcas se guardan en `metadata_json`. Las tablas definitivas
de progreso se añadirán cuando este recorrido esté validado.

## Runtime

```text
runtime/
├── sessions/
├── generated_profiles/
├── imports/
└── exports/
```

Por cada sesión se crean:

```text
session_context.json
session_status.json
2_lanzar_app_ahootsa_sesion.ps1
```

## Seguridad y actualización

El endpoint de lanzamiento solo puede ejecutar scripts de rutas fijadas en
`config/panel_config.json`. No acepta comandos arbitrarios.

El servidor sigue enlazado a `127.0.0.1`, por lo que el panel no se publica en
la red local.

## Fuera del alcance

- transcripción en directo dentro del panel;
- análisis automático de logs;
- control externo completo de VAD y audio;
- progresión automática;
- modificación de nivel sin confirmación profesional;
- Ollama;
- cambios en `src/` oficial.
