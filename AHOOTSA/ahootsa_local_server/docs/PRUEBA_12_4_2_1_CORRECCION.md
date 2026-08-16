# Prueba 12.4.2.1 — Corrección del verificador SQLite

## Causa

El archivo Python contenía secuencias literales `\n` dentro de la construcción
de la consulta SQL:

```python
'SELECT ... ' \n 'value_text ...'
```

Python las interpretó como caracteres inesperados después de una continuación
de línea y produjo:

```text
SyntaxError: unexpected character after line continuation character
```

La prueba no llegó a consultar SQLite. El error no demuestra que los eventos
no se registrasen; solo demuestra que el verificador no pudo ejecutarse.

## Corrección

La consulta se construye ahora mediante una cadena multilínea válida:

```python
sql = f"""
    SELECT ...
    FROM session_events
    WHERE id IN ({placeholders})
    ORDER BY id
"""
```

También se añaden:

- validación de identificadores vacíos o inválidos;
- captura de errores SQLite en JSON;
- comprobación de que se encuentran todos los eventos;
- prueba funcional con una base SQLite temporal.

## Alcance

Solo se sustituye:

```text
tests/verificar_eventos_sqlite_12_4_2.py
```

No se modifica el servidor Python, la base de datos, los perfiles ni la
aplicación oficial.
