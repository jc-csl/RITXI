# 10 — Versiones, limpieza y migración

## 1. Línea 5.0

La línea 5.0 aportó muchas funciones, pero terminó con parches incrementales y dependencias históricas.

Problemas acumulados:

```text
- scripts dependientes de versiones previas;
- tools copiadas en paquetes oficiales;
- perfiles duplicados;
- logs ahootsa5 en versiones nuevas;
- referencias antiguas a puerto 7870;
- intentos de cargar tools/play_emotion.py;
- instalaciones pip corruptas sin RECORD.
```

## 2. Serie 7.0

La serie 7 nace como base limpia y completa.

Resumen de hitos:

```text
7.0.0  base estable inicial serie 7
7.0.1  panel HTML de configuración
7.0.2  corrección 127.0.0.1 y arranque
7.0.3  control de versión/entrypoint
7.0.4  limpieza de instalación corrupta
7.0.5  evita pip uninstall
7.0.6  perfiles sin colisiones
7.0.7  limpieza de herramientas Ahootsa copiadas en rutas oficiales
7.0.8  warnings IK de MuJoCo tratados como advertencia si el baile se ve
7.0.9  cámara PC separada de cámara MuJoCo y Memory en 7860
7.0.10 iframe Memory más visible y frases mejoradas
7.0.11 sincronización voz/iframe Memory
7.0.12 tiempo de cartas configurable
7.0.13 resumen de logs con timestamp y mejoras de Memory
7.0.14 nombres españoles para bailes/emociones
7.0.15 refuerzo de aliases y Memory
7.0.16 play_emotion del perfil, no de tools
7.0.17 aliases play/olay y diagnóstico UTF-8 parcial
7.0.18 diagnóstico de voz y endpoint alias previsto
7.0.19 endpoint alias/play/list real y botones/prueba desde panel
```

## 3. Limpieza necesaria

La instalación actual debe limpiar residuos Ahootsa en:

```text
apps_venv\Lib\site-packages\reachy_mini_conversation_app\tools
apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles
apps_venv\Lib\site-packages\reachy_talk_data\tools
apps_venv\Lib\site-packages\reachy_talk_data\profiles
```

Solo se deben borrar residuos Ahootsa conocidos, no herramientas oficiales.

## 4. Nombres de perfiles

Evitar antiguos:

```text
ahootsa_realtime_es
ahootsa5_realtime_es
```

Usar actuales:

```text
ahootsa7_realtime_es
ahootsa7_rapido
ahootsa7_actividades
ahootsa7_completo
```

Perfil por defecto:

```text
ahootsa7_realtime_es
```

## 5. Migración de equipo nuevo

En un equipo nuevo:

```text
1. Instalar Reachy Mini Control.
2. Confirmar que existe apps_venv.
3. Instalar/descargar app oficial una vez si es necesario.
4. Instalar Ahootsa 7.0.19 con -ForceInstall -RestartDaemon.
5. Confirmar panel /ahootsa.
6. Ejecutar diagnóstico directo.
7. Probar Memory y bailes desde panel.
8. Probar voz con traza.
```
