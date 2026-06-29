# v0.4.17 — Uso integrado en Reachy Mini Desktop

## Idea importante

No hay que abrir manualmente el puerto `7860` en otra ventana.

Reachy Mini Desktop debe mostrar la interfaz de conversación integrada a la derecha, igual que en la app oficial.

El puerto `7860` solo es la dirección interna del webserver de la app. Desktop la usa para incrustar la interfaz.

## Flujo correcto

```text
1. Abrir Reachy Mini Desktop.
2. Ir a Applications.
3. Pulsar Start en Ahootsa Realtime Ollama.
4. Esperar a que aparezca App Running.
5. Usar el panel integrado de la derecha.
```

No hace falta abrir:

```text
http://127.0.0.1:7860
```

Eso solo sirve como diagnóstico si el panel integrado no carga.

## Si no aparece integrado

Comprobar:

```text
- que la app esté arrancada desde Desktop;
- que no haya otro proceso usando 7860;
- que la metadata apunte a http://127.0.0.1:7860;
- que la app no se haya abierto como script externo independiente.
```

## Respuestas de Ollama

Esta versión también ajusta `ask_ollama` para que las respuestas sean mejores para voz:

```text
- máximo 3 frases;
- sin markdown;
- sin listas largas;
- sin títulos con asteriscos;
- lenguaje fácil;
- instrucciones cortas.
```
