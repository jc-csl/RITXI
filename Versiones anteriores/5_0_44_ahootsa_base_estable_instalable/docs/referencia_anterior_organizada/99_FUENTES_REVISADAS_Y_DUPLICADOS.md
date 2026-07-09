# 99 — Fuentes revisadas, duplicados eliminados y criterios de organización

## 1. Archivos revisados de la carpeta `docs`

```text
00_LEEME_DOCUMENTACION.md
01_INSTALACION_Y_ARRANQUE.md
02_ESTRUCTURA_DEL_PROGRAMA.md
03_FLUJOS_DE_DATOS.md
04_CONFIGURACION_IMPORTANTE.md
05_JUEGOS_MEMORY_Y_HERRAMIENTAS.md
06_TESTS_Y_DIAGNOSTICO.md
07_MANTENIMIENTO_Y_DEPURACION.md
08_CAMBIOS_VERSION_ACTUAL.md
AHOOTSA_ARQUITECTURA_CODIGO_COMPLETO_actualizado_5_0_33.md
ARQUITECTURA_FUNCIONALIDAD.md
manual_archivos_config.md
Reachy mini datasheet.pdf
INSTRUCCIONES.txt
```

## 2. Documento nuevo integrado

Se integró el documento:

```text
AHOOTSA_ANALISIS_OFICIAL_Y_5_0_25_INSTALACION_NUEVO_EQUIPO.md
```

Contenido integrado principalmente en:

```text
01_INSTALACION_EQUIPO_NUEVO.md
02_ARQUITECTURA_GENERAL.md
03_APP_OFICIAL_REACHY_Y_AHOOTSA.md
04_MODELO_CONVERSACIONAL_HUGGINGFACE_Y_OLLAMA.md
05_FLUJOS_COMUNICACION_Y_PUERTOS.md
```

## 3. Código fuente revisado para contrastar arquitectura

```text
reachy_mini_conversation_app-main.zip
5_0_25_ahootsa_logs_simples_actividades_recuperadas.zip
5_0_43_ahootsa_completa_ollama_estable.zip
```

Aspectos confirmados:

```text
- La app oficial usa backend Hugging Face.
- El modo por defecto es deployed.
- El proxy de sesión oficial es pollen-robotics-reachy-mini-realtime-url.hf.space/session.
- Ahootsa 5.0.25 llama internamente a reachy_mini_conversation_app.main.run().
- ask_ollama es una herramienta auxiliar, no el motor conversacional principal.
- La cámara oficial usa media.get_frame(), no la webcam del PC.
- El modelo Ollama histórico ahootsa-local:latest no existe en el equipo actual; el modelo disponible es llama3.2:3b.
```

## 4. Duplicados detectados

### Documento de arquitectura completo

Estos archivos tenían el mismo contenido hash:

```text
docs/AHOOTSA_ARQUITECTURA_CODIGO_COMPLETO_actualizado_5_0_33.md
/mnt/data/AHOOTSA_ARQUITECTURA_CODIGO_COMPLETO.md
/mnt/data/AHOOTSA_ARQUITECTURA_CODIGO_COMPLETO_actualizado_5_0_33.md
```

Se fusionaron en documentos temáticos y no se copió el duplicado.

### `INSTRUCCIONES.txt`

El archivo estaba vacío. No se conserva como documento activo.

### `ARQUITECTURA_FUNCIONALIDAD.md`

Documento de versión 5.0.26 centrado en endpoints de compatibilidad. Su contenido útil queda integrado en:

```text
05_FLUJOS_COMUNICACION_Y_PUERTOS.md
08_LOGS_DIAGNOSTICO_Y_DEPURACION.md
10_VERSIONES_LIMPIEZA_Y_MIGRACION.md
```

### Documentos v0.4.57

Los documentos cortos de v0.4.57 se han fusionado por tema:

```text
instalación       -> 01
estructura        -> 02
flujos            -> 05
configuración     -> 06
juegos/tools      -> 07
tests/diagnóstico -> 08
mantenimiento     -> 09
cambios/versiones -> 10
```

## 5. Criterio aplicado

```text
- Evitar un documento histórico por cada parche.
- Organizar por tema estable.
- Mantener rutas, variables y comandos concretos.
- Separar claramente app oficial, app Ahootsa, backend HF, Ollama auxiliar y cámara PC.
- Dejar una guía útil para instalación en equipo nuevo.
```

## 6. Archivos conservados como recurso externo

```text
assets/Reachy mini datasheet.pdf
```

## 7. Fecha de organización

```text
2026-07-09
```
