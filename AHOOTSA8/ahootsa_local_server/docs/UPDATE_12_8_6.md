# Update 12.8.6 — Bailes con continuación y saludo personalizado

## Problemas corregidos

### El baile terminaba y Aocha permanecía en silencio

La herramienta anterior devolvía `status: started` inmediatamente y tenía
`needs_response = False`. Cuando el audio y el movimiento terminaban, el
backend no recibía un nuevo resultado que provocara una respuesta hablada.

La versión 1.4 de `ahootsa_dances.py`:

1. permanece ejecutándose hasta que termina el baile;
2. detiene y limpia la cola de movimiento;
3. limpia la música sin detener el micrófono;
4. devuelve `status: completed`;
5. provoca una respuesta hablada breve para continuar la conversación.

### El saludo preparado podía perder el nombre

`greeting.txt` contenía solo una frase sugerida. El modelo podía resumirla y
comenzar directamente por la pregunta de la actividad.

El servicio genera ahora una orden literal de primer turno. El saludo real:

- incluye siempre el nombre preferido;
- menciona los intereses cuando están registrados;
- ofrece hablar de esos intereses o iniciar la actividad;
- utiliza el saludo de la actividad cuando no existen intereses;
- queda registrado en `session_context.json` y en los eventos de sesión.

## Arquitectura conservada

- Crear una persona modifica únicamente SQLite.
- Pulsar `Preparar` copia `ahootsa_default` sobre `ahootsa_session`.
- `instructions.txt` recibe el contexto temporal.
- `greeting.txt` recibe la orden literal del saludo.
- `tools.txt` y `voice.txt` proceden de la plantilla.
- El perfil general `ahootsa` no recibe datos personales.
- No se modifica `reachy_mini_conversation_app/src`.


> Complementado por la actualización 12.8.7, que limita los relatos largos y añade recuperación de audio sin cerrar la sesión.
