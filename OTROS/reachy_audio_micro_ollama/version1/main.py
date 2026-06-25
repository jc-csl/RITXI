import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from reachy_mini import ReachyMini
from reachy_mini.motion.recorded_move import RecordedMoves

# =====================================================================
# CONFIGURACIÓN DE CONSTANTES GLOBALES E IP FIJA
# =====================================================================
ROBOT_HOST = "127.0.0.1"  # IP del simulador local
HF_LIBRARY = "pollen-robotics/reachy-mini-emotions-library"

# Inicializar el mezclador de audio de hardware para los efectos .wav
import pygame
pygame.mixer.init()

app = FastAPI(title="Reachy Mini - Matriz Completa de 81 Emociones")

# Conexión inicial al daemon del simulador
try:
    print(f"Conectando al simulador Reachy Mini en {ROBOT_HOST}...")
    robot = ReachyMini(host=ROBOT_HOST) 
    print("¡Conexión inicial con el simulador establecida con éxito!")
except Exception as e:
    print(f"Advertencia: No se detecta daemon activo en {ROBOT_HOST} ({e}). Conectando en diferido...")
    robot = None

# Indexar el catálogo de movimientos directo desde Hugging Face
print(f"Cargando base de datos de emociones desde Hugging Face ({HF_LIBRARY})...")
try:
    library = RecordedMoves(HF_LIBRARY)
    available_emotions = library.list_moves()
    print(f"¡Éxito! {len(available_emotions)} emociones indexadas en la nube.")
except Exception as e:
    print(f"Error al conectar con Hugging Face: {e}")
    available_emotions = []

# Mapeo semántico estructurado y ampliado para el dataset real de Hugging Face
EMOTION_MAP = [
    # Esenciales y Sistema
    {"id": "wake_up", "name": "Despertar / Reset Postura", "emoji": "☀️"},
    
    # Alegría, Orgullo y Éxito
    {"id": "cheerful1", "name": "Alegría / Amor", "emoji": "🥰"},
    {"id": "loving1", "name": "Afectuoso", "emoji": "🤟"},
    {"id": "laughing1", "name": "Risa 1", "emoji": "😂"},
    {"id": "laughing2", "name": "Risa 2", "emoji": "😸"},
    {"id": "proud1", "name": "Orgulloso 1", "emoji": "😎"},
    {"id": "proud2", "name": "Orgulloso 2", "emoji": "😏"},
    {"id": "proud3", "name": "Orgulloso 3", "emoji": "🦁"},
    {"id": "success1", "name": "Éxito / Victoria 1", "emoji": "🏆"},
    {"id": "success2", "name": "Éxito / Victoria 2", "emoji": "🎉"},
    {"id": "enthusiastic1", "name": "Entusiasta 1", "emoji": "🤩"},
    {"id": "enthusiastic2", "name": "Entusiasta 2", "emoji": "⚡"},
    {"id": "grateful1", "name": "Agradecido", "emoji": "🙏"},

    # Respuestas Sí / No
    {"id": "yes1", "name": "Sí / Afirmación", "emoji": "👍"},
    {"id": "yes_sad1", "name": "Sí (Triste)", "emoji": "😔"},
    {"id": "no1", "name": "No / Negación", "emoji": "👎"},
    {"id": "no_excited1", "name": "No (Emocionado)", "emoji": "🙅"},
    {"id": "no_sad1", "name": "No (Triste)", "emoji": "❌"},

    # Animación y Baile
    {"id": "dance1", "name": "Baile Rítmico 1", "emoji": "🕺"},
    {"id": "dance2", "name": "Baile Rítmico 2", "emoji": "💃"},
    {"id": "dance3", "name": "Baile Rítmico 3", "emoji": "🎶"},

    # Sorpresa y Curiosidad
    {"id": "gasp1", "name": "Sorpresa / Jadeo", "emoji": "😲"},
    {"id": "amazed1", "name": "Asombrado", "emoji": "✨"},
    {"id": "surprised1", "name": "Sorprendido 1", "emoji": "😮"},
    {"id": "surprised2", "name": "Sorprendido 2", "emoji": "🙀"},
    {"id": "curious1", "name": "Curioso", "emoji": "🧐"},
    {"id": "inquiring1", "name": "Inquisitivo 1", "emoji": "❓"},
    {"id": "inquiring2", "name": "Inquisitivo 2", "emoji": "🔍"},
    {"id": "inquiring3", "name": "Inquisitivo 3", "emoji": "🔎"},

    # Tristeza, Cansancio y Sueño
    {"id": "sad1", "name": "Triste / Llorar 1", "emoji": "😭"},
    {"id": "sad2", "name": "Triste / Llorar 2", "emoji": "😢"},
    {"id": "downcast1", "name": "Cabizbajo", "emoji": "📉"},
    {"id": "lonely1", "name": "Solitario", "emoji": "🏚️"},
    {"id": "boredom1", "name": "Aburrimiento 1", "emoji": "🥱"},
    {"id": "boredom2", "name": "Aburrimiento 2", "emoji": "💤"},
    {"id": "sleepy1", "name": "Soñoliento", "emoji": "😴"},
    {"id": "sleep1", "name": "Dormido profundo", "emoji": "🛌"},
    {"id": "exhausted1", "name": "Agotado", "emoji": "😫"},
    {"id": "tired1", "name": "Cansado", "emoji": "🪫"},
    {"id": "dying1", "name": "Sin energía / Agonizando", "emoji": "💀"},

    # Enojo, Frustración y Reprimenda
    {"id": "angry1", "name": "Enojado", "emoji": "😡"},
    {"id": "furious1", "name": "Furioso", "emoji": "🤬"},
    {"id": "rage1", "name": "Rabia", "emoji": "👿"},
    {"id": "frustrated1", "name": "Frustrado", "emoji": "😤"},
    {"id": "irritated1", "name": "Irritado 1", "emoji": "😠"},
    {"id": "irritated2", "name": "Irritado 2", "emoji": "😒"},
    {"id": "reprimand1", "name": "Regañar / Reprimenda 1", "emoji": "☝️"},
    {"id": "reprimand2", "name": "Regañar / Reprimenda 2", "emoji": "🫵"},
    {"id": "reprimand3", "name": "Regañar / Reprimenda 3", "emoji": "🗯️"},

    # Ansiedad, Temor y Confusión
    {"id": "anxiety1", "name": "Ansiedad", "emoji": "😰"},
    {"id": "fear1", "name": "Miedo", "emoji": "😨"},
    {"id": "scared1", "name": "Asustado", "emoji": "😱"},
    {"id": "confused1", "name": "Confundido", "emoji": "🧩"},
    {"id": "uncertain1", "name": "Incierto", "emoji": "🤷"},
    {"id": "uncomfortable1", "name": "Incómodo", "emoji": "🫥"},
    {"id": "shy1", "name": "Tímido", "emoji": "😳"},

    # Interacción Social y Calma
    {"id": "hello1", "name": "Saludo / Hola", "emoji": "🙋"},
    {"id": "come1", "name": "Ven aquí", "emoji": "🫴"},
    {"id": "welcoming1", "name": "Bienvenida 1", "emoji": "👐"},
    {"id": "welcoming2", "name": "Bienvenida 2", "emoji": "🤝"},
    {"id": "helpful1", "name": "Servicial 1", "emoji": "😇"},
    {"id": "helpful2", "name": "Servicial 2", "emoji": "💟"},
    {"id": "calming1", "name": "Tranquilizador", "emoji": "🍃"},
    {"id": "serenity1", "name": "Serenidad", "emoji": "🧘"},
    {"id": "relief1", "name": "Alivio 1", "emoji": "😮‍💨"},
    {"id": "relief2", "name": "Alivio 2", "emoji": "😌"},

    # Cognitivos / Pensamiento
    {"id": "thoughtful1", "name": "Reflexivo 1", "emoji": "🤔"},
    {"id": "thoughtful2", "name": "Reflexivo 2", "emoji": "💭"},
    {"id": "understanding1", "name": "Comprensivo 1", "emoji": "💡"},
    {"id": "understanding2", "name": "Comprensivo 2", "emoji": "👌"},
    {"id": "lost1", "name": "Perdido / Desorientado", "emoji": "🌀"},

    # Errores / Accidentes / Otros
    {"id": "oops1", "name": "Oops 1", "emoji": "🤭"},
    {"id": "oops2", "name": "Oops 2", "emoji": "🙈"},
    {"id": "disgusted1", "name": "Disgustado", "emoji": "🤢"},
    {"id": "contempt1", "name": "Desprecio", "emoji": "😏"},
    {"id": "displeased1", "name": "Descontento 1", "emoji": "😟"},
    {"id": "displeased2", "name": "Descontento 2", "emoji": "☹️"},
    {"id": "electric1", "name": "Efecto Eléctrico", "emoji": "🔌"}
]

# Rellenar automáticamente con un emoji genérico por si aparece un ID nuevo en el repositorio
existing_ids = {item["id"] for item in EMOTION_MAP}
for raw_move in available_emotions:
    if raw_move not in existing_ids:
        EMOTION_MAP.append({
            "id": raw_move,
            "name": f"Movimiento detectado: {raw_move}",
            "emoji": "🤖"
        })

@app.get("/api/emotions")
def get_emotions():
    """Devuelve la matriz completa de emociones al frontend."""
    return EMOTION_MAP

@app.post("/api/play/{emotion_id}")
def play_emotion(emotion_id: str):
    """Endpoint que procesa las peticiones de animación cinemática y sonido."""
    global robot
    
    # Reconexión dinámica en caliente si el daemon se inició con retraso
    if not robot:
        try:
            robot = ReachyMini(host=ROBOT_HOST)
        except Exception:
            raise HTTPException(
                status_code=503, 
                detail=f"El reachy-mini-daemon no responde en {ROBOT_HOST}."
            )
            
    try:
        print(f"Procesando comando para: {emotion_id}")
        
        if emotion_id == "wake_up":
            if hasattr(robot, 'wake_up'):
                robot.wake_up()
            return {"status": "success", "executed": "wake_up"}

        # Algoritmo de tolerancia a fallos de nomenclatura
        move = None
        try:
            move = library.get(emotion_id)
        except Exception:
            if emotion_id.endswith("1"):
                fallback_id = emotion_id[:-1]
                print(f"⚠️ Reintentando variante limpia: '{fallback_id}'...")
                try:
                    move = library.get(fallback_id)
                except Exception:
                    pass

        if move is None:
            raise ValueError(f"El movimiento '{emotion_id}' no existe en Hugging Face.")

        # 🔊 Reproducción de Audio local sincronizada (.wav)
        if hasattr(move, 'audio_path') and move.audio_path and os.path.exists(move.audio_path):
            print(f"🔊 Reproduciendo: {move.audio_path}")
            pygame.mixer.music.load(move.audio_path)
            pygame.mixer.music.play()
        else:
            print(f"⚠️ Nota: '{emotion_id}' no contiene audio funcional.")

        # 🤖 Envío de trayectoria cinemática a MuJoCo
        robot.play_move(move)
        return {"status": "success", "executed": emotion_id}
        
    except Exception as e:
        print(f"Aviso del sistema: {e}")
        raise HTTPException(
            status_code=404, 
            detail=f"Error al procesar la animación: {str(e)}"
        )

@app.get("/", response_class=HTMLResponse)
def index():
    """Renderiza el Dashboard Web optimizado para micro-tarjetas de 81 emociones."""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel Reachy Mini - 81 Emociones</title>
        <style>
            body { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                background-color: #0f0f0f; 
                color: #ffffff; 
                text-align: center; 
                padding: 15px; 
                margin: 0; 
            }
            h1 { color: #ff9800; margin-top: 10px; margin-bottom: 5px; font-size: 1.6rem; }
            p { color: #888888; font-size: 0.85rem; margin-bottom: 15px; }
            
            .grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fill, minmax(55px, 1fr)); 
                gap: 6px; 
                max-width: 95vw; 
                margin: 0 auto; 
                padding: 5px; 
            }
            
            .card { 
                background-color: #1a1a1a; 
                border: 1px solid #2a2a2a; 
                border-radius: 8px; 
                padding: 10px 0;
                cursor: pointer; 
                transition: all 0.15s ease-in-out; 
                text-align: center; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.4);
            }
            .card:hover { 
                transform: scale(1.15); 
                border-color: #ff9800; 
                background-color: #2b2b2b; 
                z-index: 10;
            }
            .emoji { 
                font-size: 1.8rem; 
                display: block; 
            }
            
            #log { 
                margin-top: 20px; 
                background: #000000; 
                padding: 10px; 
                border-radius: 6px; 
                max-width: 800px; 
                margin-left: auto; 
                margin-right: auto; 
                font-family: 'Courier New', monospace; 
                color: #00ff00; 
                text-align: left; 
                height: 70px; 
                overflow-y: auto; 
                border: 1px solid #222;
                font-size: 0.8rem;
            }
        </style>
    </head>
    <body>
        <h1>🎮 Reachy Mini - Matriz de Emociones</h1>
        <p>Mapeo dinámico completo del dataset de Hugging Face en micro-recuadros</p>
        
        <div class="grid" id="grid"></div>
        
        <div id="log">>> Sistema listo. Haz clic sobre cualquier casilla para enviar el comando...</div>
        
        <script>
            const logBox = document.getElementById('log');
            function log(txt, color='#00ff00') { 
                logBox.innerHTML += `<br>>><span style="color:${color}"> ${txt}</span>`; 
                logBox.scrollTop = logBox.scrollHeight; 
            }

            fetch('/api/emotions')
                .then(r => r.json())
                .then(data => {
                    const grid = document.getElementById('grid');
                    data.forEach(emo => {
                        const card = document.createElement('div');
                        card.className = 'card';
                        
                        card.title = emo.name + " (" + emo.id + ")";
                        card.innerHTML = `<span class="emoji">${emo.emoji}</span>`;
                        
                        card.onclick = () => {
                            log('Accionando -> ' + emo.id);
                            
                            fetch('/api/play/' + emo.id, { method: 'POST' })
                                .then(res => { 
                                    if(!res.ok) {
                                        return res.json().then(err => { throw new Error(err.detail) });
                                    }
                                    return res.json(); 
                                })
                                .then(data => log('Éxito en simulación: ' + emo.id))
                                .catch(err => log('Nota: ' + err.message, '#ff9800'));
                        };
                        grid.appendChild(card);
                    });
                })
                .catch(err => log('ERROR: No se pudo enlazar el listado con FastAPI.', '#ff0000'));
        </script>
    </body>
    </html>
    """