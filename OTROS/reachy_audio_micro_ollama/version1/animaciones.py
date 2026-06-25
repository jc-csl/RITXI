import os
import pygame
from reachy_mini import ReachyMini
from reachy_mini.motion.recorded_move import RecordedMoves

# Constantes fijas del ecosistema simulado
ROBOT_HOST = "127.0.0.1"
HF_LIBRARY = "pollen-robotics/reachy-mini-emotions-library"

class GestorAnimaciones:
    """
    Clase encargada de desacoplar la API de FastAPI del SDK físico del robot.
    Controla el hardware, el sonido y la descarga de trayectorias.
    """
    def __init__(self):
        self.robot = None
        self.library = None
        self.available_emotions = []
        
        # Inicializamos el subsistema de audio local (Pygame) para los archivos .wav
        pygame.mixer.init()
        
        # Intentamos la conexión inicial con el simulador MuJoCo
        self.conectar_robot()
        # Descargamos el catálogo de Hugging Face
        self.cargar_libreria_hf()

    def conectar_robot(self):
        """Intenta establecer conexión con el socket del reachy-mini-daemon."""
        try:
            print(f"[ROBOT] Conectando al simulador en {ROBOT_HOST}...")
            self.robot = ReachyMini(host=ROBOT_HOST)
            print("[ROBOT] ¡Conexión establecida con éxito!")
        except Exception as e:
            print(f"[ROBOT] Advertencia: Daemon no detectado en {ROBOT_HOST}. Se reintentará en caliente.")
            self.robot = None

    def cargar_libreria_hf(self):
        """Descarga e indexa los metadatos de las 81 emociones desde la nube."""
        try:
            print(f"[HF] Descargando catálogo desde {HF_LIBRARY}...")
            self.library = RecordedMoves(HF_LIBRARY)
            self.available_emotions = self.library.list_moves()
            print(f"[HF] ¡Éxito! {len(self.available_emotions)} movimientos indexados.")
        except Exception as e:
            print(f"[HF] Error crítico al conectar con Hugging Face: {e}")
            self.available_emotions = []

    def ejecutar_movimiento(self, emotion_id: str):
        """
        Lógica nuclear del robot. Procesa el ID, reproduce el audio y altera los motores.
        """
        # 1. Reconexión en caliente (Hot-reload) si el simulador se encendió tarde
        if not self.robot:
            try:
                self.robot = ReachyMini(host=ROBOT_HOST)
            except Exception:
                raise RuntimeError("El reachy-mini-daemon sigue sin responder.")

        # 2. Caso especial: Comando de reinicio / postura neutra de seguridad
        if emotion_id == "wake_up":
            if hasattr(self.robot, 'wake_up'):
                self.robot.wake_up()
            return "wake_up"

        # 3. Algoritmo de tolerancia a fallos de nomenclatura en Hugging Face
        move = None
        try:
            move = self.library.get(emotion_id)  # Intento estándar (ej: gasp1)
        except Exception:
            if emotion_id.endswith("1"):  # Fallback si el ID requiere remover el sufijo numérico (ej: gasp)
                fallback_id = emotion_id[:-1]
                print(f"[CINETICA] ID '{emotion_id}' ausente. Reintentando variante limpia: '{fallback_id}'...")
                try:
                    move = self.library.get(fallback_id)
                except Exception:
                    pass

        if move is None:
            raise ValueError(f"El movimiento '{emotion_id}' no existe en el repositorio.")

        # 4. Reproducción del sonido sincronizado (.wav) por los altavoces locales
        if hasattr(move, 'audio_path') and move.audio_path and os.path.exists(move.audio_path):
            print(f"[AUDIO] Reproduciendo archivo: {move.audio_path}")
            pygame.mixer.music.load(move.audio_path)
            pygame.mixer.music.play()
        else:
            print(f"[AUDIO] El movimiento '{emotion_id}' no dispone de pista de sonido.")

        # 5. Envío de la matriz de ángulos de servos al simulador gráfico MuJoCo
        self.robot.play_move(move)
        return emotion_id