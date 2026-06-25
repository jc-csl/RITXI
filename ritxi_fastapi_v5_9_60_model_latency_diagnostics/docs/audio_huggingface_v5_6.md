# Ritxi v5.6 — audio oficial de Hugging Face en emociones

## Problema corregido

En versiones anteriores, el backend intentaba reproducir el `.wav` oficial con `pygame`. En Windows esto puede fallar por dispositivo de audio, inicialización del mezclador o ejecución dentro de FastAPI. Cuando fallaba, la interfaz usaba TTS conversacional como fallback, pero ese sonido no era el sonido expresivo oficial de la emoción.

## Solución v5.6

Las emociones oficiales usan ahora este flujo:

```text
clic en tarjeta oficial
        ↓
frontend pide /api/audio/recorded/{emotion_id}
        ↓
backend localiza o descarga {emotion_id}.wav desde pollen-robotics/reachy-mini-emotions-library
        ↓
navegador reproduce el WAV oficial por los altavoces del PC
        ↓
en paralelo FastAPI ejecuta robot.play_move(move) con RecordedMoves
```

El backend mantiene `robot.play_move(move)` para el movimiento, pero el audio oficial se reproduce desde el navegador. Esto es más fiable para Windows y evita mezclar el sonido expresivo de Hugging Face con la voz conversacional de Ritxi.

## Endpoints nuevos

```text
GET /api/audio/recorded/{emotion_id}
```

Devuelve el `.wav` oficial como `audio/wav`.

Ejemplos:

```text
http://127.0.0.1:8080/api/audio/recorded/cheerful1
http://127.0.0.1:8080/api/audio/recorded/dance1
http://127.0.0.1:8080/api/audio/recorded/amazed1
```

## Configuración importante

En `ejecutar_windows.cmd` se deja:

```cmd
set RITXI_PLAY_RECORDED_AUDIO_DEFAULT=false
```

Esto evita doble audio. El audio oficial se reproduce en el navegador; el backend no intenta reproducirlo con `pygame`.

## Diagnóstico

En logs deberías ver eventos como:

```text
recorded_audio_path_downloaded
WAV oficial Hugging Face
recorded_move_played
```

Si no suena, comprueba:

1. Que `Audio salida` esté activado.
2. Que el navegador permita reproducir audio.
3. Que exista conexión a Hugging Face la primera vez que se descarga el audio.
4. Que el endpoint `/api/audio/recorded/cheerful1` devuelva un archivo WAV.
