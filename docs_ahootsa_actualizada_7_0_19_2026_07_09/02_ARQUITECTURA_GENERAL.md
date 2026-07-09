# 02 — Arquitectura general

## 1. Vista por capas

```text
Usuario
  ↓
Navegador / panel Ahootsa / interfaz oficial
  ↓
App activa: ahootsa_realtime_ollama_app
  ↓
Ahootsa: perfiles externos + tools externas + panel HTML propio
  ↓
reachy_mini_conversation_app: núcleo conversacional oficial
  ↓
Hugging Face Realtime + herramientas del robot
  ↓
reachy-mini-daemon.exe
  ↓
Reachy Mini real o simulación MuJoCo
```

Ahootsa añade:

```text
- panel /ahootsa;
- endpoints /memory/*;
- endpoints /camera_pc/*;
- endpoints /config/*;
- endpoints /ahootsa/resolve_activity, /ahootsa/list_activities y /ahootsa/play_activity;
- tools externas para Ollama, Memory, cámara PC, actividades, bailes y diagnóstico.
```

## 2. Componentes principales

```text
Reachy Mini Control
  ├─ apps_venv
  ├─ reachy-mini-daemon.exe
  └─ sistema de apps registradas

App oficial reachy_mini_conversation_app
  ├─ bucle realtime
  ├─ Hugging Face Realtime
  ├─ interfaz web oficial
  ├─ herramientas core
  └─ sistema de perfiles/tools

Ahootsa
  ├─ app registrada: ahootsa_realtime_ollama_app
  ├─ perfiles externos: ahootsa7_realtime_es, etc.
  ├─ tools externas
  ├─ panel /ahootsa
  ├─ juego Memory integrado
  ├─ cámara PC
  ├─ Ollama auxiliar
  ├─ gestión de bailes/emociones en español
  └─ logs en D:\RITXI\logs
```

## 3. Principio de extensión

Ahootsa no debe modificar el núcleo oficial salvo configuración externa controlada. La solución correcta es:

```text
REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY = ...\ahootsa_realtime_ollama_desktop_app\profiles
REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY    = ...\ahootsa_realtime_ollama_desktop_app\tools
```

Esto permite que la app oficial cargue perfiles y herramientas propias sin copiar archivos dentro de `reachy_mini_conversation_app`.

## 4. Separación de cámaras

```text
Cámara oficial Reachy/MuJoCo
  → media.get_frame()
  → entorno 3D o cámara del robot
  → puede ver suelo virtual de MuJoCo

Cámara PC Ahootsa
  → navegador/getUserMedia o OpenCV
  → webcam del ordenador
  → fotos en D:\RITXI\fotos
```

La herramienta de análisis de imagen de Ahootsa debe usar la cámara PC cuando se pida analizar una foto real del usuario/entorno.

## 5. Separación de IA

```text
Hugging Face Realtime
  → conversación por voz principal
  → selección de herramientas
  → interacción natural con Reachy

Ollama
  → consulta local auxiliar
  → panel o herramienta ask_ollama
  → no sustituye al motor de voz principal
```
