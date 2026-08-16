# Configuración de AHOOTSA8

**Versión documentada:** 0.12.8.2

## 1. Regla principal

La aplicación oficial incluida en el repositorio es el motor de conversación.
La personalización de Ahootsa se realiza fuera de `src`.

No modificar:

```text
reachy_mini_conversation_app\src
```

Extensiones de Ahootsa:

```text
reachy_mini_conversation_app\external_content
ahootsa_local_server
scripts
```

## 2. Perfiles

### Perfil general

```text
external_content\external_profiles\ahootsa
```

Se utiliza en el modo anónimo. No contiene identificación de una persona ni
datos de una sesión local.

### Perfil de sesión

```text
external_content\external_profiles\ahootsa_session
```

Se prepara para una sesión identificada. El servidor local introduce el
contexto de la persona, actividad y nivel.

### Plantilla

```text
external_content\profile_defaults\ahootsa_default
```

Sirve para regenerar el perfil de sesión.

La aplicación incluida en AHOOTSA8 es la versión 0.9.0 y utiliza archivos como:

```text
instructions.txt
greeting.txt
tools.txt
voice.txt
```

No migrar automáticamente al formato `profile.md` de versiones oficiales más
nuevas sin una actualización y una prueba de compatibilidad.

## 3. Archivo .env de la aplicación

Ruta:

```text
D:\RITXI\AHOOTSA8\reachy_mini_conversation_app\.env
```

Configuración recomendada:

```env
REALTIME_TRANSCRIPTION_LANGUAGE="es"
HF_REALTIME_CONNECTION_MODE="deployed"
HF_TOKEN=
REACHY_MINI_CUSTOM_PROFILE=ahootsa
REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY=./external_content/external_profiles
REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY=./external_content/external_tools
AUTOLOAD_EXTERNAL_TOOLS=false
```

Los scripts cambian temporalmente `REACHY_MINI_CUSTOM_PROFILE` a
`ahootsa_session` al iniciar una sesión identificada y lo restauran a
`ahootsa` al finalizar.

## 4. Voz e idioma

Configuración actual:

```text
idioma de transcripción: español
voz de referencia: Serena
nombre hablado del robot: Aocha
```

La voz se define en el perfil externo. Las instrucciones deben mantener:

- español natural;
- frases cortas;
- lenguaje adulto;
- una sola pregunta por turno;
- respeto a silencios y decisiones;
- ausencia de infantilización.

## 5. Herramientas externas

Ruta:

```text
external_content\external_tools
```

Herramienta principal de Ahootsa:

```text
ahootsa_dances.py
```

La actividad `Vamos a bailar` utiliza recursos locales dentro de
`external_content\activities`.

No activar herramientas de forma global con `AUTOLOAD_EXTERNAL_TOOLS=true`
salvo una prueba controlada. La selección debe depender del perfil y de
`tools.txt`.

## 6. Configuración del servidor local

Ruta:

```text
ahootsa_local_server\config\panel_config.json
```

Relaciones importantes:

```text
project_root                       ..
official_app_directory             ../reachy_mini_conversation_app
base_profile_directory             perfil ahootsa
profile_template_directory         ahootsa_default
active_session_profile_directory   ahootsa_session
external_tools_directory           external_tools
session_data_directory             ./data/sessions
active_session_file                ./data/active_session.json
conversation_app_port              7860
daemon_port                        8000
server_url                         http://127.0.0.1:8100
```

Todas las rutas son relativas a `ahootsa_local_server`. Esto permite que los
scripts operativos usen la carpeta del proyecto como referencia.

## 7. Base de datos

Archivo:

```text
ahootsa_local_server\data\ahootsa.db
```

Tecnología:

```text
SQLite + SQLAlchemy
```

Datos principales:

- personas;
- perfiles;
- sesiones;
- eventos;
- memorias locales;
- observaciones;
- estados y resúmenes.

No editar la base SQLite mientras el servidor local está activo.

## 8. Actividades y niveles

Cada actividad tiene tres niveles:

```text
initial       Inicial
intermediate  Intermedio
advanced      Avanzado
```

El nivel pertenece a la relación entre persona y actividad. No se debe asignar
un único nivel general a toda la persona.

El profesional registra:

- respuesta adecuada;
- respuesta parcial;
- respuesta incorrecta;
- sin respuesta;
- pista;
- repetición;
- ejemplo.

El sistema puede mostrar información orientativa, pero el profesional decide
mantener, subir, bajar temporalmente o repetir.

## 9. Informes

El generador:

```text
ahootsa_local_server\tools\ahootsa_session_report.py
```

Formatos:

```text
informe_sesion.pdf
informe_sesion.html
informe_sesion.json
transcripcion_sesion.txt
```

ReportLab se instala en el `.venv` del servidor local.

El informe no es una evaluación clínica y no decide automáticamente cambios de
nivel.

## 10. Puertos y URLs

| Componente | Puerto | Dirección |
|---|---:|---|
| Reachy Mini daemon | 8000 | `http://127.0.0.1:8000/docs` |
| Ahootsa Local Server | 8100 | `http://127.0.0.1:8100/docs` |
| Panel profesional | 8100 | `http://127.0.0.1:8100/panel-12-7-2` |
| Conversation App | 7860 | `http://127.0.0.1:7860` |

La ruta del panel mantiene el nombre `panel-12-7-2` aunque el servidor sea
0.12.8.2. No renombrarla sin revisar las referencias de los scripts.

## Fuentes verificadas

Documentación revisada el 5 de agosto de 2026:

- Repositorio del proyecto: https://github.com/jc-csl/RITXI
- Carpeta actual `AHOOTSA8`: https://github.com/jc-csl/RITXI/tree/main/AHOOTSA8
- Aplicación oficial incluida en el proyecto:
  https://github.com/jc-csl/RITXI/tree/main/AHOOTSA8/reachy_mini_conversation_app
- Aplicación oficial de Pollen Robotics:
  https://github.com/pollen-robotics/reachy_mini_conversation_app
- SDK Reachy Mini:
  https://github.com/pollen-robotics/reachy_mini
- Instalación oficial de `uv`:
  https://docs.astral.sh/uv/getting-started/installation/

La instalación descrita utiliza las versiones fijadas por el repositorio
AHOOTSA8. No debe sustituirse automáticamente por la última versión del
repositorio oficial de Pollen Robotics.
