# Ahootsa 5.0.17 - Sohee aplicada despues de crear la sesion del navegador

## Problema

La interfaz podia mostrar `Sohee`, pero la voz real salia como `Aiden` hasta pulsar manualmente Aplicar.

Esto indica que el valor de configuracion ya estaba en Sohee, pero la sesion realtime activa seguia con la voz anterior. Por eso al pulsar Aplicar manualmente se corregia.

## Cambio 5.0.17

El lanzador ya no abre `http://127.0.0.1:7860` antes de aplicar voz.

Nuevo flujo:

```text
1. Arranca daemon.
2. Arranca app Ahootsa.
3. Espera /status y /voices/current.
4. Aplica Sohee PRE-navegador.
5. Abre navegador.
6. Espera unos segundos para que se cree la sesion realtime.
7. Aplica Sohee POST-navegador varias veces.
8. Confirma voices/current.
```

## Comandos

```powershell
cd D:\RITXI\5_0_17_ahootsa_voz_sohee_post_browser_session
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_SINTAXIS_PS1.ps1
powershell -ExecutionPolicy Bypass -File .\VALIDAR_5_SCRIPT_DAEMON_GENERADO.ps1
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_LOGS_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

Si alguna vez vuelve a sonar Aiden:

```powershell
powershell -ExecutionPolicy Bypass -File .\VALIDAR_5_VOZ_SESION_SOHEE.ps1
```
