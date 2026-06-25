from __future__ import annotations

import random

from app.robot.base import PoseCommand


EMOTION_POSES: dict[str, list[PoseCommand]] = {
    "saludo": [PoseCommand(yaw=10, pitch=-4, left_antenna=35, right_antenna=35, duration_s=0.32), PoseCommand(yaw=-8, pitch=-2, left_antenna=15, right_antenna=15, duration_s=0.32)],
    "alegre": [PoseCommand(yaw=0, pitch=-8, left_antenna=45, right_antenna=45, duration_s=0.42)],
    "celebracion": [PoseCommand(yaw=-10, pitch=-10, roll=-4, left_antenna=55, right_antenna=55, duration_s=0.24), PoseCommand(yaw=10, pitch=-10, roll=4, left_antenna=35, right_antenna=35, duration_s=0.24), PoseCommand(yaw=0, pitch=-8, left_antenna=60, right_antenna=60, duration_s=0.26)],
    "animo": [PoseCommand(yaw=0, pitch=-6, left_antenna=35, right_antenna=35, duration_s=0.35), PoseCommand(yaw=6, pitch=-4, left_antenna=42, right_antenna=42, duration_s=0.30)],
    "paciencia": [PoseCommand(yaw=0, pitch=4, roll=0, left_antenna=8, right_antenna=8, duration_s=0.65)],
    "escucha_activa": [PoseCommand(yaw=-6, pitch=2, roll=-2, left_antenna=12, right_antenna=18, duration_s=0.36), PoseCommand(yaw=6, pitch=1, roll=2, left_antenna=18, right_antenna=12, duration_s=0.36)],
    "pensando": [PoseCommand(yaw=-8, pitch=8, roll=-4, left_antenna=-15, right_antenna=15, duration_s=0.45)],
    "curioso": [PoseCommand(yaw=12, pitch=-6, roll=5, left_antenna=20, right_antenna=-10, duration_s=0.55)],
    "sorprendido": [PoseCommand(pitch=-12, left_antenna=55, right_antenna=55, duration_s=0.35)],
    "calma": [PoseCommand(yaw=0, pitch=6, left_antenna=-8, right_antenna=-8, duration_s=0.75)],
    "empatia": [PoseCommand(yaw=-4, pitch=8, roll=-2, left_antenna=-10, right_antenna=-10, duration_s=0.65)],
    "triste": [PoseCommand(yaw=0, pitch=12, left_antenna=-35, right_antenna=-35, duration_s=0.65)],
    "preocupado": [PoseCommand(yaw=-8, pitch=10, roll=-4, left_antenna=-18, right_antenna=-18, duration_s=0.55)],
    "asustado": [PoseCommand(pitch=10, roll=-5, left_antenna=-50, right_antenna=-50, duration_s=0.45)],
    "miedo": [PoseCommand(pitch=10, roll=5, left_antenna=-50, right_antenna=-50, duration_s=0.45)],
    "timido": [PoseCommand(yaw=-18, pitch=8, left_antenna=-15, right_antenna=-5, duration_s=0.55)],
    "enfadado_suave": [PoseCommand(pitch=-4, roll=-5, left_antenna=-8, right_antenna=-8, duration_s=0.35)],
    "pedir_turno": [PoseCommand(yaw=0, pitch=-4, left_antenna=60, right_antenna=10, duration_s=0.45)],
    "repetir": [PoseCommand(yaw=-8, pitch=2, left_antenna=18, right_antenna=18, duration_s=0.25), PoseCommand(yaw=8, pitch=2, left_antenna=18, right_antenna=18, duration_s=0.25)],
    "asentir": [PoseCommand(pitch=-12, duration_s=0.18), PoseCommand(pitch=12, duration_s=0.18), PoseCommand(pitch=0, duration_s=0.18)],
    "negar": [PoseCommand(yaw=-18, duration_s=0.18), PoseCommand(yaw=18, duration_s=0.18), PoseCommand(yaw=0, duration_s=0.18)],
    "baile": [PoseCommand(yaw=-18, roll=-8, left_antenna=45, right_antenna=-45, duration_s=0.24), PoseCommand(yaw=18, roll=8, left_antenna=-45, right_antenna=45, duration_s=0.24), PoseCommand(yaw=0, roll=0, left_antenna=35, right_antenna=35, duration_s=0.24)],
    "juego": [PoseCommand(yaw=-12, pitch=-8, roll=-6, left_antenna=40, right_antenna=20, duration_s=0.28), PoseCommand(yaw=12, pitch=-8, roll=6, left_antenna=20, right_antenna=40, duration_s=0.28)],
    "aplauso": [PoseCommand(yaw=-5, pitch=-8, left_antenna=65, right_antenna=65, duration_s=0.20), PoseCommand(yaw=5, pitch=-8, left_antenna=35, right_antenna=35, duration_s=0.20), PoseCommand(yaw=0, pitch=-8, left_antenna=65, right_antenna=65, duration_s=0.20)],
    "esconderse": [PoseCommand(pitch=18, left_antenna=-60, right_antenna=-60, duration_s=0.7)],
    "neutral": [PoseCommand(duration_s=0.25)],
}


# v5.8: alias y emociones extra para actividades guiadas. Algunas trayectorias
# se inspiran en la versión anterior del controlador: alegría dinámica,
# miedo/asustado, baile, saludo, asentir y negar se basaban en combinaciones
# de cabeza + antenas y en mantener el idle bloqueado durante acciones.
EMOTION_POSES.update({
    "enfadado": EMOTION_POSES.get("enfadado_suave", EMOTION_POSES["neutral"]),
    "sorprendido": EMOTION_POSES.get("sorprendido", EMOTION_POSES["neutral"]),
    "animal": EMOTION_POSES.get("juego", EMOTION_POSES["neutral"]),
    "cuento": EMOTION_POSES.get("curioso", EMOTION_POSES["neutral"]),
    "cantar": EMOTION_POSES.get("alegre", EMOTION_POSES["neutral"]),
    "respirar": EMOTION_POSES.get("calma", EMOTION_POSES["neutral"]),
    "explicacion_alegre": [PoseCommand(yaw=-6, pitch=-6, roll=-3, left_antenna=38, right_antenna=32, duration_s=0.28), PoseCommand(yaw=6, pitch=-4, roll=3, left_antenna=32, right_antenna=38, duration_s=0.28)],
    "escuchar_pregunta": [PoseCommand(yaw=8, pitch=3, roll=4, left_antenna=8, right_antenna=28, duration_s=0.45)],
    "refuerzo_positivo": [PoseCommand(yaw=-8, pitch=-8, roll=-5, left_antenna=55, right_antenna=55, duration_s=0.24), PoseCommand(yaw=8, pitch=-8, roll=5, left_antenna=35, right_antenna=35, duration_s=0.24), PoseCommand(yaw=0, pitch=-8, left_antenna=65, right_antenna=65, duration_s=0.28)],
})

def poses_for_emotion(emotion: str) -> list[PoseCommand]:
    return EMOTION_POSES.get(emotion, EMOTION_POSES["neutral"])


def idle_pose() -> PoseCommand:
    return PoseCommand(
        yaw=random.uniform(-8, 8),
        pitch=random.uniform(-3, 5),
        roll=random.uniform(-3, 3),
        left_antenna=random.uniform(-10, 22),
        right_antenna=random.uniform(-10, 22),
        duration_s=random.uniform(0.45, 0.9),
    )


def speech_reactive_pose(intensity: float = 0.7) -> PoseCommand:
    intensity = max(0.0, min(1.0, intensity))
    return PoseCommand(
        yaw=random.uniform(-5, 5) * intensity,
        pitch=random.uniform(-4, 3) * intensity,
        roll=random.uniform(-3, 3) * intensity,
        left_antenna=random.uniform(6, 32) * intensity,
        right_antenna=random.uniform(6, 32) * intensity,
        duration_s=random.uniform(0.16, 0.34),
    )
