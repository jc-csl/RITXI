# v0.4.35 — Fix dataclass del servidor Memory

## Error corregido

```text
AttributeError: 'NoneType' object has no attribute '__dict__'
```

## Causa

El script de prueba cargaba `memory_pairs_game_server.py` con `importlib.util.module_from_spec()` sin registrar el módulo en `sys.modules` antes de ejecutar `@dataclass`.

Python `dataclasses` necesita que el módulo exista en `sys.modules`.

## Corrección

```text
- Se elimina @dataclass del servidor del juego.
- MemoryPairsGame pasa a ser una clase normal.
- Se mantiene start_server().
- Se refuerzan los scripts de prueba para registrar el módulo.
```

## Pruebas

```powershell
powershell -ExecutionPolicy Bypass -File .\PROBAR_MEMORY_MODULO_DIRECTO.ps1
powershell -ExecutionPolicy Bypass -File .\PROBAR_MEMORY_START_SERVER.ps1
```
