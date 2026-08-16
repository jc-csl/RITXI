# Cambios Ahootsa 0.12.8.6

## Saludo de sesión

- La creación de una persona continúa guardando únicamente en SQLite.
- Al pulsar `Preparar`, `ahootsa_session` se reconstruye desde
  `ahootsa_default`.
- El primer turno debe pronunciar el nombre preferido completo.
- Con intereses registrados, Aocha los menciona y ofrece hablar de ellos.
- Sin intereses, utiliza el saludo definido por la actividad y el nivel.

## Bailes

- La herramienta espera a que termine el baile.
- Al acabar, limpia automáticamente movimiento y audio.
- Conserva el micrófono.
- Devuelve `status: completed`.
- Aocha confirma brevemente el final y formula una pregunta sencilla.

## Perfiles implicados

```text
ahootsa          modo anónimo
ahootsa_default  plantilla permanente de sesiones
ahootsa_session  perfil temporal reconstruido al pulsar Preparar
```
