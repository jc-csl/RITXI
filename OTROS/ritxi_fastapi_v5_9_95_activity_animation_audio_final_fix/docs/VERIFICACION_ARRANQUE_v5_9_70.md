# Verificación de arranque v5.9.70

## Problema detectado en logs

`ReferenceError: safeBotText is not defined`.

## Corrección

- `safeBotText()` se declara globalmente.
- `sendTurn()` usa llamada protegida.
- `selfCheckConversationAndCards()` comprueba funciones críticas al arrancar.
- La versión completa aparece en la interfaz como `v5.9.70`.

## Checks

```json
{
  "version": "5.9.70",
  "safe_exists_before": false,
  "safeBotText_function_exists": true,
  "chatFlagsForBackend_function_exists": true,
  "payloadFlags_const_count": 1,
  "payloadFlags_defined_before_first_use": true,
  "safeBotText_protected_call": true,
  "selfcheck_includes_safeBotText": true,
  "version_badge_present": true,
  "node_ok": true,
  "compile_ok": true,
  "log_summary": [
    {
      "file": "session_20260625_101409_pid2356.log",
      "size": 15362,
      "hits": [
        "safeBotText",
        "ReferenceError",
        "Usuario:"
      ],
      "tail": ": \"qwen3:0.6b\", \"first_token_ms\": null, \"total_ms\": 8290.029299998423, \"content_len\": 0, \"content_preview\": \"\", \"warnings\": []}\n2026-06-25 10:14:44,892 | INFO     | ritxi.event | emotion_parsed | {\"session_id\": \"demo\", \"emotion\": \"escucha_activa\", \"clean_text_len\": 97, \"clean_text_preview\": \"Claro. Podemos practicar cómo pedir ayuda. Una frase sencilla es: “Por favor, ¿me puedes ayudar?”\"}\n2026-06-25 10:14:45,782 | INFO     | app.audio.echo_guard | EchoGuard: micro ON (turn-complete)\n2026-06-25 10:14:45,784 | INFO     | ritxi.event | micro_on | {\"reason\": \"turn-complete\"}\n2026-06-25 10:14:45,784 | INFO     | ritxi.event | turn_end | {\"session_id\": \"demo\", \"response_len\": 97, \"emotion\": \"escucha_activa\", \"action_ids\": [], \"latencies\": {\"stt_ms\": 0.0, \"llm_first_token_ms\": null, \"llm_total_ms\": 8290.029299998423, \"tts_first_enqueue_ms\": null, \"output_total_ms\": 907.2816999978386, \"turn_total_ms\": 9197.350900001766}, \"warnings\": [], \"microphone_enabled\": true, \"state\": \"idle\"}\n2026-06-25 10:14:45,792 | INFO     | ritxi.event | client_log | {\"level\": \"error\", \"message\": \"[chat] Error en turno: ReferenceError: safeBotText is not defined\", \"data\": {\"model\": \"qwen3:0.6b\"}}\n2026-06-25 10:14:45,796 | INFO     | ritxi.event | client_log | {\"level\": \"debug\", \"message\": \"[chat] Turno cliente completado en 9240 ms\", \"data\": {}}\n2026-06-25 10:14:46,053 | INFO     | ritxi.event | client_log | {\"level\": \"debug\", \"message\": \"[ui] Entrada de texto habilitada: sendTextNow-finally\", \"data\": {}}\n"
    },
    {
      "file": "session_20260625_101409_pid2356.jsonl",
      "size": 13322,
      "hits": [
        "safeBotText",
        "ReferenceError",
        "Usuario:"
      ],
      "tail": "_ms\": 8290.03, \"first_token_ms\": null}\n{\"ts\": \"2026-06-25T10:14:44.889\", \"event\": \"llm_end\", \"session_id\": \"demo\", \"provider\": \"ollama\", \"model\": \"qwen3:0.6b\", \"first_token_ms\": null, \"total_ms\": 8290.029299998423, \"content_len\": 0, \"content_preview\": \"\", \"warnings\": []}\n{\"ts\": \"2026-06-25T10:14:44.891\", \"event\": \"emotion_parsed\", \"session_id\": \"demo\", \"emotion\": \"escucha_activa\", \"clean_text_len\": 97, \"clean_text_preview\": \"Claro. Podemos practicar cómo pedir ayuda. Una frase sencilla es: “Por favor, ¿me puedes ayudar?”\"}\n{\"ts\": \"2026-06-25T10:14:45.784\", \"event\": \"micro_on\", \"reason\": \"turn-complete\"}\n{\"ts\": \"2026-06-25T10:14:45.784\", \"event\": \"turn_end\", \"session_id\": \"demo\", \"response_len\": 97, \"emotion\": \"escucha_activa\", \"action_ids\": [], \"latencies\": {\"stt_ms\": 0.0, \"llm_first_token_ms\": null, \"llm_total_ms\": 8290.029299998423, \"tts_first_enqueue_ms\": null, \"output_total_ms\": 907.2816999978386, \"turn_total_ms\": 9197.350900001766}, \"warnings\": [], \"microphone_enabled\": true, \"state\": \"idle\"}\n{\"ts\": \"2026-06-25T10:14:45.792\", \"event\": \"client_log\", \"level\": \"error\", \"message\": \"[chat] Error en turno: ReferenceError: safeBotText is not defined\", \"data\": {\"model\": \"qwen3:0.6b\"}}\n{\"ts\": \"2026-06-25T10:14:45.796\", \"event\": \"client_log\", \"level\": \"debug\", \"message\": \"[chat] Turno cliente completado en 9240 ms\", \"data\": {}}\n{\"ts\": \"2026-06-25T10:14:46.052\", \"event\": \"client_log\", \"level\": \"debug\", \"message\": \"[ui] Entrada de texto habilitada: sendTextNow-finally\", \"data\": {}}\n"
    },
    {
      "file": "lanzador_20260625_101407.log",
      "size": 682,
      "hits": [],
      "tail": "﻿[2026-06-25 10:14:08] Lanzador iniciado desde D:\\RITXI\\ritxi_fastapi_v5_9_69_chat_modes_full_fix\n[2026-06-25 10:14:08] [OK] Daemon Reachy disponible en 127.0.0.1:8000\n[2026-06-25 10:14:08] [Ritxi] Arrancando FastAPI con entorno correcto: reachy_daemon + ollama + browser TTS\n[2026-06-25 10:14:08] [Ritxi] FastAPI PID: 5212\n[2026-06-25 10:14:08] [Ritxi] Esperando hasta 90 segundos a 127.0.0.1:8080...\n[2026-06-25 10:14:16] esperando FastAPI... 5/90 s\n[2026-06-25 10:14:17] [OK] FastAPI disponible en http://127.0.0.1:8080\n[2026-06-25 10:14:17] [Ritxi] Esperando 10 segundos antes de abrir navegador...\n[2026-06-25 10:14:28] [OK] Navegador abierto: http://127.0.0.1:8080\n"
    }
  ]
}
```
