"""
Constantes externas de Ritxi v5.9.71.

Este archivo centraliza valores que antes estaban dispersos:
- modelo por defecto;
- timeouts;
- puerto de Ollama;
- ruta del daemon/robot;
- límites de conversación.

Se puede importar desde otros módulos Python al arrancar.
"""

DEFAULT_MODEL = "gemma3:1b"
DEFAULT_TEMPERATURE = 0.25
OLLAMA_URL = "http://127.0.0.1:11434"
OLLAMA_TIMEOUT_S = 60.0
CHAT_TIMEOUT_MS = 60000
DEFAULT_SESSION_ID = "demo"
MAX_HISTORY_MESSAGES = 2
REACHY_DAEMON_HOST = "127.0.0.1"
REACHY_DAEMON_PORT = 8000
