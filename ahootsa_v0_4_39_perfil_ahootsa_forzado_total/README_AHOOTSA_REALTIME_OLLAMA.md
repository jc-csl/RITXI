# Ahootsa Realtime Ollama — v0.4.39

Versión para corregir el problema de perfil.

## Problema corregido

Si la app dice que es Reachy Mini y no conoce el juego de parejas, está cargando el perfil oficial `default` en lugar de `ahootsa_realtime_es`.

## Solución

Ejecutar con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\FORZAR_PERFIL_AHOOTSA_TOTAL.ps1
```

Diagnóstico:

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_PERFIL_AHOOTSA_TOTAL.ps1
```

## Instalación completa

```powershell
cd D:\RITXI\ahootsa_v0_4_39_perfil_ahootsa_forzado_total
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```

## Resultado esperado

```text
¡Hola! Soy Ahootsa. Estoy lista para ayudarte. ¿Qué quieres hacer?
```

Y debe conocer:

```text
juego de animales
juego de ciudades
juego de alimentos
```

## Documentación

```text
docs/11_PERFIL_AHOOTSA_FORZADO_TOTAL_v0_4_39.md
```
