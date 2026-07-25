# Update 10 — Motor modular de actividades

## Objetivo

Separar las actividades del núcleo del servidor y ofrecer una interfaz común.

## Interfaz

Cada actividad implementa:

- `start(context)`
- `next_step(current_step, context)`
- `evaluate(current_step, answer, context)`
- `serialize()`

## Registro

`ActivityEngine` mantiene el catálogo de actividades disponibles. Añadir una
actividad nueva no requiere modificar el gestor de conversación.

## Persistencia

La actividad actual y su paso se reconstruyen a partir de los eventos:

- `activity_started`
- `robot_message`
- `user_response`
- `hint_given`
- `activity_completed`

## Actividades iniciales

### emotions

Actividad cerrada y evaluable con tres pasos.

### preferences

Actividad abierta que recoge respuestas sin decidir todavía si deben convertirse
en memoria permanente. Esa decisión quedará para una capa posterior supervisada.

## API

- `GET /activities`
- `POST /activities/active/start`
- `GET /activities/active`
- `POST /activities/active/answer`
