# Emociones oficiales WAV v5.9.77

## Regla

```text
Emoción oficial con WAV → reproducir WAV + animación
Emoción oficial sin WAV/fallo → solo animación
Nunca → decir "Ritxi reproduce..." con TTS
```

## Motivo

Las emociones oficiales Pollen/Reachy ya tienen su propio audio asociado. Si no está disponible, verbalizar una frase genérica resulta incorrecto y confuso.

## Funciones afectadas

```text
playOfficialRecordedAudio()
recordedEmotionNoTtsFallback()
executeAction()
```
