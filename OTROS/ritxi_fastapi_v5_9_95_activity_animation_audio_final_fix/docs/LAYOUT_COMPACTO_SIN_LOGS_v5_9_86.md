# Layout compacto sin logs visibles v5.9.86

## Logs

Se elimina el panel visual:

```text
Registros del sistema
```

Se mantienen los logs internos:

```text
logClient() → /api/log/client
```

## Layout

Objetivo: trabajar con la ventana de control y la ventana del robot visibles a la vez.

Cambios:

```text
app-shell max-width: 1520px
chat con más proporción
fichas más compactas
acciones minmax: 96px
modo portátil minmax: 88px
```

## Código eliminado o neutralizado

```text
panel logs-panel en HTML
listeners de pauseLogsBtn / clearLogsBtn / exportLogsBtn / logSearch / data-log-filter
renderLogs() queda como no-op
exportLogs() eliminado
```
