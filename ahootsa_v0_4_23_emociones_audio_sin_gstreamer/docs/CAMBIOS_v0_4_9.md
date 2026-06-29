# Cambios v0.4.9 - Base Original Resources

Esta versión se declara como nueva base estable del proyecto Ahootsa Realtime Ollama.

## Objetivo

Mantener todos los recursos originales de la app oficial de Reachy Mini Conversation App sin alterarlos, y añadir únicamente la posibilidad de consultar Ollama local mediante `ask_ollama`.

## Cambios frente a v0.4.8

```text
- Se actualiza versión a 0.4.9.
- Se añade docs/ARQUITECTURA_FUNCIONALIDAD.md.
- Se añade docs/ARQUITECTURA_BASE_ESTABLE_ASK_OLLAMA.md.
- Se endurece instructions.txt para que ask_ollama NO se use por defecto.
- ask_ollama se activa solo por orden explícita: IA local, Ollama, modelo local o ahootsa-local.
- Se mantiene la limpieza de variables experimentales de emociones locales.
- Se mantiene desactivado cualquier control manual JSON/OGG.
- Se mantiene desactivado media.play_sound().
```

## Recursos que no deben tocarse

```text
- interfaz web original
- micro
- voz realtime
- backend realtime
- perfiles oficiales
- herramientas originales
- emociones y bailes originales
- cámara
- memoria
- cola de movimientos
```

## Herramientas activas

Originales:

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

Nueva:

```text
ask_ollama
```

## Regla de ask_ollama

```text
No se activa por defecto.
Solo se activa si el usuario pide explícitamente IA local, Ollama, modelo local o ahootsa-local.
```

Ejemplos que activan `ask_ollama`:

```text
usa la IA local
consulta Ollama
pregunta al modelo local
usa ahootsa-local
hazlo con la IA local
```

Ejemplos que NO activan `ask_ollama`:

```text
baila
saluda
mueve la cabeza
usa la cámara
recuerda esto
olvida eso
```
