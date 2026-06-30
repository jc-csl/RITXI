# 12 — Voz Sohee, recordatorio idle y bailes del panel v0.4.42

## Voz Sohee

Si Reachy Mini Desktop elige Aiden por ser la primera voz de la lista:

```powershell
powershell -ExecutionPolicy Bypass -File .\FORZAR_VOZ_SOHEE_TOTAL.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_VOZ_SOHEE_TOTAL.ps1
```

## Recordatorio de presencia

Primer aviso a los 20 segundos:

```powershell
powershell -ExecutionPolicy Bypass -File .\CONFIGURAR_RECORDATORIO_IDLE_AHOOTSA.ps1 -Seconds 20 -RepeatSeconds 60
```

Desactivar:

```powershell
powershell -ExecutionPolicy Bypass -File .\CONFIGURAR_RECORDATORIO_IDLE_AHOOTSA.ps1 -Disable
```

Nota: es un recordatorio sencillo desde el wrapper. La app oficial no expone todos los eventos de micrófono al wrapper, por lo que no es un detector perfecto de silencio.

## Bailes y actividades del panel

Herramientas nuevas:

```text
list_panel_dances_activities
play_panel_dance_activity
```

Ejemplos:

```text
haz un baile
baile dos
saluda con movimiento
haz algo eléctrico
```

Diagnóstico:

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_BAILES_PANEL_AHOOTSA.ps1
```
