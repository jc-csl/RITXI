# Ritxi v5.1 · Emociones oficiales Pollen + audio

Esta versión corrige el caso en el que al pulsar una emoción se escuchaba audio, pero Reachy Mini no se movía.

## Cambio principal

Las tarjetas de emociones principales usan ahora la librería oficial de movimientos grabados:

```text
pollen-robotics/reachy-mini-emotions-library
```

Cuando se pulsa una tarjeta marcada como emoción oficial, el backend intenta:

1. resolver el identificador del movimiento (`cheerful1`, `gasp1`, `hello1`, etc.);
2. si falla por cambio de nombre, probar variantes sin sufijo (`cheerful`, `gasp`, `hello`);
3. reproducir el audio `.wav` del movimiento si está disponible;
4. enviar `robot.play_move(move)` al daemon de Reachy;
5. si la librería o el ID fallan, usar un movimiento interno de fallback para que Ritxi no quede estático.

## Tarjetas oficiales añadidas

En la sección **Emociones Pollen Robotics** aparecen, entre otras:

- Despertar / reset postura (`wake_up`)
- Amor / alegría (`cheerful1`)
- Sorpresa (`gasp1`)
- Saludo / hola (`hello1`)
- Asombrado (`amazed1`)
- Aburrido / pensar (`boredom1`)
- Sí / OK (`yes1`)
- No / rechazo (`no1`)
- Triste (`sad1`)
- Asco / ansiedad (`anxiety1`)
- Enojado (`angry1`)
- Dormido (`sleepy1`)

## Diagnóstico

Nuevo endpoint:

```text
GET /api/robot/recorded_moves
```

Devuelve si la librería se ha cargado, cuántos movimientos detecta y cualquier error de carga.

## Orden correcto de ejecución

Terminal 1:

```powershell
scripts\run_reachy_sim_daemon.bat
```

Esperar a:

```text
Uvicorn running on http://127.0.0.1:8000
```

Terminal 2:

```powershell
scripts\run_v5_professional_panel_windows.bat
```

Abrir:

```text
http://127.0.0.1:8080
```

## Nota sobre el audio

Las emociones oficiales reproducen el audio asociado al movimiento mediante el backend, usando `pygame` cuando existe `move.audio_path`. En esas tarjetas no se fuerza TTS de navegador para evitar doble audio.

Las tarjetas tutor o acciones propias de Ritxi pueden seguir usando TTS de navegador o TTS backend, según los checkboxes activos.
