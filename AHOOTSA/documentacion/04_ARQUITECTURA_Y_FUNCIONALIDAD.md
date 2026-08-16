# Arquitectura y funcionalidad de AHOOTSA8

## 1. Objetivo

AHOOTSA8 es una solución de robótica social orientada a actividades
comunicativas con supervisión profesional. Combina Reachy Mini, conversación
de voz, perfiles accesibles, actividades por niveles, un panel local y
registro de sesiones.

No sustituye a profesionales ni realiza diagnósticos.

## 2. Arquitectura general

```text
Persona usuaria
      │ voz
      ▼
Reachy Mini Conversation App ───────► backend Hugging Face realtime
      │
      ├── perfil ahootsa / ahootsa_session
      ├── herramientas oficiales
      ├── herramientas externas
      ├── audio y transcripción
      └── movimientos / MuJoCo
              │
              ▼
Reachy Mini daemon :8000

Profesional
      │ navegador
      ▼
Ahootsa Local Server :8100
      ├── panel
      ├── personas y perfiles
      ├── actividades y niveles
      ├── sesiones y eventos
      ├── SQLite
      └── informes
```

## 3. Componentes

### Aplicación oficial incluida

```text
reachy_mini_conversation_app
```

Responsabilidades:

- conversación de baja latencia;
- transcripción;
- backend desplegado;
- voz;
- herramientas;
- movimientos;
- interfaz 7860.

La base es la aplicación oficial de Pollen Robotics incluida y fijada en el
repositorio. `src` no se modifica para las extensiones de Ahootsa.

### Reachy Mini SDK y daemon

El SDK 1.9.0 está dentro del `.venv` de la aplicación.

El daemon:

- conecta con robot o simulación;
- expone 8000;
- ejecuta MuJoCo en el flujo actual;
- gestiona movimiento y multimedia.

### Extensiones Ahootsa

```text
external_content\external_profiles
external_content\external_tools
external_content\activities
external_content\profile_defaults
```

### Servidor local

```text
ahootsa_local_server
```

Responsabilidades:

- alta y edición de personas;
- perfiles comunicativos;
- actividades;
- sesiones y eventos;
- contexto previo;
- seguimiento profesional;
- informes;
- persistencia SQLite.

No debe:

- sustituir la conversación oficial;
- generar cada respuesta del diálogo;
- duplicar el backend realtime;
- modificar el turno de conversación en tiempo real;
- tomar decisiones clínicas.

## 4. Dos modos de ejecución

### Anónimo

```text
INICIAR_AHOOTSA_ANONIMO.ps1
```

```text
8000 + 7860
sin 8100
perfil ahootsa
sin identificación
sin informe
```

### Sesión local

```text
INICIAR_AHOOTSA_SESION.ps1
```

```text
8100 + 8000
panel prepara sesión
7860 comienza después
perfil ahootsa_session
sesión e informe
```

## 5. Flujo de sesión

```text
profesional selecciona persona
→ revisa ficha
→ elige actividad y nivel
→ prepara sesión
→ se genera contexto
→ se prepara ahootsa_session
→ se inicia Conversation App
→ profesional registra marcas
→ se cierra conversación
→ se importa log
→ se finaliza sesión
→ se generan informes
```

## 6. Persistencia

```text
ahootsa_local_server\data\ahootsa.db
ahootsa_local_server\data\active_session.json
ahootsa_local_server\data\sessions\session_XXXXXX
```

Entidades principales:

- `users`;
- `user_profiles`;
- `sessions`;
- `session_events`;
- `memory_items`.

## 7. Informes

Cada sesión identificada puede producir:

- PDF para lectura e impresión;
- HTML para navegador;
- JSON para análisis y panel;
- TXT con la transcripción.

El generador reconstruye líneas partidas por el transcript de PowerShell,
evita duplicados mediante claves SHA-256 e importa eventos en el servidor.

## 8. Seguridad y ética

- lenguaje adulto y no infantilizante;
- consentimiento para actividades;
- posibilidad de parar;
- no almacenar datos sensibles innecesarios;
- no emitir diagnóstico;
- no cambiar niveles sin confirmación profesional;
- mantener la información en el servidor local;
- revisar los informes antes de compartirlos.

## 9. Decisiones técnicas actuales

- Windows 10/11;
- Python 3.12;
- `uv`;
- aplicación 0.9.0 incluida en el repositorio;
- SDK 1.9.0;
- MuJoCo 3.3.0;
- FastAPI;
- SQLAlchemy;
- SQLite;
- ReportLab;
- backend Hugging Face `deployed`;
- voz Sohee;
- transcripción española.

## 10. Evolución futura

Las ampliaciones deben mantenerse en las capas externas o en el servidor
local. Una actualización de la aplicación oficial debe tratarse como una
migración, no como un simple `git pull` sobre su repositorio upstream.

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


## 11. Saludo y continuación tras actividades largas

El servicio de sesión crea un saludo literal usando el nombre preferido. Si el
perfil contiene intereses, los incluye y ofrece conversar sobre ellos. La
herramienta de baile no devuelve su resultado final al comenzar, sino al
terminar, permitiendo que el backend genere la frase de continuación.
