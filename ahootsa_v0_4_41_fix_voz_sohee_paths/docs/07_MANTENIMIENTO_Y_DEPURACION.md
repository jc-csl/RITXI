# 07 — Mantenimiento y depuración

## Si Ahootsa saluda en inglés

Causa probable:

```text
Reachy Mini Desktop está usando primero el perfil original/default.
```

Solución:

```powershell
powershell -ExecutionPolicy Bypass -File .\FORZAR_INICIO_CASTELLANO_SOHEE.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_INICIO_AHOOTSA.ps1
```

## Si la voz no es Sohee

```powershell
powershell -ExecutionPolicy Bypass -File .\CAMBIAR_VOZ_AHOOTSA.ps1 -Voice Sohee
powershell -ExecutionPolicy Bypass -File .\test\VER_VOZ_AHOOTSA.ps1
```

## Si no abre `http://localhost:7870/`

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_MEMORY_START_SERVER.ps1
powershell -ExecutionPolicy Bypass -File .\test\PROBAR_MEMORY_START_SERVER.ps1
```

## Si el juego Memory no cambia de tema

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_JUEGOS_PAREJAS_JSON.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_JUEGOS_PAREJAS_JSON.ps1
```

## Si Ollama no responde

```powershell
powershell -ExecutionPolicy Bypass -File .\RECREAR_MODELO_OLLAMA_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_ASK_OLLAMA.ps1
```

## Si cámara PC no funciona

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_CAMARA_PC.ps1
powershell -ExecutionPolicy Bypass -File .\test\PROBAR_CAMARA_PC.ps1
```

## Si las emociones no tienen audio

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AUDIO_EMOCIONES_PYGAME.ps1
powershell -ExecutionPolicy Bypass -File .\test\PROBAR_AUDIO_EMOCION_PYGAME.ps1
```

## Qué no tocar normalmente

```text
- Código original de Reachy Mini.
- Librerías instaladas en apps_venv.
- Carpetas internas generadas automáticamente por Python.
```

## Qué sí se puede editar

```text
profiles/ahootsa_realtime_es/instructions.txt
profiles/ahootsa_realtime_es/greeting.txt
profiles/ahootsa_realtime_es/voice.txt
profiles/ahootsa_realtime_es/*.json
```
