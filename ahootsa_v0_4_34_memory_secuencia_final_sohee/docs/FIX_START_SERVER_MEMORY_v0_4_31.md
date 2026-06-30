# v0.4.34 — Fix start_server del juego Memory

## Error corregido

```text
AttributeError: module 'ahootsa_memory_pairs_game_server' has no attribute 'start_server'
```

## Causa probable

Había una versión incompleta o cacheada de `memory_pairs_game_server.py` cargada por el runner de Reachy Mini.

## Corrección

```text
- Se sustituye memory_pairs_game_server.py por una versión completa.
- Se valida que exista start_server().
- Las herramientas ya no reutilizan un módulo cacheado antiguo.
- Se añade REPARAR_MEMORY_START_SERVER.ps1.
```

## Reparación rápida

Con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_MEMORY_START_SERVER.ps1
```

## Prueba directa

```powershell
powershell -ExecutionPolicy Bypass -File .\PROBAR_MEMORY_START_SERVER.ps1
```

Debe abrir:

```text
http://localhost:7870/
```

con cartas azules y números blancos grandes.
