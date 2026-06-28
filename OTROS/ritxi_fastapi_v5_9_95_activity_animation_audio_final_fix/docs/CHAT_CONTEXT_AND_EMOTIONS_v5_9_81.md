# Chat y emociones v5.9.81

## Fallo corregido

Los logs mostraban:

```text
ReferenceError: Cannot access 'id' before initialization
at fastActivityReply
```

Causa: `fastActivityReply()` usaba `id` antes de declararlo.

## Contexto de actividad pegado

El chat normal estaba usando `currentActivityContext` aunque el usuario ya no estuviera respondiendo una actividad. Eso hacía que conversaciones nuevas se trataran como actividad anterior.

Corrección:

```text
activitySource = isActivityTurnSource(source)
activeContextForTurn = activitySource ? contexto : null
```

Si no es actividad, se limpia el contexto anterior.

## Emociones oficiales

Se conserva:

```text
click emoción → audio oficial .ogg/.wav + animación robot
```

Independiente de modo:

```text
Texto + IA rápida
Texto + IA + Robot
Micro + IA
Completo
```

## Diagnóstico manual

En consola del navegador:

```js
await testOfficialEmotionRuntime('cheerful1')
```
