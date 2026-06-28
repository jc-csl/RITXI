# Emociones independientes del modo v5.9.79

## Regla

Las tarjetas de la pestaña de emociones oficiales son acciones directas.

No dependen de:

```text
Texto + IA rápida
Texto + IA + Robot
Micro + IA
Completo
```

## Ejecución

```text
click emoción
  → playOfficialRecordedAudio(... force=true)
  → /api/robot/action motion_enabled=true wait=true
```

## Si falla el WAV

No se usa TTS. Solo se ejecuta animación.

## Si falla robot

Se muestra aviso en estado y se registra en logs como `Animación oficial no ejecutada`.
