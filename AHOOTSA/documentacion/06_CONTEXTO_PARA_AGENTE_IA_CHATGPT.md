# Contexto del proyecto AHOOTSA8 para un agente de IA o ChatGPT

## Instrucción de uso

Este documento debe proporcionarse al agente antes de pedir cambios técnicos.
Describe el estado base que debe respetar. El agente debe revisar también los
archivos reales del repositorio y no asumir que una versión histórica sigue
vigente.

## 1. Identidad del proyecto

AHOOTSA8 es una solución de robótica social basada en Reachy Mini para apoyar
actividades comunicativas con supervisión profesional.

Nombre hablado del robot:

```text
Aocha
```

Entidades del proyecto:

- Asociación Gaude: necesidades, validación social y acompañamiento;
- Centro San Luis: desarrollo y mantenimiento tecnológico.

El público objetivo incluye personas adultas con discapacidad intelectual. El
lenguaje debe ser adulto, claro, respetuoso y no infantilizante.

## 2. Estado técnico de referencia

```text
Ahootsa Local Server: 0.12.8.6
Reachy Mini Conversation App incluida: 0.9.0
Reachy Mini SDK: 1.9.0
MuJoCo: 3.3.0
Python: 3.12
Sistema: Windows 10/11
PowerShell: compatible con 5.1
Backend: Hugging Face realtime deployed
Transcripción: español
Voz: Sohee
```

Ruta principal:

```text
D:\RITXI\AHOOTSA8
```

Repositorio:

```text
https://github.com/jc-csl/RITXI
```

## 3. Jerarquía de fuentes

Cuando haya contradicciones, utilizar este orden:

1. archivos actuales del repositorio `AHOOTSA8`;
2. código y configuración de `ahootsa_local_server`;
3. scripts operativos de la raíz y `scripts`;
4. esta documentación actualizada;
5. documentos históricos de fases;
6. versiones anteriores y logs antiguos.

No utilizar Ahootsa 5, 7 u Ollama como arquitectura actual. El sistema actual
usa la aplicación oficial incluida y el backend Hugging Face desplegado.

## 4. Arquitectura obligatoria

### Motor principal

```text
reachy_mini_conversation_app
```

Responsable de:

- conversación;
- audio;
- transcripción;
- voz;
- backend realtime;
- herramientas;
- movimientos;
- interfaz 7860.

### Extensiones

```text
external_content
```

Contiene perfiles, herramientas y actividades de Ahootsa.

### Servidor local

```text
ahootsa_local_server
```

Responsable de:

- personas;
- perfiles;
- sesiones;
- eventos;
- actividades;
- panel;
- SQLite;
- informes.

No es el motor de respuesta principal y no debe duplicar el backend realtime.

## 5. Restricciones de desarrollo

- No modificar `reachy_mini_conversation_app\src` para añadir funciones de
  Ahootsa, salvo una decisión explícita y documentada.
- Preferir `external_content`, herramientas externas y servidor local.
- No sustituir la aplicación oficial por una aplicación paralela.
- No introducir Ollama sin una nueva decisión de arquitectura.
- No cambiar versiones de SDK, MuJoCo o aplicación sin prueba de migración.
- No crear scripts dispersos en muchas carpetas.
- Mantener pocos scripts operativos y nombres claros.
- Validar PowerShell con el parser real de Windows PowerShell 5.1.
- Evitar expresiones problemáticas como `"$Variable:"`; usar
  `"${Variable}:"`.
- Los ZIP de actualización deben tener una carpeta contenedora y no deben
  dejar `payload` en la raíz.
- Cada actualización debe incluir documentación de arquitectura y cambios.
- Trabajar y validar un paso cada vez.
- No afirmar que algo está validado en Windows hasta ver su salida real.

## 6. Modos de inicio

### Anónimo

```powershell
.\INICIAR_AHOOTSA_ANONIMO.ps1
```

- 8000 y 7860;
- 8100 detenido;
- perfil `ahootsa`;
- sin usuario;
- sin sesión;
- sin informe.

### Sesión local

```powershell
.\INICIAR_AHOOTSA_SESION.ps1
```

- 8100 y 8000;
- panel;
- prepara persona, actividad y nivel;
- Conversation App se inicia después;
- perfil `ahootsa_session`;
- informe al finalizar.

## 7. Scripts operativos

```text
INICIAR_AHOOTSA_ANONIMO.ps1
INICIAR_AHOOTSA_SESION.ps1
FINALIZAR_SESION_AHOOTSA.ps1
COMPROBAR_AHOOTSA.ps1
LIMPIAR_PROCESOS_AHOOTSA.ps1
```

Scripts internos:

```text
scripts\ahootsa_process_utils.ps1
scripts\iniciar_servidor_local.ps1
scripts\iniciar_daemon_mujoco.ps1
scripts\iniciar_conversation_anonima.ps1
scripts\iniciar_conversation_sesion.ps1
```

## 8. Puertos

```text
8000 daemon
8100 servidor local y panel
7860 Conversation App
```

Panel actual:

```text
http://127.0.0.1:8100/panel-12-8-5
```

No cambiar esta ruta solo porque el servidor sea 0.12.8.6; está referenciada
por scripts.

## 9. Perfiles

```text
ahootsa          modo general y anónimo
ahootsa_session  sesión identificada
ahootsa_default  plantilla
```

La versión incluida usa:

```text
instructions.txt
greeting.txt
tools.txt
voice.txt
```

No migrar a `profile.md` por copiar documentación de una versión oficial más
nueva.

## 10. Modelo profesional

Actividades por niveles:

```text
Inicial
Intermedio
Avanzado
```

Marcas:

```text
adecuada
parcial
incorrecta
sin respuesta
pista
repetición
ejemplo
```

El profesional decide:

```text
mantener
subir
bajar temporalmente
repetir
sin decisión
```

El sistema no realiza evaluación clínica ni cambios automáticos de nivel.

## 11. Datos e informes

```text
ahootsa_local_server\data\ahootsa.db
ahootsa_local_server\data\sessions\session_XXXXXX
```

Informes:

```text
informe_sesion.pdf
informe_sesion.html
informe_sesion.json
transcripcion_sesion.txt
```

ReportLab debe estar instalado en el `.venv` del servidor.

## 12. Forma de responder del agente

Al proponer cambios:

1. explicar qué archivo se modifica;
2. justificar por qué;
3. no alterar componentes no relacionados;
4. proporcionar comandos exactos de PowerShell;
5. preparar un ZIP incremental cuando proceda;
6. incluir un comprobador;
7. esperar la salida del usuario antes del siguiente paso;
8. documentar la nueva arquitectura;
9. diferenciar entre comprobación local y validación real en Windows.

## 13. Preguntas que el agente debe resolver antes de tocar código

- ¿El cambio afecta al modo anónimo, a la sesión local o a ambos?
- ¿Debe ejecutarse en la aplicación oficial, en `external_content` o en el
  servidor local?
- ¿Cambia el formato de la base de datos?
- ¿Afecta a la finalización o a los informes?
- ¿Necesita migración de datos?
- ¿Se mantiene PowerShell 5.1?
- ¿Se ha conservado el perfil general?
- ¿Se ha evitado modificar `src`?
- ¿Se ha actualizado esta documentación?

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


## 14. Reglas incorporadas en 0.12.8.6

- Crear una persona solo modifica SQLite.
- Pulsar `Preparar` reconstruye el perfil fijo `ahootsa_session` desde
  `ahootsa_default`.
- El saludo de sesión debe decir literalmente el nombre preferido.
- Si hay intereses registrados, el saludo debe mencionarlos y ofrecer hablar
  de ellos.
- `play_ahootsa_dance` debe finalizar automáticamente y provocar una respuesta
  hablada breve al terminar.
- No debe modificarse `src` para implementar estas funciones.
