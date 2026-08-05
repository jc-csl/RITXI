# Estado, versiones y referencias

## Estado documentado

```text
Fecha de revisión: 5 de agosto de 2026
Servidor Ahootsa: 0.12.8.6
Aplicación incluida: 0.9.0
SDK: 1.9.0
MuJoCo: 3.3.0
Python: 3.12
Backend: Hugging Face deployed
```

## Dependencias de la aplicación

El `pyproject.toml` del repositorio fija:

```toml
requires-python = ">=3.11"
"reachy-mini[mujoco]==1.9.0"
```

La configuración de desarrollo declara Python 3.12. La instalación de Ahootsa
estandariza Python 3.12 para evitar diferencias entre equipos.

## Dependencias del servidor

`requirements.txt` contiene:

```text
fastapi
uvicorn
sqlalchemy
```

El generador PDF usa además ReportLab, que debe instalarse explícitamente:

```powershell
uv pip install --python .\.venv\Scripts\python.exe "reportlab>=4,<5"
```

## Estado del repositorio

La carpeta `AHOOTSA8` contiene:

- aplicación de conversación incluida;
- servidor local;
- perfiles y herramientas;
- recursos de bailes;
- scripts operativos;
- documentación histórica;
- carpetas de actualizaciones anteriores.

Para una instalación nueva se usa directamente el estado actual de
`AHOOTSA8`; no se encadenan updates históricos.

## Compatibilidad con la aplicación oficial

La versión oficial actual puede evolucionar y utilizar otros formatos de
perfil o versiones del SDK. AHOOTSA8 está fijado sobre su copia 0.9.0 y su
`uv.lock`.

Actualizar el upstream requiere:

1. rama separada;
2. copia de datos;
3. comparación de perfiles;
4. adaptación de herramientas externas;
5. prueba del daemon;
6. prueba de audio;
7. prueba de los dos modos;
8. prueba de informes;
9. actualización de documentación.

## Referencias

- Proyecto: https://github.com/jc-csl/RITXI
- AHOOTSA8: https://github.com/jc-csl/RITXI/tree/main/AHOOTSA8
- App oficial: https://github.com/pollen-robotics/reachy_mini_conversation_app
- SDK: https://github.com/pollen-robotics/reachy_mini
- uv: https://docs.astral.sh/uv/
- Instalación de uv:
  https://docs.astral.sh/uv/getting-started/installation/

## Documentación histórica integrada

Se han revisado especialmente:

- instalación inicial de la app oficial y MuJoCo;
- creación del perfil externo;
- configuración de personalidad, idioma y voz;
- herramientas oficiales;
- biblioteca local de bailes;
- análisis del panel profesional y niveles;
- arquitectura y actualizaciones 12.7 a 12.8.2.

Los documentos históricos siguen siendo útiles para conocer decisiones, pero
no sustituyen este manual operativo.


## Cambios funcionales de 0.12.8.6

- saludo literal con nombre en sesiones identificadas;
- uso de intereses registrados en el saludo inicial;
- saludo por defecto cuando no existen intereses;
- finalización automática de bailes;
- continuación hablada tras terminar un baile;
- documentación detallada del ciclo `ahootsa_default → ahootsa_session`.
