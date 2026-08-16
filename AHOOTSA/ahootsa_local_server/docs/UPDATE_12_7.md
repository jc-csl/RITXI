# Update 12.7 — Panel compacto, usuarios y cierre completo

## Problemas corregidos

1. El botón anterior solo creaba a Álex como ejemplo.
2. No existía un formulario para crear personas reales.
3. Una sesión podía quedar bloqueada aunque se utilizara un script de cierre.
4. Finalizar desde el panel guardaba el resumen, pero no generaba el PDF.
5. Los controles eran grandes y obligaban a recorrer verticalmente la página.
6. La información de la ficha no podía modificarse directamente.

## Nuevo panel

La pantalla se organiza en tres columnas y ocupa la ventana completa:

- ficha de la persona;
- actividad, preparación y seguimiento;
- finalización, informe y bloqueo.

En un monitor de escritorio no hay desplazamiento de página. Cada columna puede
desplazarse internamente solo cuando la resolución es pequeña.

## Gestión de personas

El panel permite:

- crear una persona nueva;
- generar automáticamente el identificador;
- modificar todos los datos;
- editar con doble clic;
- guardar o cancelar;
- vaciar campos opcionales;
- borrar la ficha si no tiene sesiones;
- ocultarla si tiene sesiones, conservando informes e historial.

## Finalización

El botón de finalización:

1. crea una marca para evitar dos generadores simultáneos;
2. cierra la Conversation App;
3. espera a que Windows termine el log;
4. finaliza la actividad y la sesión;
5. elimina el bloqueo de sesión;
6. restaura el perfil base;
7. importa la conversación;
8. genera PDF, HTML, JSON y transcripción;
9. habilita la preparación de una sesión nueva.

## Recuperación

El botón `Liberar`:

- cierra la Conversation App;
- finaliza una sesión activa que haya quedado bloqueada;
- elimina `active_session.json`;
- restaura `ahootsa_session`;
- permite preparar una sesión nueva.
