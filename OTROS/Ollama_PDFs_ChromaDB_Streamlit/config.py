# ============================================================
# CONFIGURACION DE VOZ (SINTESIS DE TEXTO A VOZ)
# ============================================================
# Velocidad del habla (Palabras por minuto). Por defecto suele ser 200.
# Un valor de 140 - 150 es mas pausado y facil de entender (Lectura Facil).
TTS_RATE = 140

# Volumen del motor de voz (Rango de 0.0 a 1.0)
TTS_VOLUME = 1.0

# Idioma preferido para la voz. Buscara entre las voces instaladas en Windows.
TTS_LANGUAGE = "spanish"

# ============================================================
# CONFIGURACION DE MODELOS IA (OLLAMA)
# ============================================================
# Estos nombres deben coincidir exactamente con los instalados ('ollama list').
MODEL_CHAT = "llama3.2:3b"
MODEL_EMBED = "nomic-embed-text:latest"

# ============================================================
# CONFIGURACION DE BASE DE DATOS Y RAG (CHROMA DB)
# ============================================================
# Carpeta local donde ChromaDB guardara la memoria y los PDFs vectorizados.
CHROMA_PATH = "./chroma_db_pdf"
COLLECTION_NAME = "documentos_y_memoria"

# Numero de fragmentos recuperados para contestar.
TOP_K = 5

# Tamano de fragmentos de texto del PDF y solape de memoria.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
