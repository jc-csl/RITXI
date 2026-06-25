# Ritxi FastAPI v5.8.5 — panel profesional con daemon robusto

Versión profesional de Ritxi para Reachy Mini con:

- panel oscuro estilo Reachy Mini Desktop;
- chat con Ollama;
- catálogo de acciones, emociones, bailes, gestos sociales y tutor/terapia;
- checkboxes para activar/desactivar módulos de prueba;
- integración con `pollen-robotics/reachy-mini-emotions-library` mediante `RecordedMoves`;
- audio de emociones con `.wav` oficial cuando está disponible y fallback de voz del navegador;
- daemon Reachy/MuJoCo integrado en el panel mediante lectura de `logs/reachy_daemon_current.log`;
- scripts Windows simplificados y corregidos.


## Corrección v5.6: sonidos oficiales de Hugging Face

Las emociones oficiales de Pollen Robotics usan ahora los `.wav` reales del dataset `pollen-robotics/reachy-mini-emotions-library`.

El flujo de una tarjeta oficial es:

```text
click emoción → navegador reproduce /api/audio/recorded/{id} → FastAPI ejecuta robot.play_move(move)
```

Así el sonido expresivo no se sustituye por voz conversacional. La voz conversacional solo se usa para chat, cuentos, actividades o fallback final si el WAV oficial no puede descargarse/reproducirse.

Ver detalles en `docs/audio_huggingface_v5_6.md`.

## Instalación desde cero en Windows CMD

Descomprime el proyecto, por ejemplo en:

```cmd
D:\ritxi_fastapi_v5_5
```

Abre **CMD** y ejecuta:

```cmd
cd /d D:\ritxi_fastapi_v5_5
instalar_windows.cmd
```

## Ejecución normal

```cmd
cd /d D:\ritxi_fastapi_v5_5
ejecutar_windows.cmd
```

El script hará lo siguiente:

1. comprobar si el daemon Reachy responde en `127.0.0.1:8000`;
2. si no responde, lanzar `reachy-mini-daemon --sim` en una ventana minimizada;
3. guardar la salida del daemon en `logs\reachy_daemon_current.log`;
4. esperar hasta 90 segundos a que abra el puerto;
5. arrancar Ritxi en `http://127.0.0.1:8080`.


## Corrección v5.6: sonidos oficiales de Hugging Face

Las emociones oficiales de Pollen Robotics usan ahora los `.wav` reales del dataset `pollen-robotics/reachy-mini-emotions-library`.

El flujo de una tarjeta oficial es:

```text
click emoción → navegador reproduce /api/audio/recorded/{id} → FastAPI ejecuta robot.play_move(move)
```

Así el sonido expresivo no se sustituye por voz conversacional. La voz conversacional solo se usa para chat, cuentos, actividades o fallback final si el WAV oficial no puede descargarse/reproducirse.

Ver detalles en `docs/audio_huggingface_v5_6.md`.

## Instalación + ejecución en un paso

```cmd
instalar_y_ejecutar_windows.cmd
```

## Solo arrancar el daemon

```cmd
arrancar_daemon_windows.cmd
```

Esto sirve para diagnosticar si MuJoCo/Reachy arranca correctamente antes de abrir Ritxi.

## Si el script se queda esperando puerto 8000

Mira este archivo:

```text
logs\reachy_daemon_current.log
```

También puedes probar manualmente:

```cmd
.venv\Scripts\reachy-mini-daemon.exe --sim
```

Cuando esté correcto deberías ver el daemon en:

```text
http://127.0.0.1:8000
```

## Panel

Abre Chrome o Edge:

```text
http://127.0.0.1:8080
```

Desde el panel puedes:

- activar/desactivar módulos: micrófono, STT, Ollama, TTS, audio, texto, movimiento, cámara, logs, simulación;
- lanzar acciones directas con movimiento + audio;
- ver logs de Ritxi y del daemon;
- revisar si el movimiento oficial se resolvió con `RecordedMoves`;
- usar fallback si el audio oficial no está disponible.

## Orden recomendado para probar

1. Ejecuta `instalar_windows.cmd`.
2. Ejecuta `ejecutar_windows.cmd`.
3. Espera a que abra el panel.
4. Pulsa una emoción oficial, por ejemplo `Saludo / Hola` o `Alegría`.
5. Mira los logs del panel.

Eventos esperados:

```text
recorded_move_resolved
recorded_audio_started
recorded_move_played
```

Si el audio oficial falla, el panel debe lanzar voz fallback del navegador.


## v5.8 — Actividades dinámicas

Esta entrega mejora la pestaña de actividades: cada tarjeta puede lanzar una secuencia guiada con voz, movimiento, sonidos, pausas y refuerzo. Las actividades nuevas incluyen animales, sinónimos, cuento por turnos, respiración, ritmo, pedir ayuda, respetar turnos y elegir opción.



## v5.8.2 · Arranque Windows corregido

Esta versión retrasa la apertura del navegador y espera mejor a que todo esté listo:

```cmd
instalar_windows.cmd
ejecutar_windows.cmd
```

O todo junto:

```cmd
instalar_y_ejecutar_windows.cmd
```

El script de ejecución:
1. comprueba el daemon de Reachy en `127.0.0.1:8000`;
2. lo arranca si no está disponible;
3. espera hasta 120 segundos;
4. arranca FastAPI en `127.0.0.1:8080`;
5. espera a `/api/health`;
6. añade 10 segundos de margen;
7. abre el navegador.

Logs:
- `logs\reachy_daemon_current.log`
- `logs\ritxi_fastapi_current.log`


## v5.8.3 · Lanzador Windows corregido

La v5.8.2 fallaba con `No se esperaba 120 en este momento` por un bucle `cmd` con variables dentro de bloques `if`. En v5.8.3 el arranque se gestiona desde `ejecutar_windows.ps1`, llamado por `ejecutar_windows.cmd`.

Uso recomendado:

```cmd
instalar_windows.cmd
ejecutar_windows.cmd
```

O todo junto:

```cmd
instalar_y_ejecutar_windows.cmd
```

El lanzador ahora:

1. abre el daemon en una ventana propia;
2. espera hasta 150 segundos a `127.0.0.1:8000`;
3. arranca FastAPI;
4. espera a `127.0.0.1:8080`;
5. espera 10 segundos extra;
6. abre Chrome o el navegador predeterminado.

Logs principales:

- `logs\reachy_daemon_current.log`
- `logs\ritxi_fastapi_current.log`


## v5.8.4 · Lanzador Windows simplificado

Usa los nuevos scripts en mayúsculas:

```cmd
INSTALAR_RITXI.cmd
INICIAR_RITXI.cmd
```

O todo junto:

```cmd
INSTALAR_Y_EJECUTAR_RITXI.cmd
```

Esta versión abre dos ventanas visibles:
- `INICIAR_DAEMON_REACHY.cmd`
- `INICIAR_FASTAPI_VISIBLE.cmd`

Así, si FastAPI se cierra, verás el error real y también quedará en:

```text
logs\ritxi_fastapi_current.log
```

El navegador se abre 10 segundos después de que FastAPI responda en `127.0.0.1:8080`.


## v5.8.5 · Lanzador corregido y logs siempre creados

Usa:

```cmd
INSTALAR_RITXI.cmd
INICIAR_RITXI.cmd
```

O todo junto:

```cmd
INSTALAR_Y_EJECUTAR_RITXI.cmd
```

Esta versión crea siempre:

```text
logs\lanzador_current.log
logs\reachy_daemon_current.log
logs\ritxi_fastapi_current.log
```

Si FastAPI no abre `127.0.0.1:8080`, mira la ventana `RITXI v5.8.5 - FASTAPI VISIBLE` y el archivo `logs\ritxi_fastapi_current.log`.


## v5.8.6 · Scripts claros 1 / 2 / 3

Orden recomendado:

```cmd
1_INSTALAR_RITXI.cmd
2_INICIAR_DAEMON_RITXI.cmd
3_RUN_RITXI.cmd
```

Uso normal:

1. Ejecuta `1_INSTALAR_RITXI.cmd` solo la primera vez.
2. Ejecuta `2_INICIAR_DAEMON_RITXI.cmd` y deja esa ventana abierta.
3. Ejecuta `3_RUN_RITXI.cmd` en otra ventana.

Mejora de logs:

- El daemon ya no intenta pisar siempre `reachy_daemon_current.log` al arrancar.
- Cada sesión crea su propio log:
  - `logs\reachy_daemon_YYYYMMDD_HHMMSS.log`
  - `logs\ritxi_fastapi_YYYYMMDD_HHMMSS.log`
  - `logs\lanzador_YYYYMMDD_HHMMSS.log`


## v5.8.7 · Kill automático antes del daemon

`2_INICIAR_DAEMON_RITXI.cmd` ahora hace limpieza antes de arrancar:

- mata procesos `reachy-mini-daemon.exe` anteriores;
- busca procesos escuchando en `127.0.0.1:8000`;
- los cierra automáticamente;
- espera 2 segundos;
- arranca `reachy-mini-daemon --sim`.

También se corrige el falso `NativeCommandError` de PowerShell: el daemon a veces escribe líneas INFO por `stderr`, y PowerShell las mostraba como error aunque no fueran un fallo real.

Orden:

```cmd
1_INSTALAR_RITXI.cmd
2_INICIAR_DAEMON_RITXI.cmd
3_RUN_RITXI.cmd
```

Opcionalmente, si quieres limpiar a mano:

```cmd
0_MATAR_DAEMON_Y_PUERTO_8000.cmd
```


## v5.8.8 · Branding GAUDE

Cambio visual en la cabecera:

- Antes: `Compañero Reachy Mini`
- Ahora: `App Ritxi para GAUDE`


## v5.8.9 · Paso 3 sin pregunta S/N

Se corrige `3_RUN_RITXI.cmd`.

Antes el paso 3 podía mostrar:

```text
¿Desea terminar el trabajo por lotes (S/N)?
```

Ahora `3_RUN_RITXI.cmd` ya no crea ni ejecuta un `.cmd` temporal. Arranca FastAPI directamente con PowerShell y `Start-Process`.

Orden:

```cmd
1_INSTALAR_RITXI.cmd
2_INICIAR_DAEMON_RITXI.cmd
3_RUN_RITXI.cmd
```

Si necesitas ver FastAPI en primer plano para depurar:

```cmd
3B_DEBUG_FASTAPI_VISIBLE.cmd
```


## v5.9 · Corrección de emociones Hugging Face

Se corrigen IDs que no existían en el dataset oficial.

Ejemplos:
- `sleepy1` → `sleep1`
- `pensando` → `thoughtful1/thoughtful2`
- `calma` → `calming1/serenity1`
- `baile` → `dance1/dance2/dance3`
- `aplauso` → `success1/success2/proud1`

También se reduce el máximo de tokens del LLM en el paso 3 para mejorar la velocidad.


## v5.9.1 · Layout práctico
- Chat y actividades/emociones más grandes y accesibles.
- Logs y paneles de configuración movidos a la parte inferior.
- Zona superior centrada en conversación y acciones.
- Zona inferior reservada para diagnóstico, daemon, audio y pruebas por módulos.


## v5.9.2 · Voz más precisa y respuestas más rápidas

Ajustes principales:

- grabación máxima de voz: `4500 ms`;
- umbral de voz/ruido: `0.035`;
- silencio para enviar: `900 ms`;
- reescucha: `700 ms`;
- Whisper local por defecto: `tiny` + `int8`;
- Ollama limitado a respuestas más cortas:
  - `RITXI_LLM_MAX_TOKENS=55`;
  - `RITXI_LLM_TIMEOUT_S=25`;
  - `RITXI_OLLAMA_NUM_CTX=1024`;
- creatividad/temperatura por defecto: `0.25`.

Si sigue entendiendo mal, sube el umbral de voz a `0.045` o usa un micrófono USB cercano.


## v5.9.3 · Juegos cortos marcados y ciclo
- Las tarjetas quedan marcadas mientras se ejecutan.
- Se desmarcan al finalizar.
- Nuevo botón: `Ciclo juegos cortos`.
- El ciclo lanza acciones breves sin conversaciones largas.


## v5.9.4 · Ciclo con turnos y botón Salir

Cambios:
- Al activar `Espera activa`, Ritxi hace un movimiento visible inmediato.
- `Modo simulación` se renombra a `Simulación 3D / MuJoCo`.
- Nuevo ciclo de juegos cortos con turnos:
  - Ritxi ejecuta una acción breve;
  - espera a que hables o pulses `Siguiente`;
  - luego continúa.
- También queda disponible `Ciclo automático`.
- Nueva sección: `Actividades cortas con turno`.
- Nuevo botón superior `Salir`.
- Nuevo script:
  - `4_SALIR_RITXI.cmd`


## v5.9.5 · Carpeta limpia e iconos aclarados

Se limpian scripts antiguos o duplicados. En la raíz quedan como scripts principales:

- `1_INSTALAR_RITXI.cmd`
- `2_INICIAR_DAEMON_RITXI.cmd`
- `3_RUN_RITXI.cmd`
- `4_SALIR_RITXI.cmd`

También se añade:

- `LEEME_SCRIPTS_VALIDOS.txt`

En el panel se aclaran las acciones rápidas:

- `↻ Reconectar`: reconecta app con daemon/robot.
- `⇩ Guardar log`: descarga el log de sesión.
- `📷 Captura`: registra una captura/evento de cámara.
- `◎ Calibrar`: devuelve el robot a postura/calibración.


## v5.9.6 · Paneles prioritarios en horizontal

Reordenación práctica del panel inferior:

- `Estado actual`, `Daemon Reachy / MuJoCo` y `Audio` pasan a una fila horizontal.
- El panel de checks `Pruebas por módulos` queda justo debajo, a ancho grande.
- `Registros del sistema` queda debajo de los checks.
- A la izquierda quedan solo los paneles secundarios:
  - resumen del robot;
  - acciones rápidas.


## v5.9.7 · Corrección de tarjetas, ciclos y configuración

Cambios:
- Se elimina la emoción marcada por defecto que quedaba activa.
- Al pulsar una tarjeta se desactiva temporalmente el resto para evitar solapamientos.
- Si se pulsa otra tarjeta mientras hay una en curso, queda en cola visual.
- La tarjeta se desmarca siempre al terminar, incluso si hay error.
- `Ver configuración avanzada` abre un modal real con archivos de configuración.
- Ciclos corregidos para no quedarse bloqueados por el estado visual.


## v5.9.8 · Paso 3 sin pregunta S/N y con entorno correcto

`3_RUN_RITXI.cmd` ahora abre el lanzador en una ventana PowerShell separada y sale inmediatamente. Esto evita el mensaje de Windows:

```text
¿Desea terminar el trabajo por lotes (S/N)?
```

Además, FastAPI se arranca siempre con las variables correctas:

- `RITXI_MODE=reachy_daemon`
- `RITXI_LLM_PROVIDER=ollama`
- `RITXI_TTS_PROVIDER=browser`

Si quieres depurar manualmente, usa:

```cmd
3B_DEBUG_FASTAPI_CON_ENV.cmd
```

No uses directamente:

```cmd
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8080
```

porque así no se cargan las variables de Ritxi y arranca en `internal_simulation` + `mock`.


## v5.9.9 · Turno de usuario en actividades
Correcciones:
- Las actividades cortas activan el turno de usuario al terminar.
- En ciclo con turnos, Ritxi intenta abrir el micro automáticamente.
- El ciclo espera respuesta hablada/enviada o el botón `Siguiente`.
- También puedes escribir y pulsar Enter o ➤; ahora eso cuenta como respuesta de actividad.
- El paso 3 añade `RITXI_STT_PROVIDER=local_whisper` y `RITXI_STT_WHISPER_MODEL_SIZE=tiny`.


## v5.9.10 · Micro más rápido y precalentado

Correcciones para el micro:

- Whisper se precarga al abrir la app para evitar la espera de 5–6 segundos en la primera frase.
- STT local más rápido:
  - `serverRecordMaxMs=3500`
  - `serverVadThreshold=0.024`
  - `silenceSendMs=650`
  - `relistenDelayMs=500`
- Mensajes más claros:
  - “Preparando micro/Whisper…”
  - “Micro preparado…”
  - “No detecté voz suficiente…”

Si no detecta bien, prueba hablar más cerca o selecciona otro micrófono en el panel Audio.


## v5.9.11 · Micro con permiso explícito

Cambios:
- `Activar conversación / micro` pide permiso real al navegador usando `getUserMedia`.
- Si una actividad necesita que el usuario responda, pregunta:
  - activar micro;
  - o responder por texto.
- Si el micro no se puede abrir, se muestra un mensaje claro y se puede escribir en el chat.
- El micro no intenta abrirse mientras Ritxi está reproduciendo audio oficial o hablando; espera a que termine.


## v5.9.12 · Micro directo y segundo turno corregido

Cambios:
- El botón `Activar conversación / micro` ya no solo activa un bucle: intenta abrir el micro inmediatamente.
- Cuando Ritxi termina de hablar, reintenta abrir el micro automáticamente.
- Si está activo el modo conversación, el segundo turno vuelve a escuchar sin tener que pulsar de nuevo.
- Tiempos reducidos:
  - `serverRecordMaxMs=3200`
  - `silenceSendMs=550`
  - `relistenDelayMs=350`
  - `serverVadThreshold=0.020`


## v5.9.13 · Reescucha en juegos de turnos

Corrección concreta:
- En actividades y juegos con turnos, el micro se vuelve a abrir después de que Ritxi responda con audio.
- Antes se abría solo en el primer turno.
- Ahora el modo actividad mantiene `activityAutoListenAfterBot` hasta que pulses `Detener`, `Reset` o pares el ciclo.

Esto recupera el comportamiento esperado:
1. Ritxi pregunta.
2. Usuario habla.
3. Ritxi responde con voz.
4. Micro se abre otra vez para el usuario.


## v5.9.14 · Botón Hablar ahora

Cambio importante de uso:

- Antes: `Activar conversación / micro`
- Ahora: `Hablar ahora / activar micro`

Comportamiento:
- Si has perdido el turno, pulsa el botón y el micro se abre otra vez.
- Si el micro ya está escuchando, el botón lo para.
- Si Ritxi no entiende la voz, el turno no se pierde: puedes pulsar otra vez o escribir en el chat.


## v5.9.15 · Enviar texto y micro recuperan el turno

Corrección:
- Si Ritxi queda enganchado tras una respuesta o acción, `Enviar` ya no queda bloqueado.
- El botón `Hablar ahora / activar micro` fuerza la recuperación del turno y abre el micro.
- `Reset` limpia también estados del navegador.
- Se añade `app.js?v=5.9.15` para evitar que Chrome use una versión vieja del JavaScript.


## v5.9.16 · Ajuste de palabras entendidas

Sí hay ajuste sobre las palabras que Ritxi entiende.

En esta versión se añade vocabulario guiado para STT:

- En juegos de animales, Ritxi espera palabras como:
  - `perro`, `gato`, `vaca`, `oveja`, `caballo`, `león`, `mono`, `rana`, `pato`.
- Si Whisper oye algo parecido, se corrige hacia la palabra esperada.
- También hay vocabulario corto para:
  - `hola`, `adiós`, `sí`, `no`, `ayuda`, `gracias`, `por favor`.

Esto no afecta a conversaciones largas normales; se aplica sobre todo en juegos cortos y actividades con vocabulario cerrado.


## v5.9.17 · Lenguaje con turno real

Corrección:
- `Sinónimos` ahora no es solo una frase de Ritxi: abre turno para que el usuario responda.
- También se corrigen:
  - `Buscar palabra`
  - `Opuestos`
  - `Completar frase`
  - `Describir imagen`
  - `Frase corta`
  - `Historia por turnos`

Después de la consigna:
1. Ritxi habla.
2. Se activa el turno del usuario.
3. El micro se abre o puedes escribir y pulsar `➤`.


## v5.9.18 · Recuperación fuerte de turnos

Corrección importante:
- Si una actividad se queda en `Abriendo micro...`, ahora puedes pulsar `Hablar ahora / activar micro` y se reinicia la captura de micro.
- `Enviar texto` también funciona aunque el micro haya quedado enganchado.
- El botón `Hablar ahora` ya no intenta adivinar si debe parar o arrancar: siempre recupera el turno y abre micro.
- Para parar se usa `Parar micro`.


## v5.9.19 · Revisión profunda del micro

Cambio importante:
- El micro pasa a gestionarse como **micro continuo controlado**.
- Ya no se abre/cierra en cada turno.
- Queda abierto mientras estás en conversación o actividad con turno.
- Se pausa solo mientras Ritxi habla.
- Se reanuda cuando Ritxi termina de hablar.
- `Parar micro` es el botón para anularlo.
- Al elegir una acción sin turno, el micro se desconecta.

Este enfoque evita los bloqueos repetidos en `Abriendo micro...`.


## v5.9.20 · Revisión profunda del micro

Cambio clave:
- El micro deja de depender de `echo_guard/canListenNow` para abrirse.
- Antes podía quedarse bloqueado en `Abriendo micro...`.
- Ahora el navegador abre el micro directamente y solo lo pausa mientras Ritxi habla.

Ajustes:
- `serverVadThreshold=0.015`
- `silenceSendMs=700`
- `serverRecordMaxMs=5000`

Flujo:
1. Actividad con turno o botón `Activar micro continuo`.
2. El navegador abre el micro.
3. Ritxi habla → micro pausado.
4. Ritxi termina → micro activo otra vez.
5. Acción sin turno → micro desconectado.


## v5.9.21 · Filtro de repeticiones de Whisper

Se añade un filtro para evitar que se envíen a Ollama transcripciones repetitivas como:

`la idea de que es la idea de que es la idea de que es...`

Ese patrón suele ser una alucinación de STT por silencio, eco o ruido. Ahora:

- se detecta por repetición de n-gramas;
- se descarta;
- se avisa al usuario;
- el micro queda listo para repetir o se puede escribir texto.

El filtro está tanto en backend como en frontend.


## v5.9.22 · Editar configuración y carácter desde el panel

Corrección:
- `Editar carácter de Ritxi` ahora carga el perfil y guarda mostrando confirmación.
- El carácter se guarda en `profiles/characters/ritxi_tutor_comunicacion_di.json`.
- `Configuración avanzada` ahora permite editar archivos reales y guardarlos.
- Se añade botón `Editar JSON del carácter`.

Archivos editables desde configuración avanzada:
- `.env.example`
- `README.md`
- `plan.md`
- `agents.local.md`
- `profiles/characters/ritxi_tutor_comunicacion_di.json`
- `app/prompts/system_prompt.txt`
- `app/core/config.py`

Algunos cambios pueden requerir reiniciar Ritxi.


## v5.9.23 · Panel simplificado

- Se elimina del panel principal el bloque visible de **Acciones rápidas**.
- Se elimina del panel principal el bloque visible de **Daemon Reachy / MuJoCo**.
- El panel **Pruebas por módulos** se simplifica y deja solo 3 modos generales:
  - Solo texto
  - Voz + robot
  - Tutor completo
- Los checkboxes internos siguen existiendo en segundo plano para no romper la lógica actual, pero ya no se muestran al usuario.


## v5.9.24 · Limpieza de botones de micro

- Se elimina el botón redundante **Parar micro** del panel principal.
- Se elimina el botón redundante **Forzar micro ON** del panel principal.
- El botón principal pasa a ser un **toggle real**:
  - `▶ Activar micro`
  - `■ Parar micro`
- Al parar manualmente el micro, **queda bloqueado** y ya no se reactiva solo tras TTS o respuestas automáticas.
- Ese bloqueo solo se levanta cuando:
  - el usuario pulsa **Activar micro**, o
  - se lanza una **actividad que requiere entrada de voz**.


## v5.9.25 · Correcciones de estabilidad detectadas en logs

Esta versión aplica las correcciones detectadas en los logs:

- micro menos sensible para evitar ruido/eco;
- filtro anti-repetición reforzado;
- `sí/no` menos agresivo, solo en respuestas cortas;
- Ollama más rápido con menos tokens/contexto;
- movimiento de Reachy con protección antisolape;
- audio oficial HF reproducido desde navegador, no desde backend;
- cache actualizado a `app.js?v=5.9.25`.

Valores principales:
- `serverVadThreshold=0.028`
- `serverRecordMaxMs=3500`
- `silenceSendMs=850`
- `RITXI_LLM_MAX_TOKENS=45`
- `RITXI_LLM_TIMEOUT_S=18`
- `RITXI_OLLAMA_NUM_CTX=768`


## v5.9.26 · Carpeta de vocabularios JSON por actividad

Se añade la carpeta:

```text
app/config/stt_vocabularies/
```

Contenido:

- `index.json`: índice general y estrategia de matching.
- `activity_mapping.json`: mapa de actividad/tarjeta a grupo de vocabulario esperado.
- `common.json`: sí/no, saludos, despedidas, cortesía y muletillas.
- `animals.json`: animales y sonidos.
- `language.json`: sinónimos, opuestos, completar frase y frases cortas.
- `social_communication.json`: pedir ayuda, pedir turno, presentación y escucha activa.
- `emotions.json`: emociones y regulación.
- `music_sounds.json`: ritmo, sonidos e imitación.

Esta versión deja preparada la estructura para STT guiado por actividad.


## v5.9.27 · Modelos rápidos y prompt general

Cambios:
- Modelo recomendado por defecto: `gemma3:1b`.
- Modelos disponibles en el selector del panel:
  - Rápido: `qwen3:0.6b`
  - Equilibrado: `gemma3:1b`
  - Llama rápido: `llama3.2:1b`
  - Calidad: `llama3.2:3b`
- El selector de modelo se envía en cada turno a `/api/chat`.
- Nuevo archivo editable: `app/config/model_presets.json`.
- El archivo `app/prompts/system_prompt.txt` se copia y se usa como instrucciones generales del sistema dentro del prompt de Ritxi.
- `Configuración avanzada` permite editar `Prompt de sistema` y `Modelos rápidos Ollama`.

Comandos recomendados:
```cmd
ollama pull gemma3:1b
ollama pull qwen3:0.6b
ollama pull llama3.2:3b
```


## v5.9.28 · Limpieza de scripts y requirements

La raíz del proyecto queda simplificada:

### Scripts principales

```text
0_INSTALAR_MODELOS_OLLAMA.cmd
0_INSTALAR_MODELOS_OLLAMA.sh
1_INSTALAR_RITXI.cmd
2_INICIAR_DAEMON_RITXI.cmd
2_INICIAR_DAEMON_RITXI.ps1
3_RUN_RITXI.cmd
3_RUN_RITXI.ps1
4_SALIR_RITXI.cmd
```

### Cambios

- Se eliminan scripts auxiliares no necesarios de la raíz:
  - `3B_DEBUG_FASTAPI_CON_ENV.cmd`
  - `LEEME_SCRIPTS_VALIDOS.txt`
- Se agrupan los requirements en un único archivo:
  - `requirements.txt`
- Se eliminan:
  - `requirements-dev.txt`
  - `requirements-optional.txt`
  - `requirements-stt-whisper.txt`
- Se añade instalador independiente para Ollama/modelos:
  - `0_INSTALAR_MODELOS_OLLAMA.cmd`
  - `0_INSTALAR_MODELOS_OLLAMA.sh`

### Modelos instalados por el script 0

```text
Rápido        → qwen3:0.6b
Equilibrado   → gemma3:1b
Llama rápido  → llama3.2:1b
Calidad       → llama3.2:3b
```

El modelo recomendado por defecto sigue siendo:

```text
gemma3:1b
```

En Linux/WSL, si Ollama no está instalado, el script usa:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```


## v5.9.29 · Layout ampliado y desbloqueo de turnos

Cambios visuales:
- El panel de Emociones/Actividades gana más anchura y altura.
- La zona inferior queda más compacta para dejar espacio al panel principal.
- La caja de 3 modos generales se hace más pequeña.
- Se muestra el modelo cargado/seleccionado:
  - en el chat;
  - en el panel inferior compacto.

Cambios de estabilidad:
- Nuevo botón `Desbloquear`.
- El envío a `/api/chat` tiene watchdog cliente.
- Si Ollama se queda demasiado tiempo pensando, la interfaz se desbloquea y avisa.
- El estado visible indica el modelo usado en el turno.


## v5.9.30 · Pestaña Configuración con editor real

Se rehace la pestaña `Configuración` para que no dependa solo de botones/modal.

Ahora permite editar directamente:

- Prompt del sistema:
  - `app/prompts/system_prompt.txt`
- Constantes/configuración Python:
  - `app/core/config.py`
- Modelos Ollama:
  - `app/config/model_presets.json`
- Carácter de Ritxi:
  - `profiles/characters/ritxi_tutor_comunicacion_di.json`
- Variables de entorno de ejemplo:
  - `.env.example`
- Vocabularios STT:
  - `app/config/stt_vocabularies/activity_mapping.json`
  - `language.json`
  - `social_communication.json`
  - `animals.json`

También se validan los JSON antes de guardarlos.


## v5.9.31 · Limpieza de chat y estado de Ritxi en barra superior

Cambios:
- La información de Ritxi, batería, temperatura y Wi‑Fi pasa a la línea superior.
- Se elimina visualmente el panel inferior de resumen de Ritxi para dejar sitio a Estado actual y Audio.
- El panel de Audio mantiene información de micrófono y altavoz.
- La entrada de mensaje es más grande.
- En el recuadro del chat queda solo:
  - botón Activar/Parar micro;
  - mensaje de estado del micro.
- Se ocultan Reset, Desbloquear y Diagnóstico STT/micro de la vista principal.


## v5.9.32 · Nueva pestaña Juegos / canciones / bailes

La pestaña `Aplicaciones` se elimina porque no aportaba información funcional al uso diario.

En su lugar se crea:

```text
Juegos / canciones / bailes
```

Agrupa:

- bailes oficiales y baile libre;
- canciones y ritmo;
- palmas;
- instrumentos;
- sonidos;
- juegos de animales;
- cuentos e imaginación;
- chistes y juego social.

Además, esos elementos se eliminan visualmente de las otras pestañas para dejar:

- `Emociones`: emociones, gestos sociales y apoyo.
- `Actividades`: comunicación, lenguaje, conversación y regulación.
- `Juegos / canciones / bailes`: parte lúdica.
- `Configuración`: edición de archivos importantes.


## v5.9.33 · Área de conversación ampliada

- Se amplía la altura útil del panel de chat para aprovechar el hueco vertical libre.
- El historial de conversación gana más espacio visible.
- La caja de entrada del mensaje crece ligeramente para escribir mejor.


## v5.9.34 · Ciclos visibles y pestaña de juegos

- Los botones **Ciclo con turnos** y **Ciclo automático** ahora se comportan como modos excluyentes: solo uno puede quedar activo.
- Al pulsar el otro ciclo, el anterior se desactiva y el nuevo queda marcado visualmente.
- La secuencia usa actividades cortas de **juegos, canciones y bailes** para que se vea claramente que está funcionando.
- Los 3 modos generales (**Solo texto / Voz + robot / Tutor completo**) también se resaltan como selección única.
- La pestaña lúdica queda consolidada como **Juegos / canciones / bailes**.


## v5.9.35 · Barra de ciclos más compacta

- Se reduce la altura del cuadro de `Ciclo con turnos / Ciclo automático / Siguiente`.
- El texto explicativo queda en la misma línea siempre que haya espacio.
- Se acorta el texto para dejar más sitio al panel de tarjetas.


## v5.9.36 · Botones de ciclo funcionales

- `Ciclo con turnos` y `Ciclo automático` quedan como modos excluyentes.
- Si pulsas el modo activo, se para.
- Si pulsas el otro modo, cambia de ciclo.
- El botón activo queda resaltado.
- `Siguiente` se activa solo cuando el ciclo con turnos está esperando.
- Se añade estado visible en la misma barra para saber qué está pasando.


## v5.9.37 · Restaurar fichas de Actividades y Juegos

Corrección:
- Actividades y Juegos / canciones / bailes vuelven a renderizar tarjetas siempre.
- Se elimina el filtrado agresivo que podía dejar pestañas vacías.
- Se añade fallback de juegos si los grupos principales no cargan.
- Ciclo con turnos y Ciclo automático usan actividades reales visibles.
- Los botones de ciclo cambian de estado y se pueden parar pulsando de nuevo.


## v5.9.38 · Corrección error STT 500

- Se corrige el error que hacía que Whisper grabara audio y cargara modelo, pero devolviera `500 Internal Server Error`.
- Causa: faltaba la función interna `_simple_tokens()` usada por el filtro anti-repetición.
- El postprocesado de vocabulario/repetición ahora está protegido para que nunca rompa la transcripción completa.
- Si un filtro falla, se registra el error y se devuelve la transcripción de Whisper en lugar de HTTP 500.


## v5.9.39 · Tutor/apoyo emocional y ciclo único con turnos

Cambios:
- Nueva pestaña `Tutor / apoyo`.
- Se mueven ahí las actividades de tutoría, terapia comunicativa, regulación emocional y refuerzo.
- Se amplía esa pestaña con actividades nuevas:
  - pausa sensorial;
  - semáforo emocional;
  - frase segura;
  - pedir descanso;
  - ensayo pedir ayuda;
  - primero/después;
  - elegir emoción;
  - cierre tranquilo.
- Se elimina `Ciclo automático` para evitar confusión.
- Queda solo `Ciclo con turnos`, que hace preguntas cortas y espera respuesta o botón Siguiente.
- `Carácter: Tutor amable` pasa a selector rápido con:
  - Tutor amable;
  - Apoyo emocional;
  - Lenguaje claro;
  - Juegos y canciones;
  - Modo calma.


## v5.9.40 · Mejor estado STT y actividad de nombre

Correcciones:
- El mensaje de estado del micro/STT se hace más grande y visible.
- La actividad `Preguntar nombre` usa `vocabularyHint: open_name`.
- `open_name` no se envía como vocabulario cerrado al backend.
- Para nombre se relaja el filtro previo de señal baja para no descartar voz corta.
- Si no entiende el nombre, el mensaje indica claramente que puede repetirlo despacio o escribirlo.


## v5.9.41 · Preguntas abiertas y conversación natural

Corrección principal:
- Se clasifican actividades de conversación natural o pregunta abierta como `open_text` u `open_name`.
- Los hints `open_*` no se envían al backend como vocabulario cerrado.
- Se evita que respuestas como `Me llamo Juanita` sean rechazadas por un `vocabulary_hint=yes_no` anterior.
- Al ejecutar una acción sin turno, se limpia `currentVocabularyHint` para no arrastrar el hint de la actividad anterior.

Actividades abiertas revisadas:
- `preguntar_nombre` → `open_name`
- `escuchar`, `vamos_hablar`, `presentacion` → `open_text`
- `historia_turnos`, `cuento_interactivo`, `explicar_imagen`, `frase_corta` → `open_text`
- actividades de apoyo emocional/regulación con frase libre → `open_text`


## v5.9.42 · Código comentado y manual técnico

Se añaden comentarios de arquitectura en los módulos principales:

- `app/main.py`
- `app/static/app.js`
- `app/audio/local_whisper.py`
- `app/llm/ollama_provider.py`
- `app/orchestration/action_scheduler.py`
- `app/robot/reachy_sdk.py`
- `app/core/config.py`

Se añade el manual técnico:

```text
docs/MANUAL_CODIGO_RITXI.md
```

Contenido del manual:

- estructura de carpetas;
- flujo de arranque;
- flujo de conversación por texto;
- flujo de conversación por voz;
- flujo de STT;
- clasificación de actividades abiertas/cerradas;
- flujo de acciones y tarjetas;
- ciclo con turnos;
- pestañas del panel;
- endpoints principales;
- comunicación entre módulos;
- archivos de configuración;
- puntos delicados del código.


## v5.9.43 · Scroll en chat y script 5

Cambios:
- El historial del chat ahora tiene scroll interno.
- El panel de conversación ya no aumenta indefinidamente de altura.
- Se añade:

```text
5_INSTALAR_E_INICIAR_DAEMON_RITXI.cmd
```

Este script ejecuta seguidos:
1. `1_INSTALAR_RITXI.cmd`
2. `2_INICIAR_DAEMON_RITXI.cmd`

Los modelos Ollama siguen instalándose aparte con:
`0_INSTALAR_MODELOS_OLLAMA.cmd`.


## v5.9.44 · Fichas restauradas y micro tras actividades

Correcciones:
- Las pestañas Emociones, Actividades, Juegos y Tutor restauran tarjetas si quedan vacías.
- Se eliminan filtros de renderizado que podían dejar pestañas sin fichas.
- Se añade fallback de actividades básicas si un grupo no carga.
- Actividades como `Ritmo con palmas`, `Palmas lentas`, `Palmas rápidas`, `Cantar saludo`, `Baile suave`, `Baile divertido`, `Eco de Ritxi` e `Imítame` pasan a ser actividades con turno.
- Si una actividad dice “Ahora te toca a ti”, se activa el turno y el micro.
- El botón `Activar micro` hace desbloqueo manual fuerte y debe obedecer después de terminar una actividad.


## v5.9.45 · Texto siempre aceptado y turnos abiertos en juegos

Correcciones:
- El botón de enviar texto funciona aunque el micro esté esperando una respuesta.
- Enviar texto cancela captura/STT pendiente, desbloquea el turno y envía a Ollama.
- Las actividades abiertas que esperan respuesta activan turno:
  - historia por turnos;
  - cuento por turnos;
  - inventar final;
  - personajes;
  - recordar historia;
  - ritmo con palmas;
  - palmas lentas;
  - palmas rápidas;
  - cantar saludo;
  - baile suave;
  - baile divertido;
  - imítame;
  - eco de Ritxi.
- Los pasos internos de actividades (`steps`) que dicen `tu turno`, `qué crees`, `continúa`, etc. abren micro y aceptan texto.
- Consulta a Ollama más rápida:
  - timeout cliente baja a 14 s;
  - tokens por defecto bajan a 35;
  - historial por defecto baja a 4 mensajes.


## v5.9.46 · Coherencia de actividades, velocidad y pestañas en una línea

Correcciones:
- Se mantiene contexto de actividad cuando Ritxi pregunta y el usuario responde.
- La respuesta del usuario se envía a Ollama enriquecida con:
  - nombre de actividad;
  - consigna original;
  - paso actual;
  - instrucción de continuar la misma actividad.
- Para actividades cerradas o lúdicas se evita Ollama y se responde localmente:
  - animales;
  - ritmo/palmas;
  - cantar saludo;
  - baile/imitación;
  - nombre.
- Esto reduce mucho la latencia en juegos cortos.
- El timeout cliente baja a 10 s.
- Las pestañas superiores se compactan para que Config. no baje a segunda línea.


## v5.9.47 · Ajuste visual de pestañas

Cambios:
- Las pestañas superiores aumentan de tamaño.
- La pestaña activa se ve un poco más grande.
- La segunda fila del ciclo queda algo más pequeña, pero legible.
- Se mantiene todo en una sola línea.


## v5.9.48 · Flujo real de actividades y texto siempre enviable

Correcciones:
- `Completar frase` ya no salta a “dime una frase corta...”; completa la actividad.
- `Frase corta`, `Describir imagen`, cuentos e historias mantienen contexto.
- El botón de enviar texto se re-habilita siempre aunque el micro/STT esté esperando.
- El texto manual no se filtra como repetición STT.
- Respuestas de actividades cerradas se hacen localmente, sin Ollama.
- Timeout de Ollama baja a 8 s para evitar esperas largas antes del fallback.


## v5.9.49 · Revisión completa de actividades, turnos y respuestas no repetitivas

Cambios:
- Se revisan sistemáticamente las fichas que esperan respuesta.
- Se crea `REVIEWED_TURN_ACTIVITY_IDS`.
- Se marcan como turno actividades de saludo, despedida, ayuda, turno, lenguaje, cuentos, historias, emociones, ritmo y juegos.
- Se amplía `fastActivityReply()` con respuestas específicas por tipo de actividad.
- Se añaden variantes de respuesta para evitar repetir siempre la misma frase.
- Las actividades largas como historias o descripción mantienen contexto y siguen pidiendo turno.
- Se añade documentación:
  - `docs/REVISION_ACTIVIDADES_TURNOS_v5_9_49.md`


## v5.9.50 · Barras de color por nivel de interacción

Cambios:
- Cada ficha muestra una barra inferior de color:
  - gris: solo reproduce;
  - azul: interacción corta;
  - morada: interacción larga;
  - dorada: máxima interacción.
- Las etiquetas aparecen en la parte baja de la tarjeta sin tapar título ni descripción.
- Se añade `MAX_CREATIVE_ACTIVITY_IDS`.
- Se marcan como máxima interacción:
  - Historia por turnos;
  - Cuento por turnos;
  - Inventar final;
  - Describir imagen;
  - Elegir emoción.
- Estas actividades mantienen contexto hasta que el usuario diga terminar/parar/cambiar.
- Se evita respuesta local repetitiva en actividades de máxima interacción.
- Documento añadido:
  - `docs/CLASIFICACION_INTERACCION_FICHAS_v5_9_50.md`


## v5.9.51 · Prioridad absoluta del texto sobre el micro

Correcciones:
- La caja de texto y el botón ➤ quedan siempre habilitados.
- Al hacer clic, enfocar o escribir en la caja de texto, se activa `Modo texto`:
  - se para el micro;
  - se cancela STT/VAD pendiente;
  - se desbloquea el envío;
  - se conserva el contexto de actividad.
- Nuevo botón visible:
  - `⌨ Modo texto`
- El preset `Solo texto` ahora detiene realmente el micro/STT.
- Enviar texto manual conserva el contexto de actividad, pero no permite que el micro bloquee la entrada.


## v5.9.52 · Envío de texto no bloqueable y respuesta local realmente rápida

Correcciones:
- El botón `➤` envía con `click`, `pointerup` y `touchend`.
- Se añade `sendTextNow()` con bloqueo anti-doble-envío corto.
- Entrar en modo texto ya no espera una parada larga del micro antes de enviar.
- La respuesta rápida local ya no espera a que termine el TTS; habla en paralelo y libera la interfaz.
- El watchdog re-habilita entrada de texto cada segundo.
- `5_INSTALAR_E_INICIAR_DAEMON_RITXI.cmd` ejecuta `1_` y `2_` seguidos, sin pausa intermedia.


## v5.9.53 · Panel Estado/Audio compacto

Cambios:
- Panel `Estado actual` más bajo.
- Bloque `Ejecutando` reorganizado en una sola línea:
  - título;
  - subtítulo;
  - botón Detener.
- Onda de ejecución reducida para no ocupar altura.
- Panel `Audio` más compacto:
  - micrófono y altavoz en columnas;
  - medidores más pequeños;
  - botón Probar audio integrado a la derecha.


## v5.9.54 · Controles de actividad unificados

Cambios:
- Se elimina la caja grande duplicada `Acción seleccionada`.
- El resumen de actividad queda en la misma barra que el ciclo.
- El botón `Detener` se mantiene solo en `Estado actual`, para no duplicar controles.
- La barra superior queda como:
  - `Ciclo corto`;
  - `Siguiente`;
  - estado del ciclo;
  - actividad actual compacta.
- `Ciclo con turnos` pasa a llamarse `Ciclo corto`, porque realmente ejecuta una secuencia de fichas breves y `Siguiente` solo sirve cuando está esperando respuesta.
- El texto `Respuesta de actividad: ...` se limpia y no aparece duplicado como título.


## v5.9.55 · Modo de interacción integrado y script 5 sin pausa intermedia

Cambios:
- `5_INSTALAR_E_INICIAR_DAEMON_RITXI.cmd` ya no se detiene en la pausa final de `1_INSTALAR_RITXI.cmd`.
- `1_INSTALAR_RITXI.cmd` acepta `RITXI_NO_PAUSE=1`.
- La antigua barra `Modo general` pasa a `Modo de interacción` y se integra junto a `Estado actual` y `Audio`.
- Modos:
  - `Texto`: apaga micro/STT y deja entrada escrita activa.
  - `Micro`: activa micrófono/STT/IA/voz, manteniendo texto disponible como respaldo.
  - `Tutor completo`: activa texto + micro + IA + voz + robot.
- El botón `⌨ Modo texto` del chat queda sincronizado con `Texto`.
- Audio/micro queda más estrecho para dejar espacio al reajuste de los paneles.


## v5.9.56 · Modos coherentes y texto/IA local revisados

Cambios:
- Se elimina visualmente cualquier resto de `Modo general`.
- La zona se llama `Modo de interacción`.
- Se muestran estados reales:
  - Texto ON/OFF;
  - Micro ON/OFF;
  - IA ON/OFF;
  - Robot ON/OFF.
- `Texto` activa IA local escrita y apaga micro/STT/voz/robot.
- `Micro + IA` activa micro/STT/IA/voz, pero mantiene texto disponible.
- `Completo` activa texto + micro + IA + voz + robot.
- Las actividades de conversación abierta dejan de responder con respuesta rápida local genérica; pasan a IA local/Ollama.
- El estado `Respuesta rápida local, sin Ollama` se sustituye por `Actividad resuelta al instante; IA no necesaria`, solo para actividades cerradas.
- Si el usuario intenta enviar vacío, aparece aviso en estado de micro.


## v5.9.57 · Corrección envío de texto

Problema confirmado en logs:
- El botón `➤` recibía el clic.
- Después se llamaba a `forceUnlockTurnState(...)`.
- Esa función no existía, provocando un error JavaScript antes de llegar a `/api/chat`.
- Por eso no aparecía ningún `Usuario:` ni `turn_start` en los logs.

Correcciones:
- Se añade `forceUnlockTurnState()` como desbloqueo ligero real.
- `sendTextNow()` ahora captura errores y los escribe en logs.
- Se simplifican eventos del botón `➤` para evitar doble click `pointerup/click`.
- Se añade log `Preparando envío de texto a actividad/IA` para diagnosticar futuros bloqueos.


## v5.9.58 · Modo arriba y timeout real de IA local

Correcciones basadas en logs:
- El texto sí se enviaba correctamente.
- El fallo era el timeout del cliente a 10 s.
- Después el backend seguía trabajando y acababa cayendo a fallback mock, pero el navegador ya había abortado.
- Se elimina el mensaje que sugería cambiar de modelo/modo automáticamente.

Cambios:
- `Modo de interacción` sube arriba, encima del chat y de los paneles.
- El modo seleccionado no cambia automáticamente al escribir, hablar o esperar.
- `Texto + IA` conserva Ollama/IA local activa y apaga micro/STT/voz/robot.
- `Micro + IA` conserva texto disponible.
- `Completo` conserva texto + micro + IA + voz + robot.
- Timeout cliente sube a 60 s.
- Timeout backend de Ollama sube a 60 s.
- Proveedor LLM por defecto pasa a `ollama`.
- TTS de respuestas normales pasa a no bloquear el turno.


## v5.9.59 · Estado actual arriba en zona de control

Cambios:
- `Estado actual` sube a la zona superior de control.
- `Ejecutando / Detener` también sube arriba.
- La zona superior queda unificada:
  - Modo de interacción;
  - Estado actual;
  - Actividad / ejecución.
- Se elimina la tarjeta inferior duplicada de `Estado actual`.
- El bloque inferior queda más libre para audio/logs y no roba altura al chat.


## v5.9.60 · Diagnóstico de latencia por modelo

Correcciones basadas en logs:
- El modo `Texto + IA` sí estaba funcionando sin audio, sin STT y sin robot.
- La lentitud venía del modelo real seleccionado: `llama3.2:3b`.
- En los logs, `llama3.2:3b` tarda 24-31 s hasta el primer token y 27-36 s en total.
- Se añade indicador de velocidad del modelo:
  - `Muy rápido`;
  - `Rápido recomendado`;
  - `Rápido`;
  - `Lento / calidad`.
- Se añade botón manual `Usar rápido` para cambiar a `gemma3:1b`.
- El sistema no cambia automáticamente el modo ni el modelo.
- Se reduce historial por defecto a 2 mensajes para aligerar llamadas a Ollama.
