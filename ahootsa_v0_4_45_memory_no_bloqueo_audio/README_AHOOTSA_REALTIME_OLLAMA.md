# Ahootsa Realtime Ollama — v0.4.45

Corrección del bloqueo del juego Memory y del audio.

## Reparación directa

Con Reachy Mini Desktop cerrado:

```powershell
cd D:\RITXI\ahootsa_v0_4_45_memory_no_bloqueo_audio
powershell -ExecutionPolicy Bypass -File .\REPARAR_MEMORY_ESTABLE_SIN_BLOQUEO.ps1
```

## Instalación completa

```powershell
cd D:\RITXI\ahootsa_v0_4_45_memory_no_bloqueo_audio
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_MEMORY_NO_BLOQUEO.ps1
```

Debe salir:

```text
sin await emotion = True
sin play_emotion interno = True
visual_only_no_blocking_audio = True
```

## Cambio importante

Dentro del juego Memory ya no se lanza movimiento/audio interno.  
Esto evita que la escucha del micrófono se quede bloqueada.

Las emociones y bailes siguen funcionando fuera del juego.
