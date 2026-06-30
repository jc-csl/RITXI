# Ahootsa Realtime Ollama — Revisión de base estable y uso de ask_ollama

**Propuesta de base estable:** `v0.4.34_base_original_resources`  
**Objetivo:** mantener intactos todos los recursos de la app original de Reachy Mini y añadir únicamente la posibilidad de consultar Ollama local mediante `ask_ollama`.

---

## 1. Principio principal

La versión base estable debe partir de esta regla:

```text
No modificar la app original.
No modificar sus recursos.
No modificar su interfaz.
No modificar sus herramientas.
No modificar sus perfiles oficiales.
No modificar su gestión de audio.
No modificar su sistema de movimiento.
No modificar su sistema de emociones.
No modificar su sistema de bailes.
```

Ahootsa debe funcionar como una **capa externa** que arranca la app oficial y añade un perfil propio.

---

## 2. Recursos originales que nunca deben alterarse

Estos recursos deben mantenerse como los trae la app oficial:

```text
reachy_mini_conversation_app/
├─ interfaz web original
├─ sistema de micrófono
├─ sistema de voz realtime
├─ sistema de perfiles
├─ herramientas oficiales
├─ cámara
├─ memoria
├─ emociones
├─ bailes
├─ movimientos
├─ cola de acciones
├─ gestión de estado del robot
└─ backend realtime original
```

Herramientas originales que deben conservarse:

```text
dance
stop_dance
play_emotion
stop_emotion
camera
idle_do_nothing
move_head
sweep_look
remember
forget
```

Estas herramientas deben seguir siendo las responsables de:

```text
bailar
parar baile
hacer emociones
parar emociones
usar cámara
mover cabeza
mirar alrededor
recordar
olvidar
```

No se debe crear una versión alternativa de estas herramientas si la original ya funciona.

---

## 3. Qué añade Ahootsa sobre la app original

Ahootsa solo debe añadir:

```text
1. Una app nueva en Reachy Mini Desktop.
2. Un perfil propio en español.
3. Una herramienta nueva: ask_ollama.
4. Scripts de instalación y metadata.
5. Documentación de arquitectura.
```

Estructura nueva mínima:

```text
src/
└─ ahootsa_realtime_ollama_desktop_app/
   ├─ main.py
   ├─ assets/
   │  └─ ahootsa_logo.png
   └─ profiles/
      └─ ahootsa_realtime_es/
         ├─ instructions.txt
         ├─ greeting.txt
         ├─ voice.txt
         ├─ tools.txt
         └─ ask_ollama.py
```

---

## 4. Papel de la IA remota

En esta arquitectura, la IA remota sigue siendo el cerebro conversacional principal.

La IA remota se encarga de:

```text
- escuchar al usuario por micrófono
- transcribir o interpretar la voz
- mantener el turno de conversación
- decidir qué herramienta usar
- llamar a dance, play_emotion, move_head, camera, remember...
- decidir si debe llamar a ask_ollama
- generar la respuesta oral final
```

Por tanto, la conversación por sonido sigue pasando por la app oficial y su backend realtime.

---

## 5. Papel de Ollama local

Ollama local no sustituye a la IA remota.

Ollama solo se usa cuando se llama a la herramienta:

```text
ask_ollama
```

Configuración habitual:

```text
Servidor Ollama: http://127.0.0.1:11434
Modelo: ahootsa-local:latest
```

`ask_ollama` sirve para consultar el modelo local y devolver texto a la conversación.

No controla directamente:

```text
- micrófono
- voz realtime
- cámara
- movimiento
- emociones
- bailes
- memoria
```

---

## 6. Cómo se activa ask_ollama si el usuario habla por voz

El usuario habla por el micrófono.

Flujo real:

```text
Usuario habla
→ app oficial recibe audio
→ backend realtime interpreta la frase
→ si la frase pide IA local, llama a ask_ollama
→ ask_ollama consulta Ollama local
→ Ollama devuelve texto
→ backend realtime lo convierte en respuesta hablada
```

Ejemplo:

```text
Usuario: usa la IA local para darme una actividad sencilla
→ backend realtime detecta intención de IA local
→ llama a ask_ollama
→ Ollama genera la actividad
→ Ahootsa la dice por voz
```

---

## 7. ¿ask_ollama se activa por defecto?

En la base estable recomendada: **no**.

`ask_ollama` no debe activarse por defecto para todo.

Debe activarse solo cuando:

```text
- el usuario lo pide claramente
- la instrucción del perfil lo ordena en un caso concreto
- queremos que una categoría concreta de preguntas use IA local
```

Esto evita romper la app original y evita que cada frase pase innecesariamente por Ollama.

---

## 8. Frases que deben activar ask_ollama

Ejemplos de órdenes por voz:

```text
usa la IA local
consulta Ollama
pregunta al modelo local
usa el modelo local
usa ahootsa-local
pide a Ollama una actividad
hazlo con la IA local
responde usando Ollama
consulta tu IA local y dime...
```

Ejemplos completos:

```text
usa la IA local para explicarme qué eres
consulta Ollama y dame una actividad sencilla
pregunta al modelo local cómo puedo practicar memoria
usa ahootsa-local para crear una pregunta fácil
hazlo con la IA local y en lenguaje sencillo
```

---

## 9. Frases que NO deben activar ask_ollama

Estas frases deben usar herramientas originales:

```text
baila
para el baile
saluda
haz una emoción alegre
estás contento
mira a la izquierda
mira a la derecha
mueve la cabeza
usa la cámara
recuerda esto
olvida eso
```

Mapa recomendado:

```text
baila                  → dance
para                   → stop_dance / stop_emotion
saluda                 → play_emotion
haz emoción alegre     → play_emotion
mira a la izquierda    → move_head
mira alrededor         → sweep_look
usa la cámara          → camera
recuerda esto          → remember
olvida eso             → forget
```

---

## 10. Posibilidades de uso de Ollama local

### Modo 1 — Activación explícita

Solo se usa Ollama cuando el usuario lo pide:

```text
usa la IA local...
consulta Ollama...
```

Ventaja:

```text
más estable
más controlado
menos riesgo de romper conversación
```

Este debe ser el modo de la versión base.

---

### Modo 2 — Activación por categoría

Se puede configurar el perfil para que use Ollama en ciertos casos:

```text
- actividades educativas
- ejercicios sencillos
- explicaciones adaptadas
- reformulación en lectura fácil
- generación de preguntas
- apoyo cognitivo
```

Ejemplo:

```text
Usuario: dame una actividad sencilla
→ podría llamar a ask_ollama por defecto
```

Pero esto requiere escribirlo claramente en `instructions.txt`.

---

### Modo 3 — Respuesta local preferente

Se podría pedir que muchas respuestas de contenido pasen por Ollama.

Ejemplo:

```text
Preguntas de conocimiento o actividades → ask_ollama
Órdenes de robot → herramientas originales
```

Limitación:

```text
La IA remota sigue escuchando y decidiendo.
No es 100% local.
```

---

### Modo 4 — 100% local futuro

No corresponde a esta base.

Requeriría otra arquitectura:

```text
STT local
+ Ollama local
+ TTS local
+ controlador local de herramientas
```

Eso ya no sería simplemente un fork seguro de la app oficial.

---

## 11. Recomendación para la versión base

La versión base debe llamarse:

```text
Ahootsa Realtime Ollama v0.4.34 Base Original Resources
```

Debe hacer:

```text
- usar app oficial intacta
- añadir perfil Ahootsa
- añadir ask_ollama
- mantener herramientas originales
- no usar JSON/OGG local
- no usar media.play_sound
- no modificar frontend
- no modificar perfiles oficiales
- no duplicar herramientas originales
```

Herramientas activas:

```text
dance
stop_dance
play_emotion
stop_emotion
camera
idle_do_nothing
move_head
sweep_look
remember
forget
ask_ollama
```

---

## 12. Instrucción recomendada para instructions.txt

Fragmento recomendado:

```text
Usa siempre las herramientas originales del robot para movimientos, emociones, bailes, cámara y memoria.

Si el usuario pide bailar, usa dance.
Si el usuario pide parar, usa stop_dance o stop_emotion.
Si el usuario pide una emoción, usa play_emotion.
Si el usuario pide mover la cabeza o mirar, usa move_head o sweep_look.
Si el usuario pide cámara, usa camera.
Si el usuario pide recordar u olvidar, usa remember o forget.

No uses ask_ollama para mover el robot.

Usa ask_ollama solo cuando el usuario pida explícitamente usar la IA local, Ollama, el modelo local o ahootsa-local.

Ejemplos que deben activar ask_ollama:
- "usa la IA local"
- "consulta Ollama"
- "pregunta al modelo local"
- "usa ahootsa-local"
- "hazlo con la IA local"

Cuando uses ask_ollama, explica al usuario que vas a consultar la IA local.
```

---

## 13. Conclusión

La base estable debe entenderse así:

```text
Ahootsa = app oficial intacta + perfil propio + ask_ollama
```

`ask_ollama` no funciona por defecto para todo.

En la base segura:

```text
Se activa con orden concreta.
```

Se puede ampliar después para que ciertas categorías usen Ollama automáticamente, pero eso debe hacerse de forma controlada y documentada.

