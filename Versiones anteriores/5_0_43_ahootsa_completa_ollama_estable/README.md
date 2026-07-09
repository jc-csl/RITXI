# Ahootsa 5.0.43 completa autónoma estable

Versión completa para usar como única carpeta de trabajo. No copia desde `5_0_25`, `5_0_35`, `5_0_42` ni otras carpetas antiguas.

Sí necesita que esté instalado Reachy Mini Control/Desktop Control, porque usa su entorno:

```text
%LOCALAPPDATA%\Reachy Mini Control\apps_venv
```

## Ejecutar con Ollama

```powershell
cd D:\RITXI\5_0_43_ahootsa_completa_ollama_estable
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_43.ps1 -Provider ollama -OllamaModel llama3.2:3b
```

O doble clic / CMD:

```cmd
LANZAR_AHOOTSA_OLLAMA_5_0_43.cmd
```

## Instalar/actualizar sin lanzar

```powershell
powershell -ExecutionPolicy Bypass -File .\0_INSTALAR_O_ACTUALIZAR_AHOOTSA_5_0_43.ps1
```

## Comprobar IA local y cámara

```powershell
powershell -ExecutionPolicy Bypass -File .\1_COMPROBAR_IA_CAMARA_5_0_43.ps1
```

La cámara PC se prueba en:

```text
http://127.0.0.1:7860/camera/page
```

## Qué mejora frente a 5.0.42

- Usa `llama3.2:3b` por defecto.
- Comprueba `ollama list`, `/api/tags` y `/api/generate` antes de arrancar.
- Si el modelo configurado no existe, intenta usar `llama3.2:3b` u otro modelo disponible.
- Añade alias para que distintos botones antiguos de “Preguntar IA local” funcionen:
  - `/ollama/ask`
  - `/ask_ollama`
  - `/api/ask_ollama`
  - `/api/ollama/ask`
  - `/local-ai/ask`
  - `/llm/ask`
  - `/ask`
  - `/chat`
- Mantiene cámara PC, logs por ejecución, bloqueo de voz Windows y beeps.

## Modelos locales

En tu equipo ya aparecen:

```text
nomic-embed-text:latest
llama3.2:3b
```

Para conversación usa `llama3.2:3b`. `nomic-embed-text` es de embeddings, no sirve como chat conversacional principal.
