# Prueba 12.4 — Conversación automática y registro persistente

## Objetivo

Comprobar de forma determinista que `ahootsa_local_server` prepara una sesión,
registra turnos alternos, calcula métricas, finaliza la actividad y conserva la
conversación en SQLite.

## Alcance

Esta prueba no utiliza micrófono, reconocimiento de voz, Hugging Face, MuJoCo ni
robot físico. Los turnos se introducen por la API pública del servidor local.
Por tanto, valida el almacenamiento y la persistencia, no la captura de una
conversación hablada real.

## Guion y resultado esperado

- 9 eventos del guion;
- 3 respuestas de usuario;
- 3 respuestas correctas;
- 1 pista;
- 1 silencio;
- 1 actividad iniciada y completada;
- estado final `finished`.

## Archivos generados

```text
ahootsa_local_server/data/sessions/session_XXXXXX/
├── session_context.json
├── session_status.json
├── profile_snapshot/
├── summary.json
└── automatic_conversation_verification.json
```

Se crea también `data/last_automatic_conversation_test.json` para comprobar la
persistencia después de reiniciar el servidor.

## Comandos

```powershell
.\tests\PROBAR_CONVERSACION_AUTOMATICA_REGISTRO_12_4.ps1
```

Tras reiniciar el servidor:

```powershell
.\tests\PROBAR_CONVERSACION_AUTOMATICA_REGISTRO_12_4.ps1 -SoloComprobarPersistencia
```
