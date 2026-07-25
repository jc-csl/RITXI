# Ahootsa 8 — Análisis actualizado de actividades por niveles y panel profesional

**Versión del documento:** 2.0  
**Fecha de actualización:** 25 de julio de 2026  
**Estado:** arquitectura funcional y técnica de referencia para el desarrollo  
**Aplicación conversacional de referencia:** `reachy_mini_conversation_app` oficial  
**Servidor local existente:** `ahootsa_local_server` 0.11.1, validado  
**Decisión principal:** mantener intacto el código principal `src/` de la aplicación oficial

---

## 0. Resumen ejecutivo

Ahootsa 8 se apoya en la aplicación oficial `reachy_mini_conversation_app` para realizar la conversación en tiempo real, el reconocimiento de voz, la generación de respuestas, la síntesis de voz, los movimientos de Reachy Mini y la ejecución de herramientas.

El proyecto Ahootsa añade actualmente, sin modificar el código principal oficial:

- un perfil externo `ahootsa`;
- instrucciones de personalidad y accesibilidad;
- saludo y voz propios;
- una herramienta externa `ahootsa_dances.py`;
- la actividad local «Vamos a bailar»;
- recursos locales de movimientos y audio;
- documentación de instalación, configuración y validación.

De forma paralela se ha desarrollado y validado un servidor local independiente:

```text
D:\RITXI\AHOOTSA8\ahootsa_local_server
```

Este servidor utiliza:

```text
FastAPI
+
SQLAlchemy
+
SQLite
```

y ya incluye una base funcional para gestionar:

- personas usuarias;
- fichas adaptativas;
- sesiones;
- eventos;
- resúmenes;
- recuerdos o datos estables;
- actividades prototipo;
- contexto unificado;
- snapshots JSON.

La función correcta de `ahootsa_local_server` no es sustituir al modelo conversacional oficial ni decidir las respuestas de Ahootsa. Su papel será actuar como:

> **backend local del panel profesional, gestor de perfiles individuales, niveles, sesiones, seguimiento y análisis posterior.**

La arquitectura definitiva debe mantener dos sistemas separados:

```text
Reachy Mini Conversation App oficial
→ conversa, escucha, habla, mueve el robot y ejecuta herramientas

ahootsa_local_server
→ prepara la sesión, personaliza el contexto, registra el seguimiento,
  analiza resultados y conserva el progreso
```

El profesional mantiene siempre la decisión final sobre:

- el nivel de cada actividad;
- la interpretación de respuestas abiertas;
- los apoyos necesarios;
- la subida, mantenimiento o bajada de nivel;
- las observaciones que forman parte del historial.

---

## 1. Finalidad del documento

Este documento sustituye y amplía la versión inicial de:

```text
ANALISIS_ACTIVIDADES_POR_NIVELES_Y_PANEL_PROFESIONAL.md
```

Su finalidad es dejar registrada la situación real de Ahootsa 8 y servir como guía para desarrollar progresivamente:

1. perfiles individualizados de personas usuarias;
2. actividades de comunicación con tres niveles;
3. un panel profesional local;
4. seguimiento por usuario y por actividad;
5. preparación automática del contexto de cada sesión;
6. registro de eventos y transcripción;
7. análisis posterior de la sesión;
8. recomendación orientativa de nivel;
9. validación final por parte del profesional;
10. integración no invasiva con la aplicación oficial.

Este documento distingue expresamente entre:

- lo que ya está implementado;
- lo que existe como prototipo;
- lo que debe reorientarse;
- lo que todavía debe desarrollarse;
- lo que no debe incorporarse por ahora.

---

## 2. Decisiones de arquitectura que deben mantenerse

### 2.1. El código principal oficial no se modifica

La carpeta principal:

```text
src/
```

de `reachy_mini_conversation_app` se mantiene sin modificaciones propias de Ahootsa.

Esta decisión permite:

- aceptar actualizaciones oficiales;
- comparar fácilmente la instalación con el repositorio original;
- reducir conflictos durante actualizaciones;
- aislar los desarrollos específicos de Ahootsa;
- facilitar la reinstalación en equipos nuevos;
- mantener una marcha atrás clara.

Las ampliaciones deben realizarse mediante:

```text
external_content/
ahootsa_local_server/
runtime/
documentacion/
scripts/
```

Solo se valorará modificar `src/` si una función imprescindible no puede resolverse mediante mecanismos externos y después de documentar expresamente el motivo, el impacto y la marcha atrás.

### 2.2. No se incorpora Ollama en esta versión

La versión actual de Ahootsa 8 no utiliza Ollama.

La conversación se mantiene dentro del funcionamiento oficial configurado mediante:

```text
HF_REALTIME_CONNECTION_MODE="deployed"
```

No se debe introducir un segundo modelo conversacional local dentro de `ahootsa_local_server`.

### 2.3. El servidor local no sustituye a la Conversation App

`ahootsa_local_server` no debe encargarse de:

- generar la respuesta hablada principal;
- sustituir el backend realtime;
- controlar el diálogo turno a turno;
- imitar el sistema de herramientas oficial;
- decidir de manera autónoma la evaluación profesional;
- ejecutar una segunda conversación paralela.

Debe encargarse de:

- seleccionar y mantener el usuario activo;
- gestionar su ficha;
- gestionar actividades, niveles y progreso;
- preparar el contexto previo;
- registrar eventos;
- importar y analizar los registros disponibles;
- mostrar información al panel profesional;
- guardar la decisión final del monitor.

### 2.4. El nivel se guarda por actividad

No se asignará a cada persona un único nivel general.

Ejemplo:

```text
Usuario: Ane
├── Pedir ayuda: Intermedio
├── Expresar preferencias: Avanzado
├── Emociones y estados: Inicial
├── Iniciar conversación: Intermedio
└── Contar una experiencia: Inicial
```

La misma persona puede necesitar distintos apoyos según la competencia comunicativa trabajada.

### 2.5. La decisión final corresponde al profesional

La aplicación puede calcular indicadores y generar recomendaciones, pero no debe presentar sus resultados como una evaluación clínica ni modificar automáticamente el nivel definitivo.

El sistema debe mostrar siempre de forma separada:

```text
Nivel actual
Nivel recomendado por el sistema
Decisión profesional
```

### 2.6. «Vamos a bailar» se mantiene como actividad motivacional

La actividad «Vamos a bailar» puede utilizarse como:

- motivación;
- elección personal;
- descanso;
- refuerzo positivo;
- transición;
- cierre de sesión.

No debe utilizarse como indicador principal del nivel comunicativo.

---

## 3. Situación actual del proyecto

## 3.1. Aplicación oficial

La base conversacional es la aplicación oficial:

```text
reachy_mini_conversation_app
```

Responsabilidades actuales:

- captura de audio;
- detección de voz;
- transcripción;
- conversación realtime;
- respuesta hablada;
- voz;
- emociones y movimientos;
- herramientas;
- control del robot;
- interfaz oficial.

## 3.2. Perfil externo Ahootsa

La personalización general del robot se encuentra en:

```text
external_content/
└── external_profiles/
    └── ahootsa/
        ├── instructions.txt
        ├── greeting.txt
        ├── tools.txt
        └── voice.txt
```

Este perfil define el comportamiento general de Ahootsa, pero no representa la ficha de una persona usuaria concreta.

## 3.3. Herramienta externa y actividad de baile

La herramienta propia se encuentra en:

```text
external_content/
└── external_tools/
    └── ahootsa_dances.py
```

La biblioteca local se encuentra en:

```text
external_content/
└── activities/
    └── vamos_a_bailar/
        ├── actividad.json
        ├── catalogo_bailes.json
        ├── local_recorded_moves.py
        ├── inventario_recursos_locales.json
        ├── verificar_biblioteca_local.py
        └── dataset/
```

La versión funcional dispone de herramientas para:

```text
play_ahootsa_dance
stop_ahootsa_dance
```

El catálogo se comunica verbalmente siguiendo las instrucciones del perfil.

## 3.4. Configuración actual

La configuración inicial utiliza:

```text
REALTIME_TRANSCRIPTION_LANGUAGE="es"
HF_REALTIME_CONNECTION_MODE="deployed"
REACHY_MINI_CUSTOM_PROFILE=ahootsa
REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY=./external_content/external_profiles
REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY=./external_content/external_tools
AUTOLOAD_EXTERNAL_TOOLS=false
```

Consecuencias:

- la transcripción está configurada en español;
- el perfil seleccionado es `ahootsa`;
- los perfiles y herramientas se cargan desde directorios externos;
- las tools se habilitan explícitamente desde `tools.txt`;
- no se cargan automáticamente todas las herramientas externas.

## 3.5. Servidor local existente

Carpeta de referencia:

```text
D:\RITXI\AHOOTSA8\ahootsa_local_server
```

Versión validada:

```text
0.11.1
```

Tecnologías:

```text
FastAPI
SQLAlchemy
SQLite
PowerShell
JSON
```

Base de datos local prevista por la configuración existente:

```text
data/ahootsa.db
```

Snapshots:

```text
data/context_snapshots/
```

## 3.6. Tablas existentes

### `users`

Contiene:

- identificador interno;
- identificador externo;
- nombre;
- nombre preferido;
- idioma;
- notas;
- estado activo;
- fecha de creación.

### `user_profiles`

Contiene:

- estilo de comunicación;
- velocidad de habla;
- tiempo de espera;
- modo de interacción preferido;
- refuerzo preferido;
- intereses;
- temas que evitar;
- notas de accesibilidad;
- máximo de instrucciones por turno.

### `sessions`

Contiene:

- persona usuaria;
- quién inicia la sesión;
- estado;
- inicio;
- final;
- resumen.

### `session_events`

Contiene un registro genérico de:

- tipo de evento;
- fuente;
- actividad;
- texto;
- valor numérico;
- éxito;
- metadatos JSON;
- fecha y hora.

### `memory_items`

Contiene datos estables asociados al usuario:

- categoría;
- contenido;
- fuente;
- importancia;
- estado activo;
- fechas.

En la arquitectura final se utilizará principalmente para información estable y no sensible, preferentemente introducida o validada por un profesional.

## 3.7. Módulos existentes

### `models.py`

Define los modelos actuales de la base de datos.

### `schemas.py`

Define los contratos de entrada y salida de la API.

### `main.py`

Expone endpoints para usuarios, perfiles, sesiones, eventos, resúmenes, memoria, actividades y contexto.

### `conversation_manager.py`

Es un prototipo determinista que propone acciones según silencios, errores, pistas y estado de actividad.

**Reorientación necesaria:** no debe utilizarse para dirigir la conversación oficial. Puede conservarse temporalmente como experimento o transformarse más adelante en un servicio de recomendación para el panel.

### `activity_engine.py`

Registra actualmente dos actividades prototipo:

```text
emotions
preferences
```

**Reorientación necesaria:** debe evolucionar hacia un gestor de definiciones, niveles, ejercicios y estado de actividad. La evaluación final no debe depender exclusivamente de este motor.

### `context_manager.py`

Construye un contexto unificado con:

- sesión;
- usuario;
- perfil;
- memoria;
- actividad;
- estado;
- eventos recientes;
- contadores.

También genera snapshots JSON.

**Aprovechamiento previsto:** será la base del futuro generador de contexto de sesión y del objeto que consuma el panel.

## 3.8. Estado de cada componente

| Componente | Estado | Decisión |
|---|---|---|
| Aplicación oficial | Operativa | Mantener sin modificar |
| Perfil externo Ahootsa | Operativo | Mantener y consolidar |
| Tool de baile | Operativa | Mantener |
| «Vamos a bailar» | Operativa | Mantener como motivación/refuerzo |
| Servidor FastAPI | Validado | Reutilizar como backend profesional |
| SQLite/SQLAlchemy | Validado | Mantener |
| Usuarios y perfiles | Implementados | Ampliar |
| Sesiones y eventos | Implementados | Ampliar |
| Memoria permanente | Implementada | Uso manual/controlado |
| Gestor conversacional local | Prototipo | No usar para sustituir la conversación oficial |
| Motor de actividades local | Prototipo | Reorientar a actividades, niveles y ejercicios |
| Gestor de contexto | Implementado | Aprovechar para generar contexto previo |
| Panel profesional | Diseño | Pendiente de implementación |
| Integración con logs oficiales | No validada | Realizar prueba técnica específica |
| Análisis posterior | Pendiente | Implementar por fases |
| Recomendación de nivel | Pendiente | Implementar con validación profesional |

---

## 4. Arquitectura objetivo

```text
┌───────────────────────────────────────────────────────────────┐
│                       PANEL PROFESIONAL                       │
│                                                               │
│ Usuario · ficha · actividad · nivel · audio · seguimiento     │
│ observaciones · resumen · recomendación · decisión final      │
└───────────────────────────────┬───────────────────────────────┘
                                │ API local
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                    ahootsa_local_server                       │
│                                                               │
│ Usuarios y perfiles                                           │
│ Actividades y tres niveles                                    │
│ Progreso por usuario y actividad                              │
│ Sesiones y eventos                                            │
│ Preparación del contexto                                      │
│ Importación de logs/transcripción                             │
│ Análisis posterior                                            │
│ Recomendación de nivel                                        │
│ SQLite                                                        │
└───────────────┬────────────────────────────────┬──────────────┘
                │ contexto previo                │ logs/eventos
                ▼                                ▲
┌───────────────────────────────────────────────────────────────┐
│             Reachy Mini Conversation App oficial              │
│                                                               │
│ Backend realtime · ASR · LLM · TTS · herramientas · Reachy    │
│ Perfil externo Ahootsa · tool de baile · interfaz oficial     │
└───────────────────────────────────────────────────────────────┘
```

La relación entre ambos sistemas debe ser asimétrica:

```text
El servidor prepara y registra
La app oficial conversa y actúa
El servidor analiza después
El profesional decide
```

---

## 5. Dos tipos de perfil diferentes

## 5.1. Perfil conversacional general

Directorio:

```text
external_profiles/ahootsa/
```

Representa a Ahootsa como robot:

- identidad;
- tono;
- idioma;
- seguridad;
- accesibilidad general;
- herramientas habilitadas;
- comportamiento durante el baile.

## 5.2. Ficha individual de usuario

Se guarda en SQLite y representa a una persona concreta:

```text
Nombre preferido
Idioma
Ritmo
Tiempo de espera
Longitud de respuesta recomendada
Máximo de opciones
Intereses
Apoyos
Refuerzo preferido
Temas que evitar
Observaciones profesionales
Progreso por actividad
```

## 5.3. Contexto temporal de sesión

Se genera antes de arrancar una sesión y combina:

```text
Perfil general Ahootsa
+
ficha individual
+
actividad seleccionada
+
nivel seleccionado
+
objetivo de sesión
+
apoyos autorizados
+
progreso anterior relevante
```

Ejemplo:

```text
La persona usuaria se llama Ane.

Utiliza su nombre preferido, Ane.
Habla con frases breves y claras.
Formula una sola pregunta por turno.
Espera al menos 8 segundos antes de repetir.
Ofrece como máximo dos opciones cuando necesite apoyo.

Actividad actual: Pedir ayuda.
Nivel actual: Intermedio.
Objetivo: formular una petición funcional breve en una situación cotidiana.

Refuerza los intentos sin exagerar.
No decidas el cambio de nivel.
El profesional registrará el resultado.
```

---

## 6. Estrategia para adaptar la conversación sin modificar `src/`

## 6.1. Perfil base estable

El perfil original debe permanecer estable:

```text
external_content/external_profiles/ahootsa/
```

No se debe sobrescribir con datos de una persona concreta.

## 6.2. Perfil temporal generado

Antes de iniciar la Conversation App, el servidor puede preparar un perfil temporal:

```text
runtime/
└── generated_profiles/
    └── ahootsa_session_000123/
        ├── instructions.txt
        ├── greeting.txt
        ├── tools.txt
        └── voice.txt
```

El servidor generaría:

```text
instructions.txt =
instrucciones base
+
bloque de usuario
+
bloque de actividad
+
bloque de nivel
+
reglas específicas de sesión
```

Los archivos `tools.txt` y `voice.txt` pueden copiarse del perfil base salvo que una actividad requiera una selección distinta de herramientas.

## 6.3. Contexto estructurado independiente

Además del perfil que consume la app oficial, debe guardarse:

```text
runtime/
└── sessions/
    └── 000123/
        └── session_context.json
```

Ejemplo:

```json
{
  "session_id": 123,
  "user_external_id": "ANE-001",
  "activity": "pedir_ayuda",
  "level": "intermediate",
  "started_by": "professional",
  "supports": {
    "max_options": 2,
    "repeat_allowed": true,
    "extra_wait_seconds": 3
  }
}
```

Este archivo no necesita ser interpretado por la aplicación oficial. Sirve para:

- tools externas;
- diagnóstico;
- importación posterior;
- trazabilidad;
- reconstrucción de la sesión.

## 6.4. Variables de entorno de la sesión

El lanzador podrá establecer temporalmente:

```text
REACHY_MINI_CUSTOM_PROFILE=ahootsa_session_000123
REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY=<ruta_runtime_generated_profiles>
REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY=<ruta_external_content_external_tools>
```

Esta técnica debe validarse mediante una prueba aislada antes de incorporarse al panel.

Debe comprobarse especialmente:

- si los ajustes guardados desde la interfaz oficial prevalecen sobre `.env`;
- si el perfil se carga únicamente al inicio;
- si una ruta absoluta funciona mejor que una ruta relativa;
- si puede reiniciarse la app sin dejar procesos anteriores;
- si el perfil temporal aparece correctamente en los logs.

## 6.5. Herramientas genéricas, no herramientas por usuario

No se debe crear una tool distinta para cada persona.

Las futuras tools deben ser genéricas y trabajar con la sesión activa:

```text
start_ahootsa_activity
record_activity_event
finish_ahootsa_activity
get_active_session_context
```

La identificación real se resuelve mediante:

```text
session_id
user_id
activity_id
level
exercise_id
```

El servidor mantiene la fuente de verdad.

---

## 7. Flujo completo de una sesión

## 7.1. Antes de la conversación

```text
1. El profesional abre el panel.
2. Selecciona la persona usuaria.
3. Revisa la ficha y el progreso anterior.
4. Selecciona una actividad.
5. Confirma el nivel.
6. Define apoyos o un objetivo concreto.
7. El servidor crea la sesión.
8. El servidor genera el contexto temporal.
9. El lanzador inicia la Conversation App con ese perfil.
10. Se comprueban micrófono, voz y estado del robot.
```

Datos mínimos al iniciar:

```text
usuario
profesional
actividad
nivel
objetivo
apoyos
fecha y hora
perfil temporal
ruta del log
```

## 7.2. Durante la conversación

La aplicación oficial:

- escucha;
- transcribe;
- conversa;
- habla;
- ejecuta herramientas;
- mueve Reachy.

El servidor:

- mantiene la sesión activa;
- recibe eventos de las tools externas cuando existan;
- registra acciones del profesional;
- conserva marcas temporales;
- no genera la respuesta conversacional principal.

El profesional puede registrar:

```text
Respuesta adecuada
Respuesta parcial
Respuesta incorrecta
Sin respuesta
Dar pista
Repetir instrucción
Dar ejemplo
Pausar
Siguiente ejercicio
Finalizar
```

## 7.3. Al finalizar

```text
1. El profesional termina la actividad.
2. Se cierra o separa el registro de la sesión.
3. El servidor importa los logs disponibles.
4. Se normalizan turnos y eventos.
5. Se calculan indicadores.
6. Se genera un resumen.
7. Se propone una recomendación de nivel.
8. El profesional revisa la información.
9. Añade observaciones.
10. Decide mantener, subir o bajar.
11. Se actualiza el progreso por actividad.
12. Se cierra la sesión.
```

---

## 8. Modelo de tres niveles

## 8.1. Nivel inicial

### Características

- frases muy breves;
- una instrucción por turno;
- preguntas cerradas;
- dos opciones como máximo;
- repetición frecuente;
- ejemplos claros;
- apoyos visuales cuando existan;
- refuerzo positivo;
- sesiones cortas;
- mayor tiempo de espera.

### Objetivos comunicativos

- responder sí o no;
- elegir entre dos opciones;
- nombrar un objeto, persona o emoción;
- pedir ayuda con una frase modelo;
- expresar una preferencia básica;
- completar una frase;
- responder a un saludo.

### Papel del profesional

- repetir;
- ofrecer dos opciones;
- dar una pista;
- modelar una frase;
- aceptar una respuesta parcial;
- decidir cuándo detener la actividad.

## 8.2. Nivel intermedio

### Características

- preguntas abiertas sencillas;
- dos o tres opciones;
- respuestas de varias palabras;
- dos o tres turnos;
- secuencias breves;
- menos ayudas directas;
- mayor autonomía;
- justificaciones breves.

### Objetivos comunicativos

- explicar una preferencia;
- pedir ayuda en una situación cotidiana;
- mantener varios turnos;
- responder y formular una pregunta;
- describir una acción;
- elegir y justificar;
- relacionar una emoción y una situación.

### Papel del profesional

- observar comprensión;
- valorar autonomía;
- registrar pistas;
- valorar mantenimiento del turno;
- controlar motivación;
- decidir si se mantiene el nivel.

## 8.3. Nivel avanzado

### Características

- conversación más espontánea;
- respuestas completas;
- role-play;
- narración;
- resolución de situaciones;
- pocos apoyos;
- varios turnos;
- cambio de tema controlado;
- opiniones y argumentos sencillos.

### Objetivos comunicativos

- iniciar y mantener una conversación;
- explicar un problema;
- pedir información;
- contar una experiencia;
- dar una opinión;
- defender una elección;
- resolver una situación social;
- adaptar el mensaje al interlocutor.

### Papel del profesional

- intervenir menos;
- reconducir;
- registrar estrategias;
- valorar generalización;
- decidir el siguiente objetivo;
- confirmar o rechazar una subida.

---

## 9. Actividades comunicativas iniciales

## 9.1. Pedir ayuda

### Inicial

- escoger entre dos frases;
- completar «Necesito…»;
- utilizar una petición modelo.

### Intermedio

- explicar brevemente el problema;
- formular una petición funcional;
- responder a una pregunta de seguimiento.

### Avanzado

- role-play;
- pedir ayuda en distintos contextos;
- explicar el problema y confirmar que ha sido comprendido.

## 9.2. Expresar preferencias

### Inicial

- elegir entre dos opciones;
- responder «me gusta» o «no me gusta».

### Intermedio

- elegir entre tres opciones;
- explicar una razón breve;
- responder a una pregunta adicional.

### Avanzado

- comparar;
- justificar;
- preguntar por la preferencia de otra persona;
- mantener una conversación sobre intereses.

## 9.3. Iniciar y mantener una conversación

### Inicial

- saludar;
- decir el nombre;
- responder una pregunta.

### Intermedio

- saludar;
- devolver una pregunta;
- mantener dos o tres turnos.

### Avanzado

- iniciar espontáneamente;
- mantener el tema;
- cambiar de tema;
- mostrar acuerdo, duda o interés.

## 9.4. Emociones y estados

### Inicial

- reconocer emociones básicas;
- elegir entre dos opciones;
- nombrar un estado.

### Intermedio

- explicar cómo se siente;
- relacionar emoción y situación.

### Avanzado

- expresar emociones más complejas;
- explicar necesidades;
- comparar estados;
- proponer estrategias de comunicación.

## 9.5. Contar una experiencia

### Inicial

- responder preguntas concretas;
- completar frases;
- ordenar dos acciones.

### Intermedio

- contar algo reciente;
- ordenar dos o tres acciones;
- responder preguntas.

### Avanzado

- narración con inicio, desarrollo y cierre;
- incorporar detalles relevantes;
- responder preguntas espontáneas.

---

## 10. Formato recomendado para nuevas actividades

Las actividades comunicativas deben almacenarse fuera del código principal.

Estructura propuesta:

```text
external_content/
└── activities/
    ├── vamos_a_bailar/
    ├── pedir_ayuda/
    │   ├── actividad.json
    │   ├── levels/
    │   │   ├── initial.json
    │   │   ├── intermediate.json
    │   │   └── advanced.json
    │   └── resources/
    └── emociones/
```

Ejemplo conceptual de `actividad.json`:

```json
{
  "id": "pedir_ayuda",
  "title": "Pedir ayuda",
  "type": "communication",
  "version": "1.0",
  "levels": [
    "initial",
    "intermediate",
    "advanced"
  ],
  "professional_evaluation": true,
  "automatic_evaluation": "assisted",
  "can_use_dance_as_reinforcement": true
}
```

Ejemplo conceptual de `intermediate.json`:

```json
{
  "level": "intermediate",
  "max_options": 3,
  "max_instructions_per_turn": 1,
  "objectives": [
    "formular una petición funcional breve",
    "explicar el problema con varias palabras"
  ],
  "exercises": [
    {
      "id": "help_intermediate_01",
      "situation": "No alcanzas un objeto.",
      "prompt": "¿Cómo pedirías ayuda?",
      "expected_intents": [
        "pedir ayuda"
      ],
      "supports": [
        "repeat",
        "hint",
        "model_phrase"
      ]
    }
  ]
}
```

Estos formatos son una propuesta de diseño. Deben validarse antes de fijarlos como esquema definitivo.

---

## 11. Diseño del panel profesional

![Diseño conceptual del panel profesional Ahootsa](panel_de_control_profesional_ahootsa.png)

El panel reúne seis áreas principales.

## 11.1. Usuario activo

Debe permitir:

- seleccionar una persona;
- consultar nombre preferido;
- consultar ritmo;
- consultar longitud de respuesta;
- consultar intereses;
- consultar apoyos;
- crear ficha;
- editar ficha;
- consultar evolución.

## 11.2. Conversación

Objetivo:

- mostrar la conversación o el registro disponible;
- conocer si el sistema escucha;
- mostrar la última transcripción;
- mostrar la respuesta de Ahootsa;
- permitir un mensaje profesional cuando se implemente de forma segura;
- repetir o pausar cuando la integración lo permita.

La transcripción en tiempo real depende de que la app oficial exponga o registre esos datos de forma accesible. Esta capacidad todavía debe validarse.

## 11.3. Actividad y nivel

Debe permitir:

- seleccionar actividad;
- seleccionar Inicial, Intermedio o Avanzado;
- mostrar el último nivel;
- mostrar el nivel recomendado;
- iniciar;
- pausar;
- pasar al siguiente ejercicio;
- finalizar.

## 11.4. Audio y micrófono

El diseño contempla:

- estado del micrófono;
- detección de voz;
- entrada;
- salida;
- ruido;
- volumen;
- ganancia;
- sensibilidad VAD.

No debe asumirse que todos estos parámetros pueden controlarse desde el panel sin modificar la app oficial. Primero deben clasificarse como:

```text
Visible mediante API o log
Controlable externamente
Solo disponible en la interfaz oficial
No disponible actualmente
```

## 11.5. Seguimiento rápido

Botones previstos:

```text
Respuesta adecuada
Respuesta parcial
Incorrecta
Sin respuesta
Dar pista
Repetir instrucción
Dar ejemplo
Pausar
Siguiente ejercicio
Finalizar
```

Cada pulsación debe crear un evento con:

```text
session_id
session_activity_id
exercise_id
event_type
timestamp
professional_id
optional_note
```

## 11.6. Observaciones y resumen

Debe incluir:

- observación profesional;
- resumen automático;
- métricas;
- recomendación;
- mantener;
- subir;
- bajar;
- confirmación de guardado.

---

## 12. Registro de conversación, transcripción y logs

## 12.1. Situación actual

Todavía no se ha validado que la aplicación oficial guarde en un archivo estructurado:

- todos los turnos del usuario;
- todas las respuestas del asistente;
- tiempos exactos;
- llamadas completas a tools;
- estados de audio.

Por ello, la integración debe comenzar con una prueba técnica de observación y no con una modificación del núcleo.

## 12.2. Fuentes posibles, por prioridad

### Opción A — Logs oficiales existentes

Preferida cuando contengan la información necesaria.

Ventajas:

- no modifica código;
- sigue el comportamiento oficial;
- facilita actualizaciones.

### Opción B — Redirección de la salida del proceso

El lanzador puede guardar la salida de pantalla en un log asociado a la sesión.

Ejemplo conceptual:

```powershell
<lanzamiento_oficial> *>> logs\conversation_app\session_000123_runtime.log
```

Debe comprobarse que la redirección no altere el comportamiento ni pierda mensajes.

### Opción C — Eventos enviados por tools externas

Las tools propias pueden registrar en el servidor:

- actividad iniciada;
- ejercicio;
- baile iniciado;
- baile detenido;
- refuerzo utilizado;
- actividad finalizada;
- error.

Ejemplo conceptual:

```text
POST http://127.0.0.1:8100/sessions/active/events
```

Esta opción no proporciona por sí sola toda la transcripción, pero sí eventos fiables de actividad.

### Opción D — Adaptador externo

Un proceso independiente puede:

- lanzar la app oficial;
- capturar su salida;
- detectar su finalización;
- conocer la ruta del log;
- informar al servidor.

No debe incorporarse dentro de `src/`.

## 12.3. Formato normalizado

El servidor debe transformar las fuentes disponibles a un formato común:

```json
{"type":"assistant_message","text":"¿Cómo pedirías ayuda?","timestamp":"10:25:18"}
{"type":"user_transcript","text":"¿Me ayudas, por favor?","timestamp":"10:25:24"}
{"type":"professional_mark","value":"adequate","timestamp":"10:25:25"}
{"type":"hint_given","exercise_id":"help_02","timestamp":"10:26:03"}
```

Formato recomendado de archivo:

```text
runtime/sessions/000123/normalized_events.jsonl
```

## 12.4. Calidad del dato

Cada evento importado debe indicar su origen:

```text
official_log
external_tool
professional_panel
derived_analysis
manual_import
```

Los datos derivados nunca deben confundirse con una valoración profesional.

---

## 13. Indicadores de seguimiento

## 13.1. Indicadores directamente registrables

Son los más fiables:

- número de intentos;
- respuestas adecuadas marcadas por el profesional;
- respuestas parciales;
- incorrectas;
- sin respuesta;
- pistas;
- repeticiones;
- ejemplos;
- pausas;
- ejercicios completados;
- duración;
- decisión final.

## 13.2. Indicadores temporales

Cuando los logs lo permitan:

- tiempo hasta comenzar a responder;
- duración de la intervención;
- tiempo total por ejercicio;
- tiempo medio de respuesta;
- número de silencios;
- tiempo acumulado de espera.

Debe indicarse si el tiempo es:

```text
exacto
estimado
no disponible
```

No se deben calcular tiempos aparentemente precisos a partir de marcas insuficientes.

## 13.3. Indicadores de participación

- número de intervenciones;
- número de turnos mantenidos;
- longitud media;
- preguntas realizadas;
- respuestas relacionadas con el tema;
- ejercicios iniciados;
- ejercicios finalizados;
- abandonos;
- cambios de actividad.

## 13.4. Indicadores de apoyos

- pistas por ejercicio;
- repeticiones;
- frases modelo;
- opciones ofrecidas;
- reformulaciones;
- intervención profesional;
- necesidad de bajar dificultad durante la sesión.

## 13.5. Indicadores de calidad comunicativa

Solo deben automatizarse con prudencia:

- presencia de una intención comunicativa;
- uso de palabras objetivo;
- respuesta relacionada con la pregunta;
- frase completa;
- justificación;
- mantenimiento del tema;
- secuencia narrativa;
- pregunta espontánea.

La evaluación automática puede ser razonable en ejercicios cerrados. En respuestas abiertas debe presentarse como una observación orientativa.

## 13.6. Información que no debe deducirse automáticamente

- diagnóstico;
- capacidad general;
- estado clínico;
- inteligencia;
- evolución terapéutica;
- intención emocional compleja;
- aptitud para una actividad fuera del contexto observado.

---

## 14. Recomendación de nivel

## 14.1. Principio general

La recomendación debe basarse en varias sesiones, no en una respuesta aislada.

## 14.2. Señales para valorar subida

- rendimiento adecuado y estable;
- pocas ayudas;
- buena comprensión;
- tiempos razonables para esa persona;
- respuestas más completas;
- mantenimiento de turnos;
- generalización a ejercicios diferentes;
- al menos dos sesiones consistentes.

## 14.3. Señales para mantener

- progreso parcial;
- apoyos moderados;
- variabilidad;
- actividad completada con ayuda;
- objetivos todavía no generalizados.

## 14.4. Señales para bajar temporalmente

- bloqueo;
- frustración;
- baja comprensión;
- demasiadas ayudas;
- abandono repetido;
- tiempos excesivos respecto al patrón personal;
- dificultad sostenida en varios ejercicios.

## 14.5. Ejemplo de resumen

```text
Actividad: Pedir ayuda
Nivel actual: Intermedio
Sesiones consideradas: 3

Intentos: 18
Adecuadas: 13
Parciales: 3
Incorrectas: 1
Sin respuesta: 1
Pistas: 4
Repeticiones: 2

Recomendación del sistema:
Mantener Intermedio.

Motivos:
- rendimiento global favorable;
- todavía necesita pistas en situaciones nuevas;
- mantiene dos turnos, pero no siempre formula una pregunta espontánea.

Decisión profesional:
[ Mantener ] [ Subir ] [ Bajar temporalmente ]
```

## 14.6. Configuración

Los criterios deben almacenarse como configuración y poder ajustarse por actividad.

Nunca se debe presentar un porcentaje aislado como criterio definitivo.

---

## 15. Datos que debe guardar el sistema

## 15.1. Ficha de usuario

Datos existentes y ampliables:

- identificador;
- nombre;
- nombre preferido;
- idioma;
- estilo comunicativo;
- velocidad;
- tiempo de espera;
- máximo de instrucciones;
- máximo de opciones;
- longitud de respuesta recomendada;
- intereses;
- temas que evitar;
- apoyos;
- refuerzo;
- observaciones;
- estado activo.

## 15.2. Actividades

- identificador;
- título;
- descripción;
- categoría;
- versión;
- estado;
- ruta de configuración;
- si admite evaluación automática;
- si requiere evaluación profesional;
- si permite refuerzo de baile.

## 15.3. Niveles

- actividad;
- nivel;
- objetivos;
- instrucciones;
- máximo de opciones;
- apoyos;
- dificultad;
- criterios orientativos;
- versión.

## 15.4. Progreso por usuario y actividad

- usuario;
- actividad;
- nivel actual;
- último nivel;
- nivel recomendado;
- sesiones;
- fecha;
- métricas acumuladas;
- decisión profesional;
- motivo;
- próximo objetivo.

## 15.5. Actividad dentro de una sesión

Una sesión puede contener más de una actividad. Debe existir una entidad específica para cada actividad trabajada:

- sesión;
- actividad;
- nivel;
- inicio;
- final;
- estado;
- número de ejercicios;
- métricas;
- recomendación;
- decisión.

## 15.6. Observaciones profesionales

- usuario;
- sesión;
- actividad;
- profesional;
- texto;
- categoría;
- fecha;
- visibilidad;
- decisión de nivel.

## 15.7. Análisis

- origen del log;
- versión del analizador;
- métricas;
- advertencias;
- datos no disponibles;
- recomendación;
- fecha.

---

## 16. Modelo de datos recomendado

## 16.1. Tablas existentes que se conservan

```text
users
user_profiles
sessions
session_events
memory_items
```

## 16.2. Tablas nuevas prioritarias

```text
activities
activity_levels
user_activity_progress
session_activities
professional_notes
```

## 16.3. Tablas posteriores

```text
activity_exercises
session_analyses
level_recommendations
professionals
```

## 16.4. Migración progresiva

No se deben eliminar las tablas actuales.

Orden recomendado:

```text
1. Crear activities.
2. Crear activity_levels.
3. Crear user_activity_progress.
4. Crear session_activities.
5. Crear professional_notes.
6. Poblar el catálogo inicial.
7. Mantener session_events como registro transversal.
8. Añadir análisis cuando la captura de logs esté validada.
```

---

## 17. Aprovechamiento y reorientación de `ahootsa_local_server`

## 17.1. Componentes que deben conservarse

```text
FastAPI
SQLAlchemy
SQLite
users
user_profiles
sessions
session_events
memory_items
resúmenes
context snapshots
scripts de validación
backups
```

## 17.2. `context_manager.py`

Debe evolucionar hacia:

```text
session_context_service.py
```

Responsabilidades futuras:

- construir contexto estructurado;
- seleccionar datos relevantes;
- generar snapshot;
- preparar el bloque de instrucciones;
- evitar información sensible;
- mantener trazabilidad.

No es necesario renombrarlo ahora, porque el módulo está validado y todavía no se ha cerrado la interfaz definitiva.

## 17.3. `conversation_manager.py`

No debe dirigir la conversación oficial.

Opciones futuras:

1. conservarlo como prototipo deshabilitado;
2. convertirlo en `support_recommendation_service.py`;
3. reutilizar parte de sus reglas para detectar:
   - demasiados silencios;
   - demasiadas pistas;
   - posible necesidad de pausa;
   - dificultad sostenida.

No se recomienda eliminarlo inmediatamente porque contiene lógica aprovechable, pero sus endpoints no deben considerarse parte del flujo definitivo.

## 17.4. `activity_engine.py`

Debe reorientarse a:

- cargar actividades JSON;
- cargar niveles;
- conocer el ejercicio actual;
- registrar estado;
- validar respuestas cerradas;
- preparar metadatos;
- no sustituir la valoración profesional.

Las actividades `emotions` y `preferences` actuales se consideran prototipos técnicos.

## 17.5. `memory_items`

Uso recomendado:

- intereses estables;
- preferencias;
- apoyos útiles;
- información comunicativa validada;
- datos introducidos por un profesional.

No debe realizarse todavía una extracción automática indiscriminada desde la conversación.

---

## 18. Adaptaciones que conviene realizar ahora

## 18.1. Adaptación documental

Se adopta este documento como referencia principal para el panel profesional y el seguimiento.

Debe guardarse en:

```text
documentacion/
ANALISIS_ACTIVIDADES_POR_NIVELES_Y_PANEL_PROFESIONAL.md
```

y copiarse también en:

```text
ahootsa_local_server/docs/
```

## 18.2. Congelar la versión 0.11.1

La versión validada del servidor debe conservarse como baseline:

```text
ahootsa_local_server 0.11.1
```

Antes de continuar debe realizarse una copia o etiqueta de esta situación.

## 18.3. No renombrar módulos todavía

No conviene cambiar ahora:

```text
conversation_manager.py
activity_engine.py
context_manager.py
```

porque:

- están importados por `main.py`;
- los endpoints actuales están validados;
- todavía no se ha definido la API de integración final;
- un cambio nominal aportaría poco y podría romper la instalación.

La incoherencia se corrige por ahora mediante documentación clara y evitando usar esos módulos como sustitutos del sistema oficial.

## 18.4. Crear estructura no invasiva

Conviene disponer de:

```text
D:\RITXI\AHOOTSA8\
├── documentacion/
├── logs/
│   └── conversation_app/
├── runtime/
│   ├── sessions/
│   ├── generated_profiles/
│   ├── imports/
│   └── exports/
└── ahootsa_local_server/
    └── docs/
```

Esta estructura no modifica la app oficial ni la base de datos.

## 18.5. No modificar `.env` todavía

La configuración actual funciona con el perfil base `ahootsa`.

El cambio a perfiles temporales debe realizarse más adelante mediante un lanzador controlado y después de validar el comportamiento de la aplicación oficial.

## 18.6. Consolidar las instrucciones del perfil

Existe documentación histórica acumulada en `instructions.txt`.

Antes de incorporar actividades por niveles conviene realizar una fase específica de consolidación para:

- eliminar reglas antiguas que contradicen funciones ya activas;
- utilizar únicamente los nombres actuales de tools;
- separar reglas generales y reglas de actividad;
- mantener el perfil base más breve;
- preparar bloques generados de sesión.

Esta adaptación debe hacerse con pruebas conversacionales y de baile, no mediante una edición masiva sin validación.

---

## 19. Estructura lógica recomendada para futuras versiones del servidor

No se aplica todavía como cambio de código, pero se adopta como objetivo:

```text
ahootsa_local_server/
├── app/
│   ├── api/
│   ├── domain/
│   ├── services/
│   │   ├── session_context_service.py
│   │   ├── activity_service.py
│   │   ├── progress_service.py
│   │   ├── log_import_service.py
│   │   ├── session_analysis_service.py
│   │   └── level_recommendation_service.py
│   ├── adapters/
│   │   └── official_conversation_app_adapter.py
│   ├── models.py
│   ├── schemas.py
│   └── main.py
├── data/
├── docs/
├── tests/
└── scripts/
```

La migración se realizará de forma incremental para no romper los pasos ya validados.

---

## 20. Plan de desarrollo recomendado

## Fase P0 — Consolidación de arquitectura

Objetivos:

- adoptar este documento;
- congelar 0.11.1;
- crear carpetas de runtime y logs;
- consolidar el perfil Ahootsa;
- no añadir funcionalidad conversacional paralela.

Criterio de aceptación:

```text
Arquitectura documentada
Servidor actual intacto
Perfil y baile siguen funcionando
```

## Fase P1 — Modelo de actividades y progreso

Objetivos:

- crear tablas nuevas;
- catálogo de actividades;
- tres niveles;
- progreso por usuario y actividad;
- observaciones profesionales.

Criterio:

```text
Se puede asignar a Ane un nivel distinto en cada actividad.
```

## Fase P2 — Panel profesional básico

Objetivos:

- seleccionar usuario;
- editar ficha;
- seleccionar actividad y nivel;
- iniciar y cerrar sesión;
- registrar botones rápidos;
- guardar observaciones;
- consultar historial.

Todavía sin transcripción en tiempo real obligatoria.

## Fase P3 — Generador de contexto y lanzador

Objetivos:

- generar perfil temporal;
- generar `session_context.json`;
- iniciar la app oficial con la sesión;
- registrar proceso y ruta de log;
- cerrar de forma controlada.

## Fase P4 — Captura e importación de logs

Objetivos:

- comprobar logs oficiales;
- redirigir salida;
- recibir eventos de tools;
- normalizar eventos;
- vincularlos a la sesión.

## Fase P5 — Análisis posterior

Objetivos:

- tiempos;
- turnos;
- apoyos;
- participación;
- resultados profesionales;
- resumen estructurado;
- advertencias por datos incompletos.

## Fase P6 — Recomendación de nivel

Objetivos:

- reglas configurables;
- varias sesiones;
- explicación de motivos;
- confirmación profesional;
- actualización de progreso.

## Fase P7 — Panel avanzado

Objetivos:

- transcripción en vivo cuando sea técnicamente posible;
- audio y VAD disponibles;
- gráficos de evolución;
- informes;
- exportación;
- despliegue replicable.

---

## 21. MVP recomendado

La primera versión útil del panel no necesita controlar todo el audio ni analizar automáticamente respuestas abiertas.

Debe incluir:

1. usuarios;
2. ficha adaptativa;
3. actividades;
4. tres niveles;
5. progreso por actividad;
6. inicio y final de sesión;
7. registro rápido profesional;
8. observaciones;
9. resumen;
10. recomendación sencilla;
11. decisión profesional;
12. contexto temporal;
13. SQLite;
14. integración externa sin tocar `src/`.

La transcripción en tiempo real y el control avanzado de audio pueden incorporarse después.

---

## 22. Privacidad y seguridad

Principios:

- almacenamiento local;
- no guardar audio por defecto;
- no guardar transcripción completa si no es necesaria;
- conservar datos estructurados y eventos relevantes;
- evitar información médica no necesaria;
- registrar quién crea o modifica una observación;
- permitir desactivar o borrar datos;
- realizar copias de seguridad;
- no presentar recomendaciones como diagnósticos;
- limitar el acceso al panel profesional.

La memoria estable debe ser:

- pertinente;
- no sensible;
- validada;
- modificable;
- eliminable.

---

## 23. Compatibilidad con actualizaciones oficiales

Después de actualizar `reachy_mini_conversation_app` deben realizarse pruebas de compatibilidad:

```text
1. La app arranca.
2. Se carga el perfil externo Ahootsa.
3. La transcripción funciona en español.
4. La voz configurada funciona.
5. Se cargan las tools externas.
6. play_ahootsa_dance funciona.
7. stop_ahootsa_dance funciona.
8. El robot vuelve a escuchar después del baile.
9. El lanzador captura el log.
10. El servidor permanece independiente.
```

Los componentes propios deben mantenerse fuera de `src/` para que una actualización oficial no los sobrescriba.

---

## 24. Riesgos principales

### Riesgo 1 — El log oficial no contiene toda la transcripción

Respuesta:

- validar antes;
- combinar log, tools y registro profesional;
- no prometer métricas no disponibles.

### Riesgo 2 — Las preferencias guardadas en la interfaz oficial prevalecen sobre `.env`

Respuesta:

- realizar prueba;
- usar lanzador;
- mostrar el perfil realmente cargado;
- bloquear el inicio si no coincide.

### Riesgo 3 — Duplicar la conversación

Respuesta:

- mantener el servidor fuera del flujo generativo;
- no añadir LLM propio;
- no usar `conversation_manager.py` como controlador principal.

### Riesgo 4 — Evaluación automática excesiva

Respuesta:

- automatizar solo indicadores observables;
- separar hechos, inferencias y valoración;
- confirmación profesional obligatoria.

### Riesgo 5 — Demasiadas instrucciones dinámicas

Respuesta:

- perfil base breve;
- contexto de sesión estructurado;
- solo información relevante;
- pruebas por actividad.

### Riesgo 6 — Cambios prematuros en código validado

Respuesta:

- fases pequeñas;
- backups;
- tests;
- no renombrar hasta definir la nueva interfaz.

---

## 25. Criterios de aceptación globales

La arquitectura se considerará correctamente implementada cuando:

- la aplicación oficial funcione sin modificaciones de `src/`;
- el servidor seleccione un usuario activo;
- cada actividad tenga tres niveles;
- el nivel se guarde por usuario y actividad;
- se genere un contexto temporal;
- la app oficial converse con ese contexto;
- las tools externas registren eventos;
- los logs se vinculen a una sesión;
- el panel permita valoración rápida;
- se calculen indicadores trazables;
- el sistema explique su recomendación;
- el profesional confirme la decisión;
- el progreso quede guardado;
- una actualización oficial pueda instalarse sin perder el desarrollo Ahootsa.

---

## 26. Decisiones registradas

### ADR-001 — Núcleo oficial inmutable

`src/` no se modifica.

### ADR-002 — Servidor local complementario

`ahootsa_local_server` es el backend profesional, no el motor conversacional.

### ADR-003 — Personalización previa

La persona, actividad y nivel se seleccionan antes de arrancar la sesión.

### ADR-004 — Perfil temporal

La personalización se aplica mediante archivos y variables externas generadas antes del inicio.

### ADR-005 — Registro posterior

El análisis principal se realiza después de la conversación para evitar latencia e interferencias.

### ADR-006 — Valoración profesional

La recomendación automática nunca sustituye la decisión del monitor.

### ADR-007 — Nivel independiente

El nivel se guarda por actividad.

### ADR-008 — Baile como refuerzo

«Vamos a bailar» es motivación o refuerzo, no medida principal de competencia comunicativa.

### ADR-009 — Sin Ollama

La versión actual no incorpora Ollama.

### ADR-010 — Evolución incremental

Se conserva el servidor 0.11.1 y se amplía mediante migraciones y pruebas pequeñas.

---

## 27. Próximo paso técnico recomendado

El siguiente paso no debe ser otro motor conversacional.

Debe ser una fase de datos y panel:

```text
Crear activities
Crear activity_levels
Crear user_activity_progress
Crear session_activities
Crear professional_notes
```

Después:

```text
Panel básico
→ selección de usuario
→ actividad
→ nivel
→ eventos profesionales
→ cierre
→ progreso
```

Solo cuando esta base esté validada se incorporará:

```text
generación de perfil temporal
→ lanzador oficial
→ captura de logs
→ análisis posterior
```

---

## 28. Recomendación final

La solución de referencia para Ahootsa 8 queda definida como:

```text
Reachy Mini Conversation App oficial sin modificar
+
perfil externo Ahootsa
+
tools y actividades externas
+
ahootsa_local_server como backend profesional
+
perfiles individuales
+
tres niveles por actividad
+
contexto generado antes de cada sesión
+
registro de eventos y logs
+
análisis posterior
+
recomendación explicable
+
decisión final del profesional
```

El trabajo realizado en `ahootsa_local_server` se conserva y se aprovecha. No debe eliminarse ni sustituirse, sino reorientarse de forma explícita hacia el panel profesional, el seguimiento y la personalización previa de la sesión.

La prioridad inmediata es consolidar los datos, las actividades por niveles y el panel básico. La integración avanzada con transcripción y audio se realizará cuando se haya comprobado exactamente qué información ofrece la aplicación oficial sin modificar su núcleo.
