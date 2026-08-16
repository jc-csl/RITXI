# AGENTS.md — AHOOTSA Local Server

## 1. Objetivo del proyecto

AHOOTSA Local Server es la aplicación local de control y gestión de sesiones de AHOOTSA / Reachy Mini.

Su función es actuar como capa profesional y de orquestación alrededor de la aplicación oficial de conversación de Reachy Mini, sin sustituirla.

El servidor debe permitir progresivamente:

- seleccionar un usuario;
- seleccionar una actividad;
- consultar y aplicar el nivel actual de ese usuario para esa actividad;
- preparar el contexto necesario antes de iniciar la conversación;
- iniciar y registrar una sesión;
- registrar eventos relevantes durante la sesión;
- guardar resúmenes y resultados;
- mostrar la información al profesional;
- permitir al profesional decidir mantener, subir o bajar el nivel;
- conservar historial por usuario y por actividad;
- facilitar futuras estadísticas, seguimiento y administración.

El sistema debe seguir siendo LOCAL y modular.

## 2. Principio fundamental

NO rehacer el proyecto desde cero.

Antes de modificar código:

1. estudiar la implementación existente;
2. localizar qué funcionalidad ya existe;
3. reutilizar código, modelos, endpoints y servicios existentes siempre que sea razonable;
4. realizar cambios pequeños y verificables;
5. preservar compatibilidad con lo que ya funciona.

No introducir una arquitectura nueva únicamente porque sea más moderna o diferente.

## 3. Arquitectura que debe preservarse

El servidor actual utiliza o puede contener:

- FastAPI;
- SQLAlchemy;
- SQLite;
- modelos de usuarios;
- perfiles;
- sesiones;
- eventos;
- resúmenes;
- memoria;
- actividades;
- niveles;
- contexto unificado;
- snapshots;
- API REST;
- frontend/panel local.

Estos elementos son parte de la arquitectura existente y deben estudiarse antes de modificarlos.

No sustituir FastAPI, SQLAlchemy o SQLite salvo instrucción explícita.

## 4. Frontera con Reachy Mini

AHOOTSA Local Server NO es el motor conversacional.

El motor conversacional principal es la aplicación oficial de Reachy Mini.

La arquitectura objetivo es:

AHOOTSA Local Server
→ selecciona usuario, actividad y nivel
→ prepara perfil/contexto temporal
→ inicia o configura la sesión
→ Reachy Mini Conversation App realiza la conversación
→ AHOOTSA Local Server registra y analiza la sesión
→ el profesional revisa resultados y decide el siguiente nivel

AHOOTSA Local Server no debe duplicar innecesariamente funcionalidades ya resueltas por Reachy Mini Conversation App.

## 5. Código externo protegido

NO modificar automáticamente:

- `reachy_mini_conversation_app/src/`
- `speech_engine/`
- llama.cpp
- configuración interna de Qwen
- Parakeet
- Kokoro
- código oficial del SDK Reachy Mini
- librerías instaladas dentro de `.venv`

Si una nueva funcionalidad requiere cambiar alguno de estos elementos:

1. detener la implementación;
2. explicar por qué es necesario;
3. proponer primero una solución que no modifique código oficial;
4. esperar autorización.

Las integraciones deben realizarse preferentemente mediante:

- APIs;
- WebSocket;
- variables de entorno;
- perfiles externos;
- herramientas externas;
- archivos de configuración;
- endpoints documentados.

## 6. Aplicación oficial de conversación

No crear un segundo chatbot independiente dentro del servidor local.

La conversación debe seguir realizándose mediante Reachy Mini Conversation App y su backend Realtime configurado.

El servidor local debe encargarse principalmente de:

- preparación;
- selección;
- configuración;
- contexto;
- registro;
- seguimiento;
- análisis;
- administración.

## 7. Usuarios, actividades y niveles

Conceptos distintos:

### Usuario

Persona que utiliza AHOOTSA.

### Actividad

Tarea o dinámica concreta disponible para el usuario.

### Nivel

El nivel NO es global para el usuario.

El nivel es independiente por actividad.

Ejemplo:

- Usuario A
  - Actividad X → nivel 1
  - Actividad Y → nivel 3
  - Actividad Z → nivel 2

No implementar un único `user.level` como fuente de verdad para todas las actividades.

La relación usuario-actividad-nivel debe quedar correctamente modelada.

## 8. Decisión del nivel

AHOOTSA puede calcular recomendaciones o indicadores.

Pero la decisión final debe pertenecer al profesional.

Al finalizar una sesión debe ser posible, cuando esa funcionalidad esté implementada:

- mantener nivel;
- subir nivel;
- bajar nivel.

No modificar automáticamente el nivel definitivo sin una acción o confirmación explícita del profesional.

## 9. Flujo funcional objetivo

El flujo de referencia es:

1. abrir panel local;
2. seleccionar usuario;
3. seleccionar actividad;
4. consultar nivel actual del usuario para esa actividad;
5. mostrar información relevante;
6. iniciar sesión;
7. generar/preparar el contexto de conversación;
8. iniciar o conectar con Reachy Mini Conversation App;
9. registrar eventos relevantes;
10. finalizar sesión;
11. generar/guardar resumen;
12. mostrar resultado al profesional;
13. profesional decide mantener, subir o bajar;
14. guardar decisión e historial.

No es obligatorio implementar todo este flujo en una sola tarea.

Implementarlo incrementalmente.

## 10. Base de datos

Antes de crear una tabla nueva:

1. comprobar si ya existe una tabla o modelo equivalente;
2. comprobar relaciones actuales;
3. reutilizar modelos existentes cuando sea coherente;
4. evitar duplicados conceptuales.

Cuando sea necesario modificar el esquema:

- explicar qué tabla cambia;
- explicar por qué;
- preservar los datos existentes;
- utilizar una migración o mecanismo seguro;
- no borrar datos automáticamente.

No ejecutar `DROP TABLE`, borrados masivos o recreaciones de base de datos sin autorización explícita.

## 11. API

Antes de crear un endpoint nuevo:

1. buscar endpoints existentes;
2. comprobar si alguno ya proporciona la información necesaria;
3. reutilizar contratos actuales cuando sea posible.

Mantener separación clara entre:

- rutas/API;
- lógica de negocio;
- acceso a datos;
- modelos/esquemas;
- frontend.

Evitar introducir lógica compleja directamente dentro de una ruta FastAPI.

## 12. Frontend

El frontend debe ser sencillo, profesional y apto para uso local.

Prioridades:

- claridad;
- accesibilidad;
- pocos pasos;
- botones y controles suficientemente grandes;
- estados visibles;
- mensajes de error comprensibles;
- evitar interfaces sobrecargadas.

El usuario principal del panel es un profesional, no un desarrollador.

Las pantallas deben reflejar el flujo real del trabajo.

No añadir dependencias frontend grandes sin justificar su necesidad.

Antes de crear un framework frontend nuevo, comprobar qué tecnología utiliza ya el proyecto.

## 13. Integración frontend/backend

No simular datos si ya existe un endpoint real.

No duplicar en frontend reglas de negocio que pertenecen al backend.

Utilizar:

- tipos/esquemas coherentes;
- validación;
- manejo de errores;
- estados de carga;
- respuestas API existentes.

Si frontend y backend no coinciden, localizar primero cuál es el contrato actual antes de cambiar ambos.

## 14. Privacidad y funcionamiento local

AHOOTSA está diseñado para funcionamiento local.

No introducir sin autorización:

- bases de datos cloud;
- almacenamiento cloud;
- telemetría externa;
- servicios SaaS;
- APIs de terceros;
- autenticación externa;
- analytics externos;
- subida automática de logs.

No enviar datos de usuarios o sesiones a servicios externos.

## 15. Datos sensibles

No mostrar ni incluir en prompts, código generado o logs:

- datos personales innecesarios;
- contraseñas;
- tokens;
- API keys;
- secretos;
- contenido completo de bases de datos reales.

No versionar:

- `.env`
- secretos;
- bases de datos de producción;
- archivos de claves;
- dumps con datos reales.

## 16. Archivos que deben excluirse del trabajo automático

No modificar salvo necesidad explícita:

- `.venv/`
- `__pycache__/`
- `.git/`
- cachés;
- bases de datos reales;
- logs históricos;
- archivos temporales;
- modelos de IA descargados;
- binarios;
- snapshots antiguos.

Si existe `.cursorignore`, respetarlo.

## 17. Git

Antes de una modificación importante:

- comprobar `git status`;
- no sobrescribir cambios locales del usuario;
- no eliminar trabajo no confirmado.

Cada tarea debe producir un conjunto de cambios pequeño y comprensible.

Evitar mezclar en un mismo cambio:

- refactorización general;
- nueva funcionalidad;
- cambio de base de datos;
- rediseño visual;
- actualización masiva de dependencias.

No hacer `git reset --hard`, `git clean -fd`, force push o acciones destructivas sin autorización.

## 18. Dependencias

No actualizar dependencias automáticamente solo porque haya versiones nuevas.

No ejecutar actualizaciones masivas.

Antes de añadir una dependencia:

1. comprobar si ya existe una herramienta equivalente;
2. justificar por qué se necesita;
3. preferir dependencias pequeñas y mantenidas;
4. evitar añadir frameworks completos para resolver una función pequeña.

Preservar versiones actualmente funcionales siempre que sea posible.

## 19. Calidad del código

Preferir:

- código sencillo;
- nombres claros;
- funciones pequeñas;
- separación de responsabilidades;
- typing cuando el proyecto ya lo utilice;
- validaciones explícitas;
- errores manejados;
- comentarios solo cuando aporten contexto.

Evitar:

- abstracciones innecesarias;
- capas sin utilidad real;
- duplicación;
- funciones gigantes;
- valores mágicos;
- código muerto.

No refactorizar partes no relacionadas con la tarea actual.

## 20. Compatibilidad con Windows

El entorno principal de desarrollo es Windows.

Tener en cuenta:

- PowerShell;
- rutas Windows;
- Python 3.12;
- ejecución local;
- localhost;
- procesos independientes.

No asumir Linux, WSL, Docker o Bash salvo que la tarea lo requiera explícitamente.

Cuando se creen scripts de operación para el usuario, usar PowerShell `.ps1`.

No crear `.cmd` salvo petición explícita.

## 21. Scripts

Para scripts destinados al usuario:

- utilizar `.ps1`;
- incluir rutas claras;
- comprobar errores;
- mostrar mensajes comprensibles;
- evitar operaciones destructivas;
- no requerir que el usuario recuerde activar manualmente un `.venv` si el script puede hacerlo.

Cuando sea necesario utilizar un entorno virtual, el propio script debe activarlo o invocar directamente sus ejecutables.

## 22. Logs

Los logs deben ser útiles para:

- diagnosticar errores;
- analizar una sesión;
- mejorar la aplicación.

Evitar generar gran cantidad de ficheros redundantes.

Preferir pocos logs bien estructurados.

No registrar secretos.

## 23. Pruebas

Después de cada modificación:

1. ejecutar las pruebas existentes relacionadas;
2. comprobar imports;
3. comprobar arranque del servidor;
4. comprobar endpoint afectado;
5. comprobar frontend afectado cuando proceda.

Si no existen tests para una funcionalidad crítica, proponer tests específicos antes de introducir un gran cambio.

No afirmar que una funcionalidad funciona si no se ha ejecutado o verificado.

Distinguir siempre entre:

- implementado;
- probado;
- pendiente de prueba.

## 24. Tratamiento de errores

Cuando aparezca un error:

1. leer el traceback completo;
2. identificar el primer punto relevante en nuestro código;
3. localizar causa raíz;
4. aplicar la corrección mínima;
5. volver a probar.

No hacer múltiples cambios especulativos simultáneamente.

## 25. Antes de modificar varias áreas

Si una tarea requiere cambios simultáneos en:

- base de datos;
- API;
- frontend;
- integración Reachy;

primero presentar un plan breve con:

- archivos afectados;
- modelos afectados;
- endpoints afectados;
- posibles riesgos;
- orden de implementación.

Después implementar por fases.

## 26. Modo de trabajo recomendado para Agent

Para una tarea nueva:

### Fase A — Analizar

Primero inspeccionar el repositorio y describir:

- implementación relevante existente;
- archivos implicados;
- código reutilizable;
- posibles incompatibilidades.

### Fase B — Planificar

Proponer el cambio mínimo necesario.

### Fase C — Implementar

Modificar únicamente los archivos necesarios.

### Fase D — Verificar

Ejecutar pruebas/comandos relevantes.

### Fase E — Informar

Al finalizar indicar:

- qué se modificó;
- archivos cambiados;
- pruebas ejecutadas;
- resultado;
- cualquier aspecto pendiente.

## 27. No asumir requisitos

Si un requisito funcional importante no está claro y afecta a:

- estructura de BD;
- flujo profesional;
- privacidad;
- integración con Reachy;
- niveles;
- actividades;
- almacenamiento;

no inventarlo.

Explicar la decisión pendiente antes de implementar una solución irreversible.

Para cambios menores y reversibles, utilizar la solución más simple compatible con la arquitectura existente.

## 28. Funcionalidades futuras

Son áreas previstas, no necesariamente implementadas todavía:

- catálogo formal de actividades;
- niveles específicos por actividad;
- pantalla inicial profesional;
- selección usuario / actividad / nivel;
- arranque coordinado de la app oficial;
- seguimiento de sesión;
- historial;
- resultados;
- decisión profesional de nivel;
- estadísticas;
- administración de actividades;
- configuración de niveles;
- perfiles/contextos temporales;
- memoria;
- exportación;
- despliegue en varios centros/equipos.

No asumir que estas funcionalidades ya existen.

Antes de implementarlas, comprobar el estado real del código.

## 29. Prioridad actual

La prioridad es evolucionar la aplicación local existente de forma controlada.

Orden recomendado:

1. documentar y entender el servidor actual;
2. estabilizar el código existente;
3. mejorar el frontend actual;
4. formalizar actividades y niveles;
5. completar selección usuario → actividad → nivel;
6. integrar preparación/inicio de sesión;
7. registrar cierre y evaluación;
8. crear panel profesional más completo;
9. incorporar funcionalidades adicionales.

## 30. Regla final

AHOOTSA debe crecer por evolución, no por sustitución.

Cuando haya dos posibles soluciones, preferir la que:

1. reutilice más código validado;
2. modifique menos componentes;
3. sea más fácil de probar;
4. sea reversible;
5. mantenga el funcionamiento local;
6. respete la aplicación oficial de Reachy;
7. mantenga al profesional como responsable de las decisiones finales.
