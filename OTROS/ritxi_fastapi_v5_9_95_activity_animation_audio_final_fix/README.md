# Ritxi FastAPI v5.9.61

Aplicación local para controlar Ritxi / Reachy Mini con:

- panel web;
- texto escrito;
- micrófono;
- STT local Whisper;
- IA local con Ollama;
- TTS del navegador;
- emociones y movimientos de Reachy Mini;
- actividades de lenguaje, comunicación, juegos y apoyo emocional.

## Novedades v5.9.61

- Código principal comentado para mantenimiento.
- Manual de programación actualizado.
- Manual de usuario actualizado.
- Carpeta `docs/` limpiada: se eliminan documentos/manuales de versiones anteriores a la 5.60.
- Se mantiene como referencia funcional la v5.9.60.

## Documentación vigente

```text
docs/MANUAL_PROGRAMACION_RITXI_v5_9_61.md
docs/MANUAL_USUARIO_RITXI_v5_9_61.md
```

## Arranque rápido

### 1. Instalar modelos Ollama

```text
0_INSTALAR_MODELOS_OLLAMA.cmd
```

### 2. Instalar Ritxi

```text
1_INSTALAR_RITXI.cmd
```

### 3. Iniciar daemon Reachy / MuJoCo

```text
2_INICIAR_DAEMON_RITXI.cmd
```

### 4. Iniciar panel

```text
3_RUN_RITXI.cmd
```

### Instalación + daemon

```text
5_INSTALAR_E_INICIAR_DAEMON_RITXI.cmd
```

## Modos de interacción

```text
Texto + IA      texto escrito + Ollama, sin micro ni robot
Micro + IA      micrófono/STT + Ollama, texto disponible
Completo        texto + micro + IA + voz + robot
```

El modo seleccionado no debe cambiar automáticamente.

## Modelos recomendados

```text
gemma3:1b       recomendado
qwen3:0.6b      más rápido
llama3.2:1b     rápido
llama3.2:3b     más lento / calidad
```

## Logs

```text
logs/session_*.jsonl
logs/session_*.log
logs/lanzador_*.log
logs/reachy_daemon_*.log
```

Los logs permiten diagnosticar lentitud de Ollama, problemas de STT, errores de robot y bloqueos de interfaz.

## Archivos comentados en v5.9.61

```text
app/static/app.js
app/main.py
app/core/config.py
app/audio/local_whisper.py
app/llm/ollama_provider.py
app/orchestration/action_scheduler.py
app/robot/reachy_sdk.py
```


## v5.9.62 · Texto + IA rápida con emociones activas

Cambios:
- El arranque por defecto pasa a `Texto + IA rápida`.
- Modelo rápido por defecto: `qwen3:0.6b`.
- El micro queda apagado por defecto.
- `Texto + IA rápida` no lee en voz alta el texto de la respuesta.
- Los sonidos/emociones oficiales de Ritxi sí pueden reproducirse aunque el modo sea texto.
- Hacer clic en una emoción oficial reproduce su audio aunque `TTS` esté apagado.
- Tras una respuesta de Ollama se puede reproducir una emoción breve automática según `data.emotion`.
- Se separan conceptos:
  - TTS = leer el texto de la respuesta.
  - sonido emocional = audio breve propio de Ritxi.
  - micro = entrada de voz, independiente del texto.


## v5.9.63 · Texto + IA + Robot y recuperación de emociones

Cambios:
- Modo por defecto: `Texto + IA rápida`, sin micro, con modelo `qwen3:0.6b`.
- Nuevo modo separado: `Texto + IA + Robot`.
- `Texto + IA rápida`:
  - texto escrito;
  - IA local;
  - micro apagado;
  - no lee la respuesta con TTS;
  - sí permite sonidos/emociones oficiales de Ritxi.
- `Texto + IA + Robot`:
  - texto escrito;
  - IA local;
  - micro apagado;
  - no lee la respuesta con TTS;
  - reproduce sonidos emocionales;
  - mueve el robot si está disponible.
- `Micro + IA` mantiene texto disponible y robot parado.
- `Completo` activa texto + micro + IA + voz + robot.
- Hacer clic en una emoción oficial fuerza su sonido aunque esté en modo texto.
- Las emociones automáticas tras conversación usan sonido breve y, si el modo tiene robot, también movimiento.


## v5.9.64 · Eliminado panel Audio/Micro inferior

Cambios:
- Se elimina el cuadro inferior `Audio` / `Micrófono` / `Altavoz`.
- Se elimina el listener del botón `Probar audio`, porque ese bloque ya no existe.
- Se conserva el audio funcional necesario para:
  - sonidos emocionales oficiales de Ritxi;
  - TTS cuando el modo lo active;
  - reproducción de emociones al hacer clic.
- Se amplía la zona superior de control/interacción con más altura, margen y respiración visual.


## v5.9.65 · Reajuste de la zona superior

Cambios:
- `Modo de interacción` gana más anchura.
- `Estado actual` y `Actividad / ejecución` quedan más compactos.
- Se añade más altura y margen al bloque superior para que no se corte en ventanas no maximizadas.
- Los botones de modo pueden partir línea y adaptarse mejor cuando falta ancho.


## v5.9.66 · Texto primero, robot después

Correcciones:
- El chat ya no puede mostrar una burbuja de Ritxi vacía aunque el modelo devuelva solo una etiqueta de emoción.
- En `Texto + IA rápida` se muestra primero la respuesta escrita y después se reproduce la emoción sonora.
- En `Texto + IA + Robot` se muestra primero la respuesta escrita y después se lanza emoción/robot en segundo plano.
- El backend no espera al movimiento del robot en turnos de chat; el movimiento emocional se lanza desde el navegador después de mostrar el texto.
- El modelo por defecto queda coherente en la interfaz: `qwen3:0.6b`.


## v5.9.67 · Fichas independientes de los modos de chat

Correcciones:
- Los modos superiores (`Texto + IA`, `Texto + IA + Robot`, `Micro + IA`, `Completo`) afectan al chat conversacional.
- Las fichas de clic directo imponen su propio funcionamiento.
- Una emoción oficial siempre puede reproducir sonido al hacer clic, aunque el chat esté en modo texto.
- Una ficha con emoción/movimiento fuerza movimiento de robot si la ficha lo necesita.
- Las actividades guiadas usan su propia voz/movimiento/turno y no quedan anuladas por el modo de chat.
- Si el chat está en `Texto + IA + Robot` o `Completo`, cada respuesta conversacional lanza animación emocional de robot en segundo plano después de mostrar el texto.


## v5.9.68 · Corrección error chatFlagsForBackend

Corrección:
- Se define `chatFlagsForBackend()` en ámbito global, justo después de `flags()`.
- `sendTurn()` ya no falla si por cualquier motivo esa función no está disponible.
- El chat vuelve a enviar texto a `/api/chat`.
- Se mantiene la separación:
  - modos superiores = chat conversacional;
  - fichas/actividades = funcionamiento propio de cada ficha.


## v5.9.69 · Corrección payloadFlags y verificación de modos

Corrección crítica:
- `payloadFlags` se calculaba después de usarse en el primer `logClient()` de `sendTurn()`.
- Eso provocaba `ReferenceError: payloadFlags is not defined` nada más enviar texto.
- Ahora se calcula antes del log y antes del payload `/api/chat`.

Separación comprobada:
- `Texto + IA rápida`: chat escrito + IA, sin micro, sin robot conversacional.
- `Texto + IA + Robot`: chat escrito + IA; texto primero; luego emoción/robot en segundo plano.
- `Micro + IA`: chat por micro + IA, texto disponible, robot conversacional parado.
- `Completo`: chat con texto + micro + IA + voz + robot.

Fichas/actividades:
- Las fichas no dependen del modo superior de chat.
- Las fichas usan `cardRuntime(item)` para imponer sonido, voz, robot o turno.
- Las actividades con turno pueden pedir micro aunque el chat esté en modo texto; si no se acepta, se responde por texto.
- Se añade `selfCheckConversationAndCards()` en arranque para detectar funciones críticas antes de usar el chat.


## v5.9.70 · safeBotText y autocomprobación real de arranque

Corrección:
- El log del usuario mostraba `ReferenceError: safeBotText is not defined`.
- `safeBotText()` ahora queda declarada en ámbito global.
- `sendTurn()` queda protegido si la función no estuviera disponible por cualquier motivo.
- `payloadFlags` se mantiene calculado antes de usarse.
- Se añade badge de versión completa visible arriba: `v5.9.70`.
- `selfCheckConversationAndCards()` comprueba en arranque:
  - `flags`;
  - `chatFlagsForBackend`;
  - `safeBotText`;
  - `sendTurn`;
  - `sendTextNow`;
  - `setModulePreset`;
  - `cardRuntime`;
  - `executeAction`;
  - `runActivity`;
  - `playAutomaticEmotionAfterReply`;
  - `playAutomaticRobotEmotionAfterReply`.

Si falta algo, deja aviso visible y evento `selfcheck` en logs.


## v5.9.71 · creatividad conectada y política externa de actividades

Cambios:
- El deslizador `Creatividad` se envía ahora a `/api/chat` como `temperature`.
- El backend aplica esa temperatura en Ollama mediante `temperature_override`.
- Se añade `app/config/interaction_policy.json`:
  - `local_activity_ids`: fichas muy simples que pueden responder localmente.
  - `ollama_activity_ids`: fichas/actividades que deben usar IA local.
  - `defaults`: modelo, temperatura y timeout de chat.
- Se añade `app/config/ritxi_constants.py` para centralizar constantes Python principales.
- Las fichas locales simples se marcan con un color azul/cian.
- Las actividades conversacionales, abiertas o que requieren pensar fuerzan Ollama.
- Se mejora `safeBotText()` para no repetir siempre “Te escucho...”.
- Se mejoran respuestas de fallback para perro/gato/ayuda/hola/contento.


## v5.9.72 · Configuración nueva visible en pestaña Config.

Cambios:
- En la pestaña `Config.` aparecen ahora botones directos para:
  - `app/config/interaction_policy.json`
  - `app/config/ritxi_constants.py`
- También quedan disponibles en `Configuración avanzada`.
- `/api/config/files` incluye etiquetas claras para ambos archivos.
- `/api/config/file` devuelve `real_path` para mostrar la ruta real en el editor.


## v5.9.73 · Todos los config editables desde pestaña Config

Cambios:
- La pestaña `Config.` ahora muestra una lista dinámica de todos los archivos editables devueltos por `/api/config/files`.
- Se añaden accesos directos:
  - `Política interacción JSON`
  - `Lista local_activity_ids`
  - `Lista ollama_activity_ids`
  - `Constantes externas`
- `local_activity_ids` y `ollama_activity_ids` se editan dentro de `app/config/interaction_policy.json`.
- `app/config/ritxi_constants.py` queda editable desde la misma pestaña.


## v5.9.74 · Creatividad visible y con efecto verificable

Cambios:
- El valor de creatividad se muestra al lado del deslizador.
- Cada respuesta del chat muestra la creatividad usada, por ejemplo `creatividad: 0.85`.
- El texto enviado a Ollama incluye una instrucción interna de estilo según el nivel:
  - precisa;
  - equilibrada;
  - variada;
  - creativa.
- `safeBotText()` también respeta la creatividad.
- Si se usa fallback seguro, la burbuja lo indica con `fallback seguro`.

Nota:
Si el modelo devuelve una respuesta vacía o solo una etiqueta de emoción, el texto mostrado no viene de Ollama sino del fallback seguro. Ahora queda marcado.


## v5.9.75 · Corrección sesgo “pedir ayuda”

Cambios:
- Se elimina el texto inicial fijo del textarea `Hola Ritxi, quiero practicar cómo pedir ayuda`.
- Cada arranque crea una sesión nueva si la sesión era `demo`, para no arrastrar historial antiguo.
- El prompt de sistema refuerza que Ritxi debe responder al tema actual del usuario.
- Se indica explícitamente que no debe cambiar a “pedir ayuda” salvo que el usuario lo pida.
- `safeBotText`, fallback backend y mock añaden respuesta específica para `vida`.
- Las respuestas de fallback genéricas ya no redirigen siempre a pedir ayuda.


## v5.9.76 · Política de conversación y anti-repetición

Problema corregido:
- El modelo rápido podía repetir la misma respuesta cuando el usuario cambiaba de tema.
- Especialmente `qwen3:0.6b` puede quedarse anclado al turno anterior.

Cambios:
- Nuevo archivo editable: `app/config/conversation_policy.json`.
- La pestaña `Config.` incluye acceso a `Política conversación / repetición`.
- Se añade filtro anti-repetición en el navegador.
- Si la respuesta se repite y el tema del usuario cambia, se sustituye por un fallback por tema.
- Los fallbacks por tema se editan en `conversation_policy.json`.


## v5.9.77 · Emociones oficiales sin TTS de sustitución

Corrección:
- Las tarjetas de emociones oficiales ya no dicen frases como `Ritxi ejecuta esta emoción` si falla el WAV.
- Regla aplicada:
  - si el WAV oficial existe, se reproduce el WAV;
  - si el WAV no existe o falla, solo se ejecuta la animación del robot;
  - nunca se usa TTS para sustituir el sonido oficial de una emoción.
- Se eliminan los `fallbackText` de las emociones oficiales grabadas.


## v5.9.78 · Config con rutas relativas y errores claros

Correcciones:
- `/api/config/file` acepta ahora claves lógicas y rutas relativas permitidas.
- La lista dinámica de Config usa `real_path` relativo.
- Si un archivo editable falta en una instalación limpia, se crea una plantilla mínima.
- Los errores del editor muestran `HTTP status + detail`, no solo `Failed to fetch`.
- Añadido endpoint de diagnóstico: `/api/config/selftest`.
- Los botones de vocabularios apuntan a rutas relativas reales:
  - `app/config/stt_vocabularies/activity_mapping.json`
  - `app/config/stt_vocabularies/language.json`
  - `app/config/stt_vocabularies/social_communication.json`
  - `app/config/stt_vocabularies/animals.json`


## v5.9.79 · Emociones oficiales independientes del modo

Corrección:
- Al hacer clic en una emoción oficial, ya no depende del modo conversacional.
- Siempre se intenta reproducir su WAV oficial.
- Siempre se envía animación al robot/simulador.
- Si el WAV no existe o falla, no se usa TTS de sustitución: solo animación.
- El envío al robot se hace con `wait:true` para verificar que la animación se ejecuta y dejar error claro si falla.


## v5.9.80 · Audio oficial OGG/WAV

Corrección basada en logs:
- El robot sí ejecutaba animaciones, pero el audio fallaba porque se buscaban archivos `.wav`.
- El dataset oficial actual usa `.ogg`.
- `get_recorded_audio_path()` prueba ahora `.ogg` y después `.wav`.
- `/api/audio/recorded/{emotion_id}` sirve `audio/ogg` o `audio/wav` según la extensión.
- La interfaz deja de hablar de WAV y muestra `audio oficial`.


## v5.9.81 · Chat sin contexto pegado + emociones oficiales

Correcciones:
- Se arregla `ReferenceError: Cannot access 'id' before initialization` en `fastActivityReply()`.
- El chat normal ya no hereda contexto de una actividad anterior.
- Si el usuario escribe fuera de un turno de actividad, se limpia `currentActivityContext`.
- El micro de actividad ya no se reabre después de un chat normal.
- Se mantiene la corrección de emociones oficiales:
  - click emoción → audio oficial `.ogg/.wav` + animación;
  - independiente del modo conversacional;
  - sin TTS de sustitución.
- Se añade diagnóstico en consola:
  - `await testOfficialEmotionRuntime('cheerful1')`


## v5.9.82 · Conversación no repetitiva y modos dentro del chat

Correcciones:
- El backend ya no envía historial en chat libre por defecto. qwen3:0.6b repetía el tema anterior cuando recibía historial.
- Se eliminan ejemplos concretos del prompt del sistema porque qwen los copiaba.
- Se quita el ejemplo de “pedir ayuda”/“vida” como respuesta dominante.
- El chat normal limpia contexto de actividad anterior.
- Los 4 modos se mueven dentro del panel `Chat con Ollama` porque solo afectan al chat conversacional.
- Los controles `Creatividad` y `Velocidad voz` vuelven a mostrarse claramente en el chat.
- La zona superior queda para resumen de modo, estado, actividad y telemetría básica: WiFi, batería y temperatura.


## v5.9.84 · Texto del modo y cierre positivo de robot

Cambios:
- El texto del modo `Texto + IA` ya no dice “no lee la respuesta completa”.
- Ahora indica: la respuesta se muestra por texto y no se reproduce en voz alta.
- En modo `Texto + IA + Robot` y `Completo`, las actividades cortas que finalizan lanzan un cierre positivo aleatorio de robot.
- El cierre positivo elige aleatoriamente entre emociones/movimientos positivos:
  - `cheerful1`
  - `enthusiastic1`
  - `yes1`
  - `hello1`
  - `dance1`
  - `dance2`
  - `dance3`
  - `electric1`
  - `amazed1`
- No se aplica a actividades largas o abiertas que mantienen contexto.


## v5.9.85 · Escucha activa como interacción larga y colores revisados

Correcciones:
- `Escucha activa` (`escucha_activa` y `escuchar`) pasa a ser interacción larga real.
- Tras una respuesta de Ollama en interacción larga, el contexto no se cierra.
- Ritxi mantiene la actividad viva hasta que el usuario diga algo como `terminar`, `fin`, `parar`, `cambiar` u `otra actividad`.
- Se revisa el orden de clasificación visual:
  1. Máxima interacción
  2. Interacción larga
  3. Respuesta local simple
  4. Interacción corta
  5. Solo reproduce
- Colores reforzados:
  - local simple: cian
  - corta: azul
  - larga: morado/fucsia
  - máxima: dorado/naranja


## v5.9.86 · Sin registros visibles y layout compacto

Cambios:
- Se elimina de la pantalla el panel `Registros del sistema`.
- Se eliminan los botones visuales de logs:
  - Todo / INFO / WARN / ERROR / DEBUG
  - Buscar en logs
  - Pausar
  - Limpiar
  - Exportar
- Los logs internos se siguen registrando y enviando al backend mediante `/api/log/client`.
- Se compactan las fichas de emociones/actividades:
  - menor anchura mínima;
  - menor separación;
  - texto e iconos algo más pequeños.
- El chat gana proporción horizontal.
- La aplicación reduce su ancho máximo para poder convivir mejor con la ventana del robot sin maximizar.


## v5.9.87 · Actividades autónomas y robot positivo al inicio/final

Cambios:
- Las actividades/fichas ya no dependen del modo conversacional del chat para reproducirse correctamente.
- Se añade `activityRuntimeMode(item)`:
  - si una actividad necesita robot, lo activa;
  - si necesita audio/voz, lo activa;
  - si necesita micro, lo solicita aunque el chat esté en modo texto.
- Toda actividad que contiene robot lanza:
  - animación positiva aleatoria al inicio;
  - animación positiva aleatoria al final cuando la actividad se cierra.
- Las interacciones largas no se cierran al primer turno. El cierre positivo se lanza cuando el usuario dice `terminar`, `fin`, `parar`, `cambiar` u otra fórmula de cierre.
- La lista positiva incluye todos los bailes:
  - `dance1`
  - `dance2`
  - `dance3`
  - `baile`
  - `calma`


## v5.9.88 · Script 6, error de chat y regla global de animaciones

Correcciones:
- Corregido el error de entrada:
  `shouldUseSafeLocalForExperimentalModel is not defined`.
- Añadido `6_LANZAR_RITXI_COMPLETO.cmd` y `6_LANZAR_RITXI_COMPLETO.ps1`.
- El script 6 ejecuta:
  1. `1_INSTALAR_RITXI.cmd`
  2. `2_INICIAR_DAEMON_RITXI.cmd` en otra terminal
  3. espera hasta 45 s / puerto 8000
  4. `3_RUN_RITXI.cmd` en otra terminal
- Los dos paneles principales se fuerzan a la misma altura.
- La zona de fichas se amplía verticalmente.
- Regla de animaciones:
  - solo el chat conversacional `Texto + IA` queda sin animaciones automáticas;
  - emociones, actividades, juegos y chat con robot/sonido/micro pueden lanzar animación positiva al inicio y al final.
- La lista positiva mantiene todos los bailes disponibles.


## v5.9.89 · Chat libre con modelo efectivo y respuestas por tema

Correcciones:
- `qwen3:0.6b` ya no produce una respuesta segura local genérica en chat libre.
- Si `qwen3:0.6b` queda seleccionado en chat libre, se redirige internamente a `gemma3:1b`.
- El desplegable se corrige en arranque para usar `gemma3:1b` si el usuario no ha tocado el selector.
- `gemma3:1b` queda como modelo recomendado por defecto.
- Añadidas respuestas de fallback para:
  - `hola`
  - `naturaleza`
  - `bosque`
  - `mar`
  - `amor`
  - `jugar`
- `fallbackFromConversationPolicy()` ahora tiene respuestas internas mínimas aunque `conversation_policy.json` aún no se haya cargado.


## v5.9.90 · Actividades no bloqueadas por robot

Corrección crítica:
- En v5.9.88/v5.9.89 había un error en `launchPositiveOpeningRobotAnimation()`:
  `phase` se usaba sin estar definido.
- Eso podía impedir que las actividades arrancaran.
- Las animaciones positivas de inicio/final pasan a ser no bloqueantes:
  - si el robot/daemon tarda o falla, la actividad sigue;
  - el error queda en logs;
  - el texto/voz/pasos de la actividad se inician igualmente.


## v5.9.91 · Animación de actividades y refreshStatus robusto

Correcciones:
- `refreshStatus()` ya no rompe el frontend si faltan elementos eliminados de la interfaz (`statusCompact`, `logStatus`, etc.).
- Se corrige la regla: todas las fichas/actividades/juegos/emociones usan animación aunque el chat esté en `Texto + IA`.
- La única excepción sin animación automática es el chat conversacional puro `Texto + IA`.
- Las animaciones de inicio/final dejan trazas explícitas:
  - `Animación positiva INICIO solicitada`
  - `Animación positiva FINAL solicitada`
- La versión visible/logueada pasa a `v5.9.91` para evitar confusión de caché.


## v5.9.92 · Animaciones inicio/final visibles y lista positiva validada

Según el log de v5.9.91, el frontend sí pedía animaciones de inicio/final, pero:
- el inicio podía quedar tapado por la acción principal inmediatamente;
- el final podía elegir `fiesta`, que no existe en la librería y terminaba en pose neutra;
- varias acciones `neutral` de arranque saturaban la cola.

Cambios:
- lista positiva limitada a movimientos reales/validados:
  - `cheerful1`
  - `amazed1`
  - `yes1`
  - `success1`
  - `dance1`
  - `dance2`
  - `dance3`
- el inicio de actividad usa una pequeña pausa visible de 650 ms antes del movimiento principal;
- el final ya no puede elegir `fiesta`;
- los bailes se usan preferentemente en actividades de baile, no como cierre genérico.


## v5.9.93 · Animaciones inicio/final visibles y configurables

Cambios:
- Nueva configuración editable:
  `app/config/robot_motion_policy.json`
- La pestaña Config incluye:
  `Política robot / animaciones`
- Las animaciones de inicio/final se priorizan con movimientos muy visibles:
  `dance1`, `dance2`, `dance3`, `cheerful1`.
- El inicio espera confirmación (`wait: true`) y deja una pausa configurable antes de la acción principal.
- Se evitan acciones `neutral` de arranque cuando el modo inicial es `Texto + IA`, para no saturar la cola.
- Si el log no muestra `Ritxi v5.9.93 iniciado`, el navegador sigue usando caché/carpeta antigua.


## v5.9.94 · Animaciones de emociones en configuración

Cambios:
- `app/config/robot_motion_policy.json` incluye ahora una lista separada:
  - `validated_visible_emotions`
  - `emotion_positive`
- Se añaden emociones/movimientos visibles validados:
  - `cheerful1`
  - `enthusiastic1`
  - `amazed1`
  - `electric1`
  - `success1`
  - `yes1`
  - `no1`
  - `attentive1`
  - `thoughtful1`
  - `dance1`
  - `dance2`
  - `dance3`
- Si se añaden nuevos ids desde Config y existen en la librería Pollen, funcionan sin tocar código.
- Si el id no existe, revisar logs porque el backend puede caer a `fallback_pose`.


## v5.9.95 · Audio oficial en animaciones inicial/final de actividad

Correcciones:
- Las animaciones positivas de inicio/final de actividad ahora reproducen también el audio oficial del movimiento.
- El audio se lanza desde navegador con `playOfficialRecordedAudio()`.
- El movimiento se sigue lanzando por `/api/robot/action`.
- La animación final queda más explícita en logs:
  - `Audio oficial positivo end solicitado`
  - `Animación positiva FINAL lanzada`
- `robot_motion_policy.json` añade:
  - `play_audio_on_positive_start`
  - `play_audio_on_positive_end`
  - `positive_audio_force`
  - `positive_audio_wait_until_end`
- Los bailes largos ya no son el valor por defecto para inicio/final; quedan disponibles en configuración.
