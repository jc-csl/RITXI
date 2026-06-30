# 15 — Memory reacción única v0.4.45

## Problema

El fallo del juego Memory podía reproducir dos veces:

```text
- movimiento;
- sonido de la emoción;
- reacción de fallo.
```

También daba sensación de versión antigua porque la secuencia no quedaba clara.

## Causa probable

La herramienta `choose_memory_cards` hacía una reacción, y después el modelo podía llamar otra vez a una herramienta de emoción por las instrucciones generales.

## Corrección

```text
- choose_memory_cards incluye una protección anti-duplicado de 8 segundos.
- Una jugada solo puede generar una reacción.
- El mensaje devuelto prohíbe llamar después a play_emotion, play_emotion_with_audio o dance.
- start_memory_pairs_game ya no lanza una emoción de saludo automática.
- Se espera 1,2 segundos tras girar cartas antes de reaccionar.
```

## Secuencia esperada

```text
Usuario: uno y tres
1. Se llama a choose_memory_cards.
2. Se giran las cartas.
3. Espera breve para verlas.
4. Si falla, una sola reacción con movimiento y sonido.
5. Las cartas quedan visibles 4 segundos.
```

## Reparación directa

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_MEMORY_REACCION_UNICA.ps1
```

## Test

```powershell
powershell -ExecutionPolicy Bypass -File .\test\PROBAR_MEMORY_REACCION_UNICA.ps1
```
