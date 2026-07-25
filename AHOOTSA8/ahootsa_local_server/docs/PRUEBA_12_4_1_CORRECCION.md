# Prueba 12.4.1 — Corrección de la verificación de eventos

## Causa del error

La prueba 12.4 insertó correctamente los nueve eventos y recibió un
identificador para cada uno. El fallo apareció al intentar localizar después
los eventos mediante el campo `metadata.test_run_id`.

En el entorno probado, esa búsqueda devolvió cero coincidencias aunque las
inserciones habían respondido correctamente.

## Corrección

La prueba 12.4.1 utiliza como evidencia principal los identificadores que
devuelve SQLite/API al crear cada evento:

1. guarda los nueve identificadores;
2. recupera todos los eventos de la sesión;
3. verifica que cada identificador exista;
4. compara tipo, origen y texto;
5. finaliza la sesión;
6. vuelve a recuperar los mismos identificadores;
7. guarda los identificadores en el informe;
8. permite repetir la comprobación después de reiniciar el servidor.

También lee las respuestas HTTP explícitamente como UTF-8 para evitar textos
como `Â¿QuÃ©`.

## Alcance

No modifica:

- código Python;
- esquema SQLite;
- perfiles;
- `.env`;
- aplicación oficial;
- Conversation App.

Esta prueba valida el registro determinista del servidor local. No valida aún
la captura automática de audio o de la conversación realtime.
