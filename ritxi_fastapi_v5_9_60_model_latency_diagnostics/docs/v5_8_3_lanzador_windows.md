# Ritxi v5.8.3 · Lanzador Windows corregido

La versión v5.8.2 podía fallar con:

```text
No se esperaba 120 en este momento.
```

La causa era un bucle en `cmd` con variables dentro de bloques `if`. En Windows CMD eso puede romperse al expandir variables antes de ejecutar el bloque.

Solución aplicada:

- `ejecutar_windows.cmd` llama a `ejecutar_windows.ps1`.
- PowerShell gestiona las esperas de puertos.
- El navegador se abre solo después de:
  - daemon disponible en `127.0.0.1:8000` o timeout controlado;
  - FastAPI disponible en `127.0.0.1:8080` o timeout controlado;
  - 10 segundos extra de margen.

Uso:

```cmd
instalar_windows.cmd
ejecutar_windows.cmd
```

O:

```cmd
instalar_y_ejecutar_windows.cmd
```
