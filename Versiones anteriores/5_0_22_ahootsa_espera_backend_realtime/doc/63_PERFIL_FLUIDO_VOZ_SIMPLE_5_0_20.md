# Ahootsa 5.0.20 - perfil fluido y voz simple

## Motivo

La voz Sohee ya queda correcta:

```text
length=5
has_bom=False
value=[Sohee]
API voices/current={"voice":"Sohee"}
```

Por eso se eliminan los bucles innecesarios de watcher de voz.

## Cambios principales

1. Perfil conversacional simplificado.
   - `instructions.txt` pasa de muchas reglas repetidas a un perfil corto.
   - Prioridad: responder rápido, natural y claro.
   - Conversación normal = respuesta directa, sin herramientas.

2. Voz simple.
   - Se mantiene Sohee sin BOM.
   - Se aplica una vez por API si la app está lista.
   - El watcher de voz queda desactivado.

3. Diagnóstico de conversación.
   - `DIAGNOSTICAR_5_CONVERSACION_FLUIDA.ps1`
   - `REINICIAR_5_SESION_CONVERSACION.ps1`

4. Documentación obligatoria:
   - `docs/ARQUITECTURA_FUNCIONALIDAD.md`

## Comandos

```powershell
cd D:\RITXI\5_0_20_ahootsa_perfil_fluido_voz_simple
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_SINTAXIS_PS1.ps1
powershell -ExecutionPolicy Bypass -File .\COMPROBAR_5_LOGS_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\LIMPIAR_5_VOZ_SOHEE_SIN_BOM.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_5_VOZ_SIN_BOM.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

Si escucha pero deja de contestar:

```powershell
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_5_CONVERSACION_FLUIDA.ps1
powershell -ExecutionPolicy Bypass -File .\REINICIAR_5_SESION_CONVERSACION.ps1
```
