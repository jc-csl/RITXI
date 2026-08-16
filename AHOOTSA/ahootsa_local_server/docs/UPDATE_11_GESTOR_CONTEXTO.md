# Update 11 — Gestor de contexto

## Objetivo

Construir una representación única y coherente del estado de una sesión para que
los módulos posteriores —Reachy, actividades, LLM, ASR y TTS— utilicen la misma
información.

## Contexto generado

El contexto contiene:

- sesión;
- usuario y nombre preferido;
- perfil de accesibilidad;
- memoria permanente activa;
- actividad y paso actuales;
- estado conversacional;
- últimos eventos;
- contadores.

## API

### `GET /context/active`

Construye el contexto actual sin escribir archivos.

### `POST /context/active/snapshot`

Construye el mismo contexto y lo guarda como JSON UTF-8 en
`data/context_snapshots`.

## Alcance

El snapshot sirve para depuración y reproducción manual. En esta versión no se
implementa todavía una reproducción automática completa de la sesión.

## Persistencia

No se crean tablas nuevas. La fuente de verdad continúa siendo SQLite y el
snapshot es una copia de diagnóstico.
