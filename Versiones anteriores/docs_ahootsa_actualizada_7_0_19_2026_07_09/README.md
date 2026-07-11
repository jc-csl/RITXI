# Docs Ahootsa actualizadas

**Versión documental:** 7.0.19 — 2026-07-09  
**Estado:** documentación consolidada después de las pruebas de la serie 7.0.0–7.0.19.

Esta carpeta documenta la arquitectura actual de Ahootsa, su instalación, perfiles, herramientas, panel web, juego de parejas, cámara PC, bailes/emociones, logs y diagnóstico.

La versión de referencia actual es:

```text
7_0_19_ahootsa_base_endpoint_alias_voz_fix
```

La app activa registrada en Reachy Mini Control es:

```text
ahootsa_realtime_ollama_app
```

Principios actuales:

```text
- Ahootsa no sustituye la app oficial; la extiende.
- El motor conversacional principal sigue siendo Hugging Face Realtime.
- Ollama es una IA local auxiliar, no el cerebro principal por voz.
- La cámara oficial de Reachy/MuJoCo y la cámara PC deben estar separadas.
- Los ZIP de versión no deben incluir docs, logs ni fotos.
- Logs:  D:\RITXI\logs
- Fotos: D:\RITXI\fotos
- Docs:  carpeta externa, actualizada aparte.
```

Lectura rápida:

```text
00_INDICE_Y_LECTURA_RAPIDA.md
01_INSTALACION_EQUIPO_NUEVO.md
02_ARQUITECTURA_GENERAL.md
07_HERRAMIENTAS_ACTIVIDADES_MEMORY_CAMARA_AUDIO.md
08_LOGS_DIAGNOSTICO_Y_DEPURACION.md
11_ESTADO_ACTUAL_7_0_19_Y_PRUEBAS.md
```
