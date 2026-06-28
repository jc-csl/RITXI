# Manual de usuario de Ritxi v5.9.61

## 1. Qué es Ritxi

Ritxi es una aplicación local para trabajar con un asistente conversacional y, si se desea, con Reachy Mini o su simulación.

Permite usar:

- texto escrito;
- micrófono;
- IA local con Ollama;
- voz del navegador;
- movimientos del robot;
- actividades de lenguaje, comunicación, juegos y apoyo emocional.

---

## 2. Arranque rápido

### 1. Instalar modelos Ollama

Ejecutar:

```text
0_INSTALAR_MODELOS_OLLAMA.cmd
```

### 2. Instalar Ritxi

Ejecutar:

```text
1_INSTALAR_RITXI.cmd
```

### 3. Iniciar daemon Reachy/MuJoCo

Ejecutar:

```text
2_INICIAR_DAEMON_RITXI.cmd
```

### 4. Iniciar panel

Ejecutar:

```text
3_RUN_RITXI.cmd
```

### Opción combinada

Ejecutar:

```text
5_INSTALAR_E_INICIAR_DAEMON_RITXI.cmd
```

Hace instalación e inicio de daemon seguidos.

---

## 3. Panel principal

La parte superior muestra:

```text
Modo de interacción | Estado actual | Actividad / ejecución
```

### Modo de interacción

Hay tres modos:

#### Texto + IA

Usar cuando se quiere escribir.

- texto activo;
- IA local activa;
- micro apagado;
- robot apagado.

#### Micro + IA

Usar cuando se quiere hablar con el micrófono.

- texto activo;
- micro activo;
- IA local activa;
- robot apagado.

#### Completo

Usar cuando se quiere texto, micro, IA, voz y robot.

- texto activo;
- micro activo;
- IA activa;
- voz activa;
- robot activo.

---

## 4. Elegir modelo de IA

En el chat se puede elegir modelo.

Recomendación:

```text
gemma3:1b      recomendado
qwen3:0.6b     más rápido
llama3.2:1b    rápido
llama3.2:3b    más lento, mayor calidad
```

Si Ritxi tarda mucho, comprobar que no esté seleccionado `llama3.2:3b`.

---

## 5. Usar texto

1. Seleccionar **Texto + IA**.
2. Escribir en la caja.
3. Pulsar **➤** o Enter.

El modo texto debe funcionar aunque el micro esté apagado.

---

## 6. Usar micro

1. Seleccionar **Micro + IA** o **Completo**.
2. Pulsar **Activar micro** si no está activo.
3. Hablar claro y esperar la respuesta.

El texto sigue disponible como respaldo.

---

## 7. Usar actividades

Las actividades están en pestañas:

```text
Emociones
Actividades
Juegos
Tutor
Config.
```

Cada ficha tiene una barra inferior de color:

```text
gris     solo reproduce
azul     interacción corta
morado   interacción larga
dorado   máxima interacción
```

### Máxima interacción

Actividades como:

```text
Historia por turnos
Cuento por turnos
Inventar final
Describir imagen
Elegir emoción
```

mantienen contexto durante varios turnos.

Para terminar se puede decir o escribir:

```text
terminar
fin
parar
otra actividad
```

---

## 8. Estado actual

La parte superior indica:

- si Ritxi está listo;
- si está pensando;
- si ejecuta una actividad;
- si hay algo en ejecución.

El botón **Detener** para acciones está en la zona:

```text
Actividad / ejecución
```

---

## 9. Audio

El panel de audio permite seleccionar:

- micrófono;
- altavoz;
- probar audio.

En **Texto + IA** el audio puede estar apagado.

---

## 10. Configuración

La pestaña **Config.** permite editar archivos importantes:

```text
app/prompts/system_prompt.txt
app/core/config.py
app/config/model_presets.json
profiles/characters/ritxi_tutor_comunicacion_di.json
.env.example
app/config/stt_vocabularies/*.json
```

Solo editar si se sabe qué se está cambiando.

---

## 11. Logs

Los logs están en:

```text
logs/
```

Sirven para diagnosticar:

- lentitud de Ollama;
- fallos de micro;
- errores de STT;
- errores de robot;
- bloqueos de interfaz.

Archivos habituales:

```text
session_*.jsonl
session_*.log
lanzador_*.log
reachy_daemon_*.log
```

---

## 12. Problemas frecuentes

### Escribo texto y no responde

Revisar:

1. que el panel esté iniciado;
2. que Ollama esté abierto;
3. que el modelo esté instalado;
4. que no esté seleccionado un modelo muy lento.

### Tarda mucho

Revisar el modelo.

Usar:

```text
gemma3:1b
```

o:

```text
qwen3:0.6b
```

Evitar `llama3.2:3b` para pruebas rápidas.

### El micro no escucha

Revisar:

1. permisos del navegador;
2. micrófono elegido;
3. modo Micro + IA o Completo;
4. logs de STT.

### El robot no se mueve

Revisar:

1. daemon iniciado;
2. modo Completo;
3. logs del daemon;
4. conexión con Reachy/MuJoCo.

---

## 13. Cerrar Ritxi

Ejecutar:

```text
4_SALIR_RITXI.cmd
```

También se puede usar el botón **Salir** del panel.


## Nota v5.9.62

En v5.9.62 se separan claramente tres conceptos:

```text
Texto + IA rápida  → conversación escrita con IA local, micro apagado
TTS                → lectura en voz alta del texto de la respuesta
Sonido emocional   → sonidos breves oficiales de Ritxi/emociones
```

Desactivar TTS no debe bloquear los sonidos emocionales de Ritxi.
El modo por defecto es Texto + IA rápida con modelo `qwen3:0.6b`.


## Nota v5.9.63

Se añade el modo `Texto + IA + Robot`.

La diferencia entre controles queda así:

```text
Texto + IA rápida   → texto + IA, micro apagado, sin lectura TTS, con sonidos emocionales.
Texto + IA + Robot  → igual que Texto + IA, pero también mueve el robot.
Micro + IA          → micro/STT + IA + voz, texto disponible, robot parado.
Completo            → texto + micro + IA + voz + robot.
```

`Sin sonido` en modo texto significa no leer en voz alta el texto completo de la respuesta.
No significa bloquear los sonidos breves de emociones de Ritxi.
