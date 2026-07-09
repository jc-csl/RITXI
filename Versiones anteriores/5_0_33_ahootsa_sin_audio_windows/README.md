# Ahootsa 5.0.33 — sin audio Windows

Versión correctiva acumulada para Ahootsa sobre la carpeta original:

```text
D:\RITXI\5_0_25_ahootsa_logs_simples_actividades_recuperadas
```

## Cambio principal

Elimina la voz Windows/navegador en el juego de parejas y en cualquier otra actividad.

La regla queda así:

```text
Solo habla Ahootsa.
No habla Windows, navegador, pyttsx3 ni SAPI.
```

## Ejecutar

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_0_33_AHOOTSA_MUJOCO_WEB.ps1
```

Si falta MuJoCo:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_0_33_AHOOTSA_MUJOCO_WEB.ps1 -InstallMujoco
```

## Comprobar que pyttsx3/SAPI queda mudo

```powershell
powershell -ExecutionPolicy Bypass -File .\3_COMPROBAR_AUDIO_WINDOWS_5_0_33.ps1
```

Si al ejecutar esa prueba suena una voz Windows, pásame la salida completa.

## Correcciones acumuladas

- 5.0.27: endpoints `/status`, `/mic`, `/voices/current`, `/voices`.
- 5.0.28/31/32: logs más robustos, timestamp por ejecución y reparación de `param(...)`.
- 5.0.33: bloqueo reforzado de audio Windows/navegador y TTS Python local.

## Nota

Después de aplicar el parche, cierra y vuelve a abrir Desktop Control para limpiar la caché del frontend.
