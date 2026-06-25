# Diagnóstico de micro en Ritxi v4.4

En el log `session_20260624_082616_pid2884` se observó:

- Reachy estaba conectado al inicio y llegó a ejecutar la emoción `pensando`.
- Chrome sí produjo una transcripción final, pero la frase reconocida no coincidía bien con lo hablado.
- Después apareció `Error micro PC: aborted` porque la propia app abortaba `SpeechRecognition` para enviar el turno.
- Ollama tardó hasta el timeout y se activó fallback mock.
- Más tarde se perdió la conexión con el daemon, por eso se saltaron movimientos posteriores.

La v4.4 cambia el enfoque: deja de depender del STT del navegador como modo recomendado. El nuevo modo graba WAV desde el navegador y lo envía a FastAPI para transcribir con Faster-Whisper local.

## Procedimiento recomendado

```powershell
scripts\setup_uv_windows.bat
scripts\setup_uv_stt_whisper_windows.bat
```

Después:

```powershell
scripts\run_reachy_sim_daemon.bat
scripts\run_v4_whisper_stt_tutor_windows.bat
```

En el panel selecciona: **STT local Whisper recomendado**.

## Qué mirar en el log

Eventos clave:

- `stt_audio_upload`: audio recibido por FastAPI.
- `stt_whisper_model_loading`: primera carga del modelo.
- `stt_whisper_result`: texto final y latencia STT.
- `llm_start` / `llm_end`: latencia del modelo.
- `tts_browser_delegate`: texto que debe hablar el navegador.
- `robot_pose_sent`: movimiento enviado a Reachy.
- `turn_end`: resumen completo del turno.
