# 14 — Sin voz Windows idle v0.4.45

## Problema

Se escuchaba la voz de Windows además de la voz seleccionada en Reachy Desktop.

## Causa

El recordatorio de presencia añadido en versiones anteriores usaba Windows SAPI para decir:

```text
Sigo aquí. Cuando quieras, podemos jugar o hacer otra actividad.
```

Esa voz no es la voz de Reachy Desktop. Por eso se mezclaba con Sohee/Aiden/etc.

## Corrección

```text
- El recordatorio hablado queda desactivado por defecto.
- El instalador desactiva AHOOTSA_IDLE_REMINDER_ENABLED.
- Se añade DESACTIVAR_VOZ_WINDOWS_IDLE_AHOOTSA.ps1.
```

## Desactivar ahora

```powershell
powershell -ExecutionPolicy Bypass -File .\DESACTIVAR_VOZ_WINDOWS_IDLE_AHOOTSA.ps1
```

Después hay que cerrar completamente Reachy Mini Desktop y abrirlo otra vez.

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_IDLE_VOZ_WINDOWS_AHOOTSA.ps1
```

Debe decir:

```text
OK: el recordatorio idle hablado está desactivado.
```

## Activarlo explícitamente

No recomendado si molesta la voz de Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\CONFIGURAR_RECORDATORIO_IDLE_AHOOTSA.ps1 -Enable -Seconds 20 -RepeatSeconds 60
```
