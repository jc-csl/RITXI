# Diagnóstico de micro en Ritxi v4.3

## Problema detectado en los logs

En la sesión `session_20260624_074026_pid14048` el daemon de Reachy estaba conectado y los movimientos funcionaban, pero la conversación no avanzaba porque el STT del navegador devolvía repetidamente:

```text
Error micro PC: aborted
```

Eso significa que la Web Speech API del navegador iniciaba la escucha, pero la abortaba antes de producir una frase final. En ese estado Ritxi no tiene texto válido para enviar a Ollama.

## Cambios de la v4.3

- Nuevo modo de micro `continuo robusto`.
- Nuevo modo `frase corta`.
- Nuevo modo `manual + enviar`.
- Diagnóstico visible de micro/STT en el panel.
- Reintentos más lentos cuando Chrome/Edge devuelve `aborted` o `no-speech`.
- Ya no se entra en bucle rápido de arranque/parada del micrófono.
- Registro más detallado de resultados parciales y finales del STT.

## Uso recomendado

1. Abre la app en Chrome o Edge.
2. Pulsa `Tutor DI tiempo real`.
3. En `Modo micro`, deja `continuo robusto`.
4. Pulsa `Activar conversación tiempo real`.
5. Habla con frases cortas.
6. Si no funciona, cambia a `frase corta`.
7. Si sigue fallando, usa `manual + enviar` para comprobar que Ollama, TTS y movimientos funcionan.

## Si Chrome sigue transcribiendo mal

La Web Speech API depende del navegador, del idioma instalado, del permiso de micrófono y de servicios internos de reconocimiento. No permite controlar bien VAD, ruido, modelo, sensibilidad ni idioma real.

Para una versión de producción offline/local, se recomienda sustituir este STT por un servidor persistente local:

```text
Micro PC / navegador → audio WAV → FastAPI → Whisper/faster-whisper → texto → Ollama
```

La arquitectura de Ritxi ya está preparada para mantener el resto del ciclo igual.
