# =====================================================================
# CONFIGURACIÓN GENERAL DEL ECOSISTEMA REACHY MINI
# =====================================================================

# --- Inteligencia Artificial (Ollama) ---
# Modelo LLM local que se utilizará para procesar las respuestas del robot
OLLAMA_MODEL = "llama3.2:3b"

# --- Simulación y Hardware ---
# Dirección IP donde se ejecuta el reachy-mini-daemon (Simulador MuJoCo)
ROBOT_HOST = "127.0.0.1"

# --- Catálogo de Movimientos ---
# Repositorio oficial en Hugging Face con el dataset de animaciones
HF_LIBRARY = "pollen-robotics/reachy-mini-emotions-library"