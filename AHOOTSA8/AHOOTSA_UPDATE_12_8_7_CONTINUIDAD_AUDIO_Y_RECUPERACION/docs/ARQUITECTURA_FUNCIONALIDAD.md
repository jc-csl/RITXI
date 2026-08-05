# ARQUITECTURA Y FUNCIONALIDAD — AHOOTSA 0.12.8.7

## Continuidad de la conversación

La Conversation App sigue siendo el motor principal. No se modifica su carpeta
`src`.

Para reducir turnos de salida excesivamente largos, los perfiles externos
indican:

- máximo habitual de cuatro frases cortas;
- máximo aproximado de 45 segundos;
- historias divididas en partes;
- una única pregunta;
- espera obligatoria de un nuevo turno de usuario.

## Recuperación de audio

`RECUPERAR_AUDIO_SESION.ps1` reinicia únicamente la Conversation App y mantiene:

- servidor local 8100;
- daemon 8000;
- sesión identificada;
- usuario;
- actividad;
- nivel;
- eventos;
- carpeta y log de la sesión.

Utiliza temporalmente `external_finish_requested.flag` para impedir que el
cierre técnico sea interpretado como finalización de la sesión.

## Informe

La versión 1.2 incorpora `audio_diagnostics` y puede advertir de un posible
bloqueo de escucha cuando el último turno es de Aocha y no se registra una
respuesta antes de un cierre muy posterior.
