# 03 — App oficial Reachy Mini Conversation App y Ahootsa

## 1. Qué es la app oficial

`reachy_mini_conversation_app` es la app oficial de conversación para Reachy Mini. Aporta:

```text
- bucle de conversación realtime
- conexión Hugging Face Realtime
- herramientas oficiales del robot
- perfiles conversacionales
- personalidad
- memoria
- cámara oficial
- movimientos y emociones
- interfaz web
```

En su código, la configuración principal indica que el backend es Hugging Face:

```text
HF_BACKEND = "huggingface"
```

También avisa de que variables antiguas como `BACKEND_PROVIDER` y `MODEL_NAME` se ignoran en la app oficial actual.

## 2. Qué es Ahootsa

Ahootsa es una app propia registrada en Reachy Mini Control. En 5.0.25 su clase principal era:

```text
AhootsaRealtimeOllamaApp
```

Esta clase configuraba variables de entorno y después importaba la app oficial:

```python
from reachy_mini_conversation_app.main import run
```

y ejecutaba:

```python
run(
    args,
    robot=reachy_mini,
    app_stop_event=stop_event,
    settings_app=self.settings_app,
    instance_path=instance_path,
)
```

Esto significa que Ahootsa no reemplazaba todo el motor oficial: lo envolvía.

## 3. Qué hace Ahootsa antes de llamar a la app oficial

Ahootsa configura:

```text
REACHY_MINI_CUSTOM_PROFILE=ahootsa_realtime_es
REACHY_MINI_PROFILE=ahootsa_realtime_es
REACHY_MINI_PERSONALITY=ahootsa_realtime_es
AHOOTSA_NAME=Ahootsa
AHOOTSA_LANGUAGE=es
REALTIME_TRANSCRIPTION_LANGUAGE=es
AHOOTSA_GREETING=¡Hola! Soy Ahootsa...
VOICE=Sohee
AHOOTSA_VOICE=Sohee
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=...
```

Después refresca la configuración oficial:

```text
refresh_runtime_config_from_env()
```

y llama al `run()` oficial.

## 4. Consecuencia práctica

La app activa es Ahootsa, pero el bucle conversacional principal sigue siendo el de la app oficial.

```text
ahootsa_realtime_ollama_app
  ↓
configura perfil, voz, idioma, herramientas y variables
  ↓
reachy_mini_conversation_app.main.run()
  ↓
Hugging Face Realtime
```

## 5. Qué se debe modificar según el objetivo

```text
Cambiar conversación principal:
  revisar perfil Ahootsa, instructions.txt y configuración HF_REALTIME_*

Cambiar herramienta Ollama:
  modificar ask_ollama.py o endpoints /ollama/ask

Cambiar actividades:
  modificar herramientas Python del perfil Ahootsa

Cambiar movimiento:
  revisar tools oficiales y llamadas a Reachy/MuJoCo

Cambiar cámara PC:
  modificar módulo propio Ahootsa, no la herramienta oficial camera.py

Cambiar instalación:
  modificar scripts PowerShell y patch_ahootsa_*.py
```

## 6. La app oficial no se arranca por separado

Si el script llama a:

```text
/api/apps/start-app/ahootsa_realtime_ollama_app
```

entonces no se está arrancando como app activa:

```text
reachy_mini_conversation_app
```

Sin embargo, se usa su código internamente si Ahootsa importa y llama a `reachy_mini_conversation_app.main.run()`.

## 7. Riesgo de tener dos apps abiertas

No conviene arrancar simultáneamente:

```text
ahootsa_realtime_ollama_app
reachy_mini_conversation_app
```

porque pueden competir por:

```text
- puerto 7860
- audio
- backend realtime
- herramientas
- robot/MuJoCo
- cámara
```
