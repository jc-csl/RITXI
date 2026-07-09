# Ahootsa 5.0.31 — logs por ejecución y diagnóstico útil

## Problema observado

En la versión anterior seguían apareciendo errores de escritura de logs:

```text
Add-Content : El proceso no puede obtener acceso al archivo ... pantalla.log porque está siendo utilizado en otro proceso.
```

Además, el script `ESPERAR_5_BACKEND_REALTIME_LISTO.ps1` quedó con un error de sintaxis:

```text
La expresión de asignación no es válida.
[int]$TimeoutSeconds = 120,
```

También se detectó que la sesión de logs podía reutilizar un timestamp antiguo, por ejemplo una ejecución iniciada a las 08:12 seguía usando:

```text
Session: 20260708_074618
Pantalla: ahootsa5_20260708_074618_pantalla.log
```

Esto mezclaba ejecuciones distintas y hacía difícil corregir el código con el último error real.

## Qué cambia la 5.0.31

La versión 5.0.31 hace cuatro cambios:

1. Cada ejecución genera un timestamp nuevo `yyyyMMdd_HHmmss`.
2. El script `ESPERAR_5_BACKEND_REALTIME_LISTO.ps1` se reconstruye con una versión segura y sintácticamente válida.
3. Las escrituras `Add-Content` contra `$Log` se vuelven tolerantes con `-ErrorAction SilentlyContinue`.
4. Se añade un script de resumen que genera un log final limpio:

```text
D:\RITXI\logs\ULTIMA_EJECUCION_AHOOTSA_CORRECCION.log
```

Este archivo contiene solo líneas útiles para depurar: errores, avisos, tracebacks, 404, timeouts, problemas de conexión y cola final de los logs de la última sesión.

## Archivos modificados en la carpeta 5.0.25

El parche revisa la carpeta:

```text
D:\RITXI\5_0_34_ahootsa_completa_consolidada_b
```

y modifica, si existen:

```text
LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
ESPERAR_5_BACKEND_REALTIME_LISTO.ps1
FORZAR_5_VOZ_SOHEE_COMPLETA.ps1
otros .ps1 con Add-Content contra $Log
```

Antes de modificar, crea copias de seguridad con este formato:

```text
archivo.ps1.bak_5_0_31_yyyyMMdd_HHmmss
```

## Uso recomendado

Ejecutar:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_0_31_AHOOTSA_MUJOCO_WEB.ps1
```

Si falta MuJoCo:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_0_31_AHOOTSA_MUJOCO_WEB.ps1 -InstallMujoco
```

Después de una prueba, para preparar el log útil para corregir código:

```powershell
powershell -ExecutionPolicy Bypass -File .\1_RESUMIR_ULTIMA_EJECUCION_5_0_31.ps1
```

El archivo importante será:

```text
D:\RITXI\logs\ULTIMA_EJECUCION_AHOOTSA_CORRECCION.log
```

## Qué enviar para depurar

Para corregir la siguiente incidencia, basta con enviar:

```text
D:\RITXI\logs\ULTIMA_EJECUCION_AHOOTSA_CORRECCION.log
```

Si el problema es muy raro, enviar también los tres logs completos de esa sesión:

```text
ahootsa5_YYYYMMDD_HHMMSS_pantalla.log
ahootsa5_YYYYMMDD_HHMMSS_runtime.log
ahootsa5_YYYYMMDD_HHMMSS_eventos.jsonl
```

## Relación con versiones anteriores

La 5.0.31 mantiene:

- 5.0.27: endpoints `/status`, `/mic`, `/voices/current`, `/voices`.
- 5.0.29: bloqueo de voz Windows/navegador para que solo hable Ahootsa.
- 5.0.30: wrapper PowerShell corregido.

Sustituye la parte de logs de la 5.0.28 porque esa corrección no cubría todos los scripts y podía romper `ESPERAR_5_BACKEND_REALTIME_LISTO.ps1` si se insertaba mal el bloque de funciones.
