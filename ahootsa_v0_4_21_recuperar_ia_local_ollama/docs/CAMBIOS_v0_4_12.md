# Cambios v0.4.12

- Se añade log específico de `ask_ollama`.
- Se reduce el riesgo de bloqueo largo al consultar Ollama.
- `ask_ollama` devuelve `message_for_user` si hay error.
- Se añade `scripts/windows/10_diagnosticar_ask_ollama.ps1`.
- Se añade `DIAGNOSTICAR_ASK_OLLAMA.ps1` en la raíz.
- Se añade `docs/DIAGNOSTICO_ASK_OLLAMA.md`.
- Se refuerzan instrucciones para que, si `ask_ollama` falla, la IA remota diga el error y no se quede en silencio.
