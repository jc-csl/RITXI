# Prueba 12.4.2.2 — Corrección de codificación del proceso Python

## Causa

El verificador corregido funcionaba, pero su prueba funcional ejecutaba un
segundo proceso Python con:

```python
text=True, encoding="utf-8"
```

En Windows, ese proceso hijo podía escribir mediante la página de códigos
local. El byte `0xFA`, correspondiente a una `ú` en Windows-1252, no es válido
como inicio de carácter UTF-8. Por eso el hilo lector de `subprocess` fallaba
con:

```text
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xfa
```

Después, `completed.stdout` quedaba en `None` y aparecía el segundo error.

## Corrección

- El verificador emite JSON ASCII mediante `ensure_ascii=True`.
- El proceso hijo recibe:
  - `PYTHONUTF8=1`
  - `PYTHONIOENCODING=utf-8`
- La prueba captura bytes, no texto.
- La decodificación intenta UTF-8 y utiliza una alternativa segura si fuera
  necesario.
- Se evita llamar `.strip()` sobre `None`.

## Alcance

Solo se sustituyen archivos de prueba:

```text
tests/verificar_eventos_sqlite_12_4_2.py
tests/probar_verificador_sqlite_12_4_2_2.py
tests/COMPROBAR_VERIFICADOR_SQLITE_12_4_2_2.ps1
```

No se modifica el código del servidor, SQLite, los perfiles ni la aplicación
oficial.
