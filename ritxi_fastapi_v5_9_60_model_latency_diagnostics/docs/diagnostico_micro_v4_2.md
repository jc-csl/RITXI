# Diagnóstico del problema de micro en v4.1 y corrección en v4.2

En el log real subido para la sesión `session_20260624_070443_pid9188` se observó:

1. El daemon llegó a conectar inicialmente.
2. Ollama no respondió dentro del timeout y se usó fallback mock.
3. `pyttsx3` inició la voz y tardó más de 250 segundos en finalizar.
4. Durante ese tiempo el echo guard mantuvo `speaking=true` y el micro no podía rearmarse.
5. Más tarde, el daemon dejó de estar disponible y los movimientos se saltaron por `not_connected`.

La v4.2 corrige el punto más crítico cambiando el modo recomendado a TTS del navegador. Así el navegador sabe cuándo termina la voz (`speechSynthesis.onend`) y rearma el micro de forma natural.

## Modo recomendado

Usar:

```text
RITXI_TTS_PROVIDER=browser
```

No usar `pyttsx3` para conversación continua salvo prueba experimental.

## Señales a revisar en logs

- `client_speaking_update` con `speaking=true`: el navegador empieza a hablar.
- `client_speaking_update` con `speaking=false`: el navegador terminó.
- `micro_on`: el backend permite reescuchar.
- `Tiempo real: armando micro`: el navegador vuelve a activar reconocimiento.
