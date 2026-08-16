# Ahootsa 0.12.5 — Estado consolidado

## Objetivo

La versión 0.12.5 consolida el trabajo realizado desde el panel MVP y elimina
las carpetas de pruebas incrementales. Solo se conserva una prueba final
guiada de extremo a extremo.

## Arquitectura

```text
D:\RITXI\AHOOTSA8
├── reachy_mini_conversation_app
│   └── external_content
│       ├── external_profiles
│       │   ├── ahootsa
│       │   └── ahootsa_session
│       ├── profile_defaults
│       │   └── ahootsa_default
│       ├── external_tools
│       └── activities
├── ahootsa_local_server
│   ├── app
│   ├── config
│   ├── data
│   │   ├── ahootsa.db
│   │   └── sessions
│   ├── docs
│   └── tools
│       └── ahootsa_smoke_test.py
├── scripts
│   └── ahootsa_process_utils.ps1
├── 0_detener_servicios_ahootsa.ps1
├── 1_lanzar_daemon_mujoco.ps1
├── 2_lanzar_app_ahootsa.ps1
├── 3_abrir_paneles_control.ps1
├── COMPROBAR_SERVICIOS_AHOOTSA.ps1
├── PROBAR_AHOOTSA_COMPLETO.ps1
└── LIMPIAR_AHOOTSA8.ps1
```

## Correcciones consolidadas

- Perfil operativo fijo `ahootsa_session`.
- Perfil de seguridad `ahootsa_default`.
- Sesiones bajo `ahootsa_local_server/data/sessions`.
- Arranques que limpian procesos anteriores.
- Endpoint oficial corregido:
  `/api/v1/personalities`.
- Versión coherente `0.12.5` en API, panel y lanzador.
- Eliminación de la carpeta `tests` y de los paquetes incrementales.
- Una única prueba final.

## Prueba final

`PROBAR_AHOOTSA_COMPLETO.ps1`:

1. arranca o comprueba Ahootsa Local Server;
2. prepara una sesión técnica;
3. arranca Reachy Mini daemon y MuJoCo;
4. arranca la Conversation App oficial;
5. verifica el perfil `ahootsa_session`;
6. comprueba el saludo personalizado, la voz y el micrófono;
7. verifica simultáneamente los puertos 8000, 7860 y 8100;
8. espera una intervención hablada real;
9. captura del log la transcripción del usuario y la respuesta de Aocha;
10. registra ambos turnos en la sesión;
11. finaliza la sesión;
12. comprueba API, SQLite y resumen;
13. guarda `smoke_test_report_12_5.json`.

La prueba usa el audio real del equipo. No sintetiza una conversación falsa.

## Registro normal

La prueba final demuestra que los turnos de la Conversation App pueden
capturarse y persistirse. La importación automática continua de todas las
conversaciones normales todavía no forma parte del flujo productivo; esta
versión valida el camino técnico con una conversación breve controlada.

## Limpieza

`LIMPIAR_AHOOTSA8.ps1` funciona primero en modo de revisión. Solo borra al
ejecutarse con `-Confirmar`.

Elimina:

- carpetas `AHOOTSA_UPDATE_*`;
- carpetas `AHOOTSA_PRUEBA_*`;
- tests incrementales;
- cachés Python;
- backups de parches anteriores;
- carpetas `runtime` y `logs` antiguas;
- informes automáticos de pruebas obsoletas.

Conserva código principal, perfiles, SQLite, sesiones, documentación, recursos
de baile y la prueba final.
