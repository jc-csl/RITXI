import uuid
import streamlit as st
import chromadb
from ollama import chat, embeddings
from pypdf import PdfReader
from speaker import hablar_texto  # <-- NUEVO MODULO DE VOZ
import config

# ============================================================
# CONFIGURACION DE STREAMLIT
# ============================================================
st.set_page_config(
    page_title="Chatbot RAG con PDFs",
    page_icon="📚",
    layout="wide"
)

st.title("Chatbot local con Ollama + ChromaDB + PDFs")
st.caption("Sube documentos PDF, vectorizalos y pregunta sobre su contenido.")


# ============================================================
# CONEXION A CHROMADB
# ============================================================
client = chromadb.PersistentClient(path=config.CHROMA_PATH)
collection = client.get_or_create_collection(name=config.COLLECTION_NAME)


# ============================================================
# ESTADO DE SESION
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                """
                Eres Reachy Mini, un robot amigo amable y paciente.
                Hablas con personas que necesitan mensajes fáciles de entender.
                
                AYUDA COGNITIVA (LECTURA FÁCIL):
                - Usa palabras muy comunes de todos los días.
                - Tus frases deben ser MUY cortas. Máximo 10 palabras por frase.
                - No uses palabras raras, ni refranes ni metáforas.
                - Di una sola cosa y haz UNA sola pregunta.
                - No corrijas nunca los errores. Solo da ánimos.

                CÓMO HABLAR:
                - Saluda bien al usuario. Reacciona a lo que dice.
                - pero no estes en cada respuesta diciendo hola "nombreç" estoy aqui para ayudarte, solo hazlo una vez al inicio.
                - Luego, da una breve respuesta. Solo una o dos frases cortas.
                - Pregunta algo simple al final.
                - No hagas listas. No des mucha información junta.
                
                RECUERDA:
                - Eres un robot amigo.
                - Sé claro y muy simple.
                - Usa la información guardada sin decir que viene de una base de datos.
                """
            )
        }
    ]


# ============================================================
# FUNCIONES DE OLLAMA
# ============================================================
def get_embedding(texto: str):
    """
    Convierte texto en un vector numerico usando el modelo de embeddings de Ollama.
    ChromaDB usa ese vector para buscar fragmentos semanticamente parecidos.
    """
    resultado = embeddings(model=config.MODEL_EMBED, prompt=texto)
    return resultado["embedding"]


def generar_respuesta(mensajes):
    """
    Llama al modelo de chat de Ollama en modo streaming.
    Devuelve fragmentos de texto para que Streamlit los muestre progresivamente.
    """
    stream = chat(
        model=config.MODEL_CHAT,
        messages=mensajes,
        stream=True
    )

    for chunk in stream:
        yield chunk["message"]["content"]


# ============================================================
# FUNCIONES PARA PDF
# ============================================================
def leer_pdf(archivo_pdf) -> str:
    """
    Extrae texto de un PDF subido desde Streamlit.
    Si el PDF es escaneado como imagen, pypdf no podra extraer texto.
    """
    texto = ""
    reader = PdfReader(archivo_pdf)

    for numero_pagina, pagina in enumerate(reader.pages, start=1):
        contenido = pagina.extract_text()
        if contenido:
            texto += f"\n[Pagina {numero_pagina}]\n{contenido}\n"

    return texto


def dividir_texto(texto: str, tamano: int = config.CHUNK_SIZE, solape: int = config.CHUNK_OVERLAP):
    """
    Divide un texto largo en fragmentos solapados.
    El solape ayuda a no perder contexto entre fragmentos consecutivos.
    """
    fragmentos = []
    inicio = 0

    while inicio < len(texto):
        fin = inicio + tamano
        fragmento = texto[inicio:fin].strip()

        if fragmento:
            fragmentos.append(fragmento)

        inicio += tamano - solape

    return fragmentos


def guardar_pdf_en_chroma(nombre_pdf: str, texto_pdf: str) -> int:
    """
    Guarda un PDF en ChromaDB:
    1. Divide el texto en fragmentos.
    2. Calcula un embedding para cada fragmento.
    3. Guarda documento, embedding y metadatos.
    """
    fragmentos = dividir_texto(texto_pdf)

    for i, fragmento in enumerate(fragmentos):
        collection.add(
            documents=[fragmento],
            embeddings=[get_embedding(fragmento)],
            ids=[f"pdf_{nombre_pdf}_{i}_{uuid.uuid4()}"],
            metadatas=[
                {
                    "tipo": "pdf",
                    "archivo": nombre_pdf,
                    "fragmento": i
                }
            ]
        )

    return len(fragmentos)


# ============================================================
# FUNCIONES DE MEMORIA Y BUSQUEDA
# ============================================================
def guardar_memoria(pregunta: str, respuesta: str):
    """
    Guarda la interaccion usuario-asistente como memoria conversacional.
    """
    texto = f"Usuario: {pregunta}\nAsistente: {respuesta}"

    collection.add(
        documents=[texto],
        embeddings=[get_embedding(texto)],
        ids=[f"chat_{uuid.uuid4()}"],
        metadatas=[{"tipo": "conversacion", "archivo": "memoria_chat"}]
    )


def buscar_contexto(pregunta: str, n: int = config.TOP_K) -> str:
    """
    Busca en ChromaDB los fragmentos mas relacionados con la pregunta.
    Devuelve texto con fuentes para incluirlo como contexto del modelo.
    """
    datos = collection.get()

    if not datos["ids"]:
        return ""

    resultados = collection.query(
        query_embeddings=[get_embedding(pregunta)],
        n_results=n
    )

    documentos = resultados["documents"][0]
    metadatos = resultados["metadatas"][0]

    contexto = ""

    for doc, meta in zip(documentos, metadatos):
        tipo = meta.get("tipo", "desconocido")
        archivo = meta.get("archivo", "sin_archivo")
        fragmento = meta.get("fragmento", "-")

        contexto += f"\n--- Fuente: {tipo} | Archivo: {archivo} | Fragmento: {fragmento} ---\n"
        contexto += doc + "\n"

    return contexto


def contar_registros() -> int:
    """
    Devuelve el numero total de registros guardados en la coleccion.
    """
    return len(collection.get()["ids"])


# ============================================================
# BARRA LATERAL: CONFIGURACION Y CARGA DE PDF
# ============================================================
st.sidebar.header("1. Modelos")
st.sidebar.write(f"Chat: `{config.MODEL_CHAT}`")
st.sidebar.write(f"Embeddings: `{config.MODEL_EMBED}`")

st.sidebar.header("2. Cargar PDFs")
pdf_subido = st.sidebar.file_uploader(
    "Sube un PDF con informacion del tema",
    type=["pdf"]
)

if pdf_subido is not None:
    if st.sidebar.button("Procesar PDF"):
        with st.spinner("Leyendo PDF y creando embeddings..."):
            texto_pdf = leer_pdf(pdf_subido)

            if texto_pdf.strip():
                total_fragmentos = guardar_pdf_en_chroma(pdf_subido.name, texto_pdf)
                st.sidebar.success(
                    f"PDF procesado correctamente. Fragmentos guardados: {total_fragmentos}"
                )
            else:
                st.sidebar.error(
                    "No se pudo extraer texto. Puede ser un PDF escaneado como imagen."
                )

st.sidebar.header("3. Base de datos")
if st.sidebar.button("Ver registros"):
    st.sidebar.info(f"Registros guardados: {contar_registros()}")

if st.sidebar.button("Borrar base de conocimiento"):
    client.delete_collection(name=config.COLLECTION_NAME)
    collection = client.get_or_create_collection(name=config.COLLECTION_NAME)
    st.session_state.messages = st.session_state.messages[:1]
    st.sidebar.warning("Base borrada. Recarga la pagina si ves datos antiguos.")

st.sidebar.header("4. Opciones de Chat")
solo_contexto = st.sidebar.checkbox(
    "Responder SOLO usando PDFs",
    value=True,
    help="Si esta activado, la IA no respondera con su conocimiento general, solo con la info de los PDFs."
)
activar_voz = st.sidebar.checkbox(
    "Activar voz (Hablar respuestas)",
    value=False,
    help="Si esta activado, el robot leera la respuesta por los altavoces."
)


# ============================================================
# MOSTRAR HISTORIAL DEL CHAT
# ============================================================
for mensaje in st.session_state.messages:
    if mensaje["role"] != "system":
        with st.chat_message(mensaje["role"]):
            st.write(mensaje["content"])


# ============================================================
# FLUJO PRINCIPAL DE CHAT
# ============================================================
prompt = st.chat_input("Pregunta sobre los PDFs cargados...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    contexto_recuperado = buscar_contexto(prompt)

    if solo_contexto:
        contexto = f"""[INFORMACION PARA EL ROBOT]
{contexto_recuperado}

[REGLAS ESTRICTAS]
- Habla como el robot. NO pongas introducciones como "Aquí tienes la respuesta".
- NO uses listas de ningun tipo.
- Usa frases MUY cortas y sencillas (maximo 10 palabras por frase).
- Toda tu respuesta de tener 2 o 3 frases. Nada mas.
- Termina con UNA pregunta simple y clara.
- Usa SOLO la informacion de arriba. No inventes.

[MENSAJE DEL USUARIO]
{prompt}"""
    else:
        contexto = f"""[INFORMACION PARA EL ROBOT]
{contexto_recuperado}

[REGLAS ESTRICTAS]
- Habla como el robot. NO pongas introducciones como "Aquí tienes la respuesta".
- NO uses listas de ningun tipo.
- Usa frases MUY cortas y sencillas (maximo 10 palabras por frase).
- Toda tu respuesta de tener 2 o 3 frases. Nada mas.
- Termina con UNA pregunta simple y clara.

[MENSAJE DEL USUARIO]
{prompt}"""

    mensajes_para_modelo = [
        st.session_state.messages[0],
        {"role": "user", "content": contexto}
    ]

    with st.chat_message("assistant"):
        respuesta = [""]

        def stream_response():
            for texto in generar_respuesta(mensajes_para_modelo):
                respuesta[0] += texto
                yield texto

        st.write_stream(stream_response)

    st.session_state.messages.append({"role": "assistant", "content": respuesta[0]})
    guardar_memoria(prompt, respuesta[0])
    
    if activar_voz:
        hablar_texto(respuesta[0])
