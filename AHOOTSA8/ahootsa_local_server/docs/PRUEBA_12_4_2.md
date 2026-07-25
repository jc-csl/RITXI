# Prueba 12.4.2 — registro explícito y verificación SQLite

La prueba 12.4.1 recibió identificadores de evento, pero al consultar la sesión no encontró uno de ellos. Para eliminar la ambigüedad, esta versión:

- publica cada evento en `/sessions/{session_id}/events`;
- exige que la respuesta devuelva el mismo `session_id`;
- consulta directamente `data/ahootsa.db` con `sqlite3`;
- verifica los nueve identificadores antes y después del cierre;
- compara también el resumen de sesión;
- trata el listado API como diagnóstico adicional.

No modifica el servidor ni el esquema de datos.
