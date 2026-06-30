# 06 — Tests y diagnóstico

Los scripts de prueba están en:

```text
test/
```

Scripts actuales:

- `DIAGNOSTICAR_ASK_OLLAMA.ps1`
- `DIAGNOSTICAR_EMOCIONES_AUDIO.ps1`
- `DIAGNOSTICAR_INICIO_AHOOTSA.ps1`
- `DIAGNOSTICAR_JUEGOS_PAREJAS_JSON.ps1`
- `DIAGNOSTICAR_JUEGO_PAREJAS_ANIMALES.ps1`
- `PROBAR_AUDIO_EMOCION_PYGAME.ps1`
- `PROBAR_CAMARA_PC.ps1`
- `PROBAR_JUEGOS_PAREJAS_JSON.ps1`
- `PROBAR_JUEGO_PAREJAS_ANIMALES.ps1`
- `PROBAR_MEMORY_MODULO_DIRECTO.ps1`
- `PROBAR_MEMORY_START_SERVER.ps1`
- `VER_VOZ_AHOOTSA.ps1`

## Tests recomendados después de instalar

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_INICIO_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\test\VER_VOZ_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\test\PROBAR_MEMORY_MODULO_DIRECTO.ps1
powershell -ExecutionPolicy Bypass -File .\test\PROBAR_MEMORY_START_SERVER.ps1
```

## Test del juego Memory

```powershell
powershell -ExecutionPolicy Bypass -File .\test\PROBAR_MEMORY_START_SERVER.ps1
```

Resultado esperado:

```text
http://localhost:7870/
```

Debe abrirse con cartas azules y números blancos.

## Test de Ollama

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_ASK_OLLAMA.ps1
```

Comprueba:

```text
- Ollama instalado;
- API local activa;
- modelo ahootsa-local:latest;
- herramienta ask_ollama.
```

## Test de voz

```powershell
powershell -ExecutionPolicy Bypass -File .\test\VER_VOZ_AHOOTSA.ps1
```

Debe mostrar `Sohee` en los perfiles instalados.

## Test de inicio

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_INICIO_AHOOTSA.ps1
```

Comprueba:

```text
- voice.txt;
- greeting.txt;
- instructions.txt;
- variables de entorno relevantes.
```

## Cámara PC en simulación

```powershell
powershell -ExecutionPolicy Bypass -File .\test\PROBAR_CAMARA_PC.ps1
```

## Emociones/audio

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_EMOCIONES_AUDIO.ps1
powershell -ExecutionPolicy Bypass -File .\test\PROBAR_AUDIO_EMOCION_PYGAME.ps1
```


## Test específico de audio de emociones

```powershell
powershell -ExecutionPolicy Bypass -File .\test\PROBAR_AUDIO_EMOCION_HERRAMIENTA.ps1
```


## Diagnóstico de perfil Ahootsa total

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_PERFIL_AHOOTSA_TOTAL.ps1
```


## Voz Sohee

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_VOZ_SOHEE_TOTAL.ps1
```

## Bailes panel

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_BAILES_PANEL_AHOOTSA.ps1
```


## Memory reacción única

```powershell
powershell -ExecutionPolicy Bypass -File .\test\PROBAR_MEMORY_REACCION_UNICA.ps1
```


## Memory sin bloqueo de audio

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_MEMORY_NO_BLOQUEO.ps1
```
