# Update 12.8 — Arranque completo y scripts operativos limpios

## Objetivo

Reducir los scripts visibles y disponer de un único arranque completo que:

1. cierre procesos anteriores;
2. libere los puertos 7860, 8100 y 8000;
3. arranque el servidor local;
4. arranque el daemon y MuJoCo;
5. abra el panel;
6. espere la preparación de una sesión identificada;
7. arranque la Conversation App;
8. compruebe el estado final.

El puerto correcto del servidor local es **8100**, no 81000.

## Scripts visibles en la raíz

```text
INICIAR_AHOOTSA.ps1
FINALIZAR_SESION_AHOOTSA.ps1
COMPROBAR_AHOOTSA.ps1
LIMPIAR_PROCESOS_AHOOTSA.ps1
```

## Scripts internos necesarios

```text
scripts/ahootsa_process_utils.ps1
scripts/iniciar_servidor_local.ps1
scripts/iniciar_daemon_mujoco.ps1
scripts/iniciar_conversation_app.ps1
```

Los scripts internos son utilizados por el arranque y por los botones del
panel. No deben ejecutarse normalmente de forma manual.

## Arranque identificado

```powershell
cd D:\RITXI\AHOOTSA8
.\INICIAR_AHOOTSA.ps1
```

El script abre el panel y espera hasta 20 minutos para preparar persona,
actividad y nivel. Cuando detecta la sesión, inicia la Conversation App con
`ahootsa_session`.

Si no se prepara ninguna sesión durante ese intervalo, inicia el modo anónimo
con `ahootsa`.

## Arranque anónimo inmediato

```powershell
.\INICIAR_AHOOTSA.ps1 -Anonimo
```

## Finalización

```powershell
.\FINALIZAR_SESION_AHOOTSA.ps1
```

Cierra la Conversation App, espera el cierre del log, finaliza la sesión y
genera PDF, HTML, JSON y transcripción.

Para detener también servidor y daemon:

```powershell
.\FINALIZAR_SESION_AHOOTSA.ps1 -DetenerTodo
```

## Limpieza

```powershell
.\LIMPIAR_PROCESOS_AHOOTSA.ps1
```

Solo cierra procesos y libera puertos. No borra usuarios, sesiones ni informes.

## Corrección del informe

Se elimina la llamada recursiva entre el panel y el generador. El informe usa
una ruta interna que finaliza el registro sin volver a lanzar otro informe.
