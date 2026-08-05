# Update 12.8.5 — Voz Sohee y comprobador corregido

## Corrección del comprobador 12.8.4

El comprobador anterior buscaba la ruta `panel-12-8-4` dentro del HTML,
aunque esa ruta pertenece a `panel_mvp.py`. Por eso mostraba un falso error.

La versión 12.8.5 comprueba por separado:

- las funciones de edición dentro del HTML;
- la ruta del panel dentro de la API Python.

No es necesario instalar 12.8.4 antes de 12.8.5.

## Voz

Se configura `Sohee` en:

```text
external_profiles/ahootsa/voice.txt
external_profiles/ahootsa_session/voice.txt
profile_defaults/ahootsa_default/voice.txt
```

Esto cubre:

- modo anónimo;
- perfil de sesión actualmente generado;
- futuras sesiones creadas desde la plantilla.

## Instrucciones iniciales

Los tres perfiles reciben un bloque prioritario que solicita:

- español estándar;
- pronunciación neutral;
- ausencia de acentos regionales o extranjeros marcados;
- dicción nítida;
- ritmo moderado;
- pausas naturales;
- frases cortas.

El timbre y una posible coloración propia de la voz dependen del sintetizador.
Las instrucciones pueden mejorar claridad y neutralidad, pero no garantizan
eliminar por completo el acento inherente de una voz.

## Panel

La actualización conserva la edición estable de 12.8.4 y utiliza:

```text
http://127.0.0.1:8100/panel-12-8-5
```
