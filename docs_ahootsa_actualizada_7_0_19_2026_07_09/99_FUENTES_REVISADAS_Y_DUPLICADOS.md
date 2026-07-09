# 99 — Fuentes revisadas, duplicados eliminados y criterios de organización

## 1. Fuentes integradas

Se revisó la carpeta documental anterior:

```text
docs_ahootsa_organizada_2026_07_09
```

Incluía:

```text
00_INDICE_Y_LECTURA_RAPIDA.md
01_INSTALACION_EQUIPO_NUEVO.md
02_ARQUITECTURA_GENERAL.md
03_APP_OFICIAL_REACHY_Y_AHOOTSA.md
04_MODELO_CONVERSACIONAL_HUGGINGFACE_Y_OLLAMA.md
05_FLUJOS_COMUNICACION_Y_PUERTOS.md
06_CONFIGURACION_PERFILES_VARIABLES.md
07_HERRAMIENTAS_ACTIVIDADES_MEMORY_CAMARA_AUDIO.md
08_LOGS_DIAGNOSTICO_Y_DEPURACION.md
09_MODIFICAR_CODIGO_Y_MANTENIMIENTO.md
10_VERSIONES_LIMPIEZA_Y_MIGRACION.md
99_FUENTES_REVISADAS_Y_DUPLICADOS.md
AHOOTSA_ANALISIS_OFICIAL_Y_5_0_25_INSTALACION_NUEVO_EQUIPO.md
assets/Reachy mini datasheet.pdf
README.md
```

## 2. Duplicado histórico integrado

El documento:

```text
AHOOTSA_ANALISIS_OFICIAL_Y_5_0_25_INSTALACION_NUEVO_EQUIPO.md
```

se mantiene como fuente histórica, pero su contenido relevante se ha integrado en:

```text
03_APP_OFICIAL_REACHY_Y_AHOOTSA.md
04_MODELO_CONVERSACIONAL_HUGGINGFACE_Y_OLLAMA.md
10_VERSIONES_LIMPIEZA_Y_MIGRACION.md
```

No se conserva como archivo independiente en esta carpeta actualizada para evitar duplicidad y confusión con la serie 7.

## 3. Criterios de actualización a 7.0.19

Se incorporó lo aprendido en pruebas posteriores a 7.0.10:

```text
- separación definitiva de play_emotion del perfil frente a tools/play_emotion.py;
- resolución de bailes/emociones con nombres españoles y alias play/olay;
- validación de dance1/dance2/dance3 y emociones con json/ogg;
- endpoint /ahootsa/resolve_activity y pruebas desde panel;
- diagnóstico directo 7.0.19;
- traza de voz para diferenciar fallo de herramienta frente a fallo de selección por HF;
- Memory integrado en 7860;
- logs con timestamp;
- problema pendiente de logs con NUL;
- 404 iniciales interpretados como sondeo prematuro si luego pasan a 200 OK.
```

## 4. Regla de documentación

La documentación se actualiza aparte del ZIP de aplicación.

Los ZIP de versión Ahootsa no deben contener:

```text
docs
logs
fotos
```

La documentación se entrega como ZIP propio:

```text
docs_ahootsa_actualizada_7_0_19_2026_07_09.zip
```
