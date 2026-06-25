from __future__ import annotations

import re
from dataclasses import dataclass


EMOTION_TAGS: dict[str, str] = {
    "SALUDO": "saludo",
    "ALEGRE": "alegre",
    "CELEBRACION": "celebracion",
    "CELEBRACIÓN": "celebracion",
    "ANIMO": "animo",
    "ÁNIMO": "animo",
    "PACIENCIA": "paciencia",
    "ESCUCHA_ACTIVA": "escucha_activa",
    "ESCUCHA": "escucha_activa",
    "PENSANDO": "pensando",
    "CURIOSO": "curioso",
    "SORPRENDIDO": "sorprendido",
    "CALMA": "calma",
    "EMPATIA": "empatia",
    "EMPATÍA": "empatia",
    "TRISTE": "triste",
    "PREOCUPADO": "preocupado",
    "ASUSTADO": "asustado",
    "MIEDO": "miedo",
    "TIMIDO": "timido",
    "TÍMIDO": "timido",
    "ENFADADO": "enfadado_suave",
    "ENFADADO_SUAVE": "enfadado_suave",
    "PEDIR_TURNO": "pedir_turno",
    "REPETIR": "repetir",
    "ASENTIR": "asentir",
    "NEGAR": "negar",
    "BAILE": "baile",
    "JUEGO": "juego",
    "APLAUSO": "aplauso",
    "ESCONDERSE": "esconderse",
    "NEUTRAL": "neutral",
}

TAG_RE = re.compile(r"\[([A-ZÁÉÍÓÚÑ_]+)\]", re.IGNORECASE)


@dataclass(frozen=True)
class ParsedEmotion:
    emotion: str
    clean_text: str
    detected_tag: str | None = None


def normalize_emotion(value: str | None) -> str:
    if not value:
        return "neutral"
    key = value.strip().upper().replace(" ", "_").replace("-", "_")
    return EMOTION_TAGS.get(key, value.strip().lower().replace(" ", "_"))


def parse_emotion(text: str, process_emotions: bool = True) -> ParsedEmotion:
    if not process_emotions:
        return ParsedEmotion(emotion="neutral", clean_text=text.strip(), detected_tag=None)

    match = TAG_RE.search(text)
    if not match:
        return ParsedEmotion(emotion=_infer_from_text(text), clean_text=text.strip(), detected_tag=None)

    tag = match.group(1).upper()
    emotion = EMOTION_TAGS.get(tag, "neutral")
    clean = TAG_RE.sub("", text, count=1).strip()
    return ParsedEmotion(emotion=emotion, clean_text=clean, detected_tag=tag)


def _infer_from_text(text: str) -> str:
    lowered = text.lower()
    if any(w in lowered for w in ["hola", "kaixo", "buenas", "bienvenido", "bienvenida"]):
        return "saludo"
    if any(w in lowered for w in ["gracias", "genial", "muy bien", "alegr", "bravo", "perfecto"]):
        return "celebracion"
    if any(w in lowered for w in ["vamos", "puedes", "ánimo", "animo", "inténtalo", "intentalo"]):
        return "animo"
    if any(w in lowered for w in ["tranquilo", "tranquila", "calma", "despacio", "poco a poco"]):
        return "calma"
    if any(w in lowered for w in ["te entiendo", "comprendo", "acompaño"]):
        return "empatia"
    if any(w in lowered for w in ["repite", "otra vez", "no entiendo"]):
        return "repetir"
    if any(w in lowered for w in ["pienso", "quizá", "quizas", "analizar", "espera"]):
        return "pensando"
    return "escucha_activa"
