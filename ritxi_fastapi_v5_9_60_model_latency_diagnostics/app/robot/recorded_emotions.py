from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any

from app.core.config import Settings
from app.core.logging import log_event

logger = logging.getLogger(__name__)

# Aliases semánticos internos -> IDs probables del dataset de Pollen Robotics.
# Se prueban en orden. Si un ID terminado en '1' no existe, se prueba también sin sufijo.
RECORDED_MOVE_ALIASES: dict[str, list[str]] = {
    # IDs reales del dataset HF cuando es posible.
    # Importante: el dataset contiene "sleep1", "thoughtful1", "calming1",
    # "dance1"... pero NO contiene "sleepy1", "hello1", "gasp1" ni "angry1".
    "wake_up": ["welcoming1", "attentive1", "serenity1"],
    "neutral": ["attentive1", "serenity1"],

    "saludo": ["welcoming1", "welcoming2", "come1"],
    "hello": ["welcoming1", "welcoming2", "come1"],
    "hello1": ["welcoming1", "welcoming2", "come1"],
    "welcoming1": ["welcoming1"],

    "alegre": ["cheerful1", "enthusiastic1", "laughing1"],
    "alegria": ["cheerful1", "enthusiastic1", "laughing1"],
    "cheerful1": ["cheerful1"],
    "amor": ["loving1", "grateful1", "cheerful1"],

    "sorprendido": ["surprised1", "surprised2", "amazed1"],
    "sorpresa": ["surprised1", "surprised2", "amazed1"],
    "gasp1": ["surprised1", "surprised2", "amazed1"],
    "asombrado": ["amazed1", "surprised1"],
    "amazed1": ["amazed1"],

    # Antes usaba boredom1 y podía bloquear mucho tiempo.
    # Para "pensando" son mejores thoughtful1/thoughtful2, más cortos.
    "pensando": ["thoughtful1", "thoughtful2", "inquiring1"],
    "pensativo": ["thoughtful1", "thoughtful2", "inquiring1"],
    "thoughtful1": ["thoughtful1"],
    "aburrido": ["boredom1", "boredom2"],
    "boredom1": ["boredom1"],

    "animo": ["yes1", "success1", "cheerful1"],
    "pulgar_arriba": ["yes1", "success1"],
    "asentir": ["yes1"],
    "yes1": ["yes1"],
    "negar": ["no1"],
    "no1": ["no1"],

    "celebracion": ["success1", "success2", "proud1", "cheerful1"],
    "aplauso": ["success1", "success2", "proud1", "cheerful1"],

    "triste": ["sad1", "sad2", "downcast1"],
    "tristeza": ["sad1", "sad2", "downcast1"],
    "sad1": ["sad1"],

    "asco": ["disgusted1", "uncomfortable1"],
    "ansiedad": ["anxiety1", "scared1"],
    "anxiety1": ["anxiety1"],

    "enfadado_suave": ["irritated1", "frustrated1", "furious1"],
    "enojado": ["irritated1", "frustrated1", "furious1"],
    "enojo": ["irritated1", "frustrated1", "furious1"],
    "angry1": ["irritated1", "frustrated1", "furious1"],

    # Compatibilidad: la UI antigua usaba sleepy1, pero el dataset real usa sleep1.
    "sleepy1": ["sleep1"],
    "sleep1": ["sleep1"],
    "dormido": ["sleep1"],
    "calma": ["calming1", "serenity1", "relief1"],
    "calming1": ["calming1"],
    "serenity1": ["serenity1"],

    "curioso": ["curious1", "inquiring1", "inquiring2"],
    "curious1": ["curious1"],
    "juego": ["curious1", "enthusiastic1", "inquiring1"],
    "baile": ["dance1", "dance2", "dance3"],
    "dance1": ["dance1"],
    "dance2": ["dance2"],
    "dance3": ["dance3"],

    "empatia": ["understanding1", "understanding2", "helpful1"],
    "escucha_activa": ["attentive1", "attentive2"],
    "paciencia": ["calming1", "attentive1"],
    "pedir_turno": ["inquiring1", "come1"],
    "repetir": ["inquiring2", "thoughtful1"],
}

def candidates_for(emotion_id: str) -> list[str]:
    base = (emotion_id or "neutral").strip()
    candidates: list[str] = []
    candidates.extend(RECORDED_MOVE_ALIASES.get(base, []))
    candidates.append(base)
    if base.endswith("1"):
        candidates.append(base[:-1])
    else:
        candidates.append(base + "1")
    # Quitar duplicados manteniendo orden.
    seen: set[str] = set()
    out: list[str] = []
    for item in candidates:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


@dataclass
class RecordedMoveResult:
    ok: bool
    requested: str
    executed_id: str | None = None
    audio_path: str | None = None
    elapsed_ms: float = 0.0
    error: str | None = None


class RecordedEmotionLibrary:
    """Carga diferida de la librería de emociones grabadas de Reachy Mini.

    La librería se descarga/cachea usando `reachy_mini.motion.recorded_move.RecordedMoves`.
    Si falla por red, dataset o nombre, el robot puede seguir usando movimientos internos.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.library_id = settings.recorded_moves_library
        self._library: Any | None = None
        self._available: list[str] | None = None
        self.last_error: str | None = None

    def available_moves(self) -> list[str]:
        self._ensure_loaded()
        return self._available or []

    def _ensure_loaded(self) -> None:
        if self._library is not None or self.last_error:
            return
        start = time.perf_counter()
        try:
            from reachy_mini.motion.recorded_move import RecordedMoves  # type: ignore
            self._library = RecordedMoves(self.library_id)
            try:
                self._available = list(self._library.list_moves())
            except Exception:  # noqa: BLE001
                self._available = []
            log_event(
                "recorded_moves_loaded",
                library=self.library_id,
                count=len(self._available),
                elapsed_ms=round((time.perf_counter() - start) * 1000, 2),
            )
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            logger.warning("No se pudo cargar RecordedMoves %s: %s", self.library_id, exc)
            log_event("recorded_moves_load_error", library=self.library_id, error=self.last_error)

    def get_move(self, emotion_id: str) -> tuple[str | None, Any | None, str | None]:
        self._ensure_loaded()
        if self._library is None:
            return None, None, self.last_error or "RecordedMoves no disponible"
        errors: list[str] = []
        for candidate in candidates_for(emotion_id):
            try:
                move = self._library.get(candidate)
                log_event("recorded_move_resolved", requested=emotion_id, executed_id=candidate)
                return candidate, move, None
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{candidate}: {exc}")
        error = "; ".join(errors[-4:]) or "movimiento no encontrado"
        log_event("recorded_move_not_found", requested=emotion_id, candidates=candidates_for(emotion_id), error=error)
        return None, None, error


    def get_recorded_audio_path(self, emotion_id: str) -> tuple[str | None, str | None, str | None]:
        """Devuelve/descarga el WAV oficial de Hugging Face para una emoción.

        Esto evita depender de pygame en el backend. El navegador reproducirá el
        archivo oficial servido por FastAPI, que es mucho más fiable en Windows.
        Devuelve (executed_id, audio_path, error).
        """
        self._ensure_loaded()
        candidates = candidates_for(emotion_id)

        # 1) Si RecordedMoves cargó, usamos sus IDs reales cuando existan.
        if self._available:
            candidates = [c for c in candidates if c in self._available] + [c for c in candidates if c not in self._available]

        # 2) Intentar primero desde el objeto RecordedMoves, porque puede haber
        #    resuelto/cacheado el archivo y conoce la ruta local del audio.
        if self._library is not None:
            for candidate in candidates:
                try:
                    move = self._library.get(candidate)
                    audio_path = getattr(move, "audio_path", None)
                    if audio_path and os.path.exists(str(audio_path)):
                        log_event("recorded_audio_path_from_move", requested=emotion_id, executed_id=candidate, audio_path=str(audio_path))
                        return candidate, str(audio_path), None
                except Exception:
                    pass

        # 3) Fallback robusto: descargar directamente <id>.wav del dataset.
        try:
            from huggingface_hub import hf_hub_download  # type: ignore
        except Exception as exc:  # noqa: BLE001
            error = f"huggingface_hub no disponible: {exc}"
            log_event("recorded_audio_download_unavailable", requested=emotion_id, error=error)
            return None, None, error

        errors: list[str] = []
        for candidate in candidates:
            try:
                path = hf_hub_download(
                    repo_id=self.library_id,
                    repo_type="dataset",
                    filename=f"{candidate}.wav",
                )
                if os.path.exists(path):
                    log_event("recorded_audio_path_downloaded", requested=emotion_id, executed_id=candidate, audio_path=path)
                    return candidate, path, None
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{candidate}.wav: {exc}")
        error = "; ".join(errors[-4:]) or "audio oficial no encontrado"
        log_event("recorded_audio_path_not_found", requested=emotion_id, candidates=candidates, error=error)
        return None, None, error

    def play_recorded_audio_if_available(self, move: Any) -> str | None:
        audio_path = getattr(move, "audio_path", None)
        if not audio_path or not os.path.exists(str(audio_path)):
            log_event("recorded_audio_missing", audio_path=str(audio_path) if audio_path else None)
            return None
        try:
            import pygame  # type: ignore
            if not pygame.mixer.get_init():
                # 44.1 kHz suele funcionar mejor en Windows/Realtek que la init por defecto
                # cuando el dispositivo se abre por primera vez desde FastAPI.
                pygame.mixer.pre_init(44100, -16, 2, 512)
                pygame.mixer.init()
            try:
                sound = pygame.mixer.Sound(str(audio_path))
                channel = sound.play()
                log_event("recorded_audio_started", audio_path=str(audio_path), method="Sound.play", channel=bool(channel))
            except Exception as sound_exc:  # noqa: BLE001
                pygame.mixer.music.load(str(audio_path))
                pygame.mixer.music.play()
                log_event("recorded_audio_started", audio_path=str(audio_path), method="music.play", sound_error=str(sound_exc))
            return str(audio_path)
        except Exception as exc:  # noqa: BLE001
            log_event("recorded_audio_error", audio_path=str(audio_path), error=str(exc))
            return None
