# Ahootsa 5.0.9 - instalacion completa sobre conversation app

`ask_ollama` no es el cerebro principal. Vuelve a ser una actividad opcional para probar IA local, porque era lento.

La conversacion normal queda en `reachy_mini_conversation_app`, pero con perfil, instrucciones y herramientas Ahootsa instaladas completamente.

## Comandos

```powershell
cd D:\RITXI\5_0_9_ahootsa_instalacion_completa_conversation_app
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_SINTAXIS_PS1.ps1
powershell -ExecutionPolicy Bypass -File .\LIMPIAR_5_OLLAMA_COMO_CEREBRO.ps1
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_5_INSTALACION_COMPLETA_CONVERSATION_APP.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

## Esperado

```text
instructions modo 5.0.9 = True
ask_ollama actividad opcional = True
ask_ollama no cerebro = True
actividad directa = True
AHOOTSA_USE_OLLAMA_AS_BRAIN =
```
