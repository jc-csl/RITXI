# 01 — Instalación y arranque

## Instalación completa

Cerrar Reachy Mini Desktop antes de instalar.

```powershell
cd D:\RITXI\ahootsa_v0_4_36_docs_limpieza_tests
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```

## Reparación rápida del inicio en castellano y voz Sohee

```powershell
powershell -ExecutionPolicy Bypass -File .\FORZAR_INICIO_CASTELLANO_SOHEE.ps1
```

## Reparación del juego Memory

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_MEMORY_START_SERVER.ps1
```

## Tests principales

Los tests están en la carpeta `test`.

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_INICIO_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\test\VER_VOZ_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\test\PROBAR_MEMORY_START_SERVER.ps1
```

## Resultado esperado al iniciar

Ahootsa debe saludar en castellano, no con el saludo original inglés de Reachy Mini.

```text
¡Hola! Soy Ahootsa. Estoy lista para ayudarte. ¿Qué quieres hacer?
```

## Nota importante

Si el saludo sigue saliendo en inglés, normalmente significa que Reachy Mini Desktop está arrancando el perfil original/default antes que el perfil `ahootsa_realtime_es`. Ejecutar:

```powershell
powershell -ExecutionPolicy Bypass -File .\FORZAR_INICIO_CASTELLANO_SOHEE.ps1
```


## Si arranca como Reachy Mini y no como Ahootsa

```powershell
powershell -ExecutionPolicy Bypass -File .\FORZAR_PERFIL_AHOOTSA_TOTAL.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_PERFIL_AHOOTSA_TOTAL.ps1
```
