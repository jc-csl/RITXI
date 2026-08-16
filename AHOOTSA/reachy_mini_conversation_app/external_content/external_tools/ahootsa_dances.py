"""Ahootsa local dance tools for the activity "Vamos a bailar".

Version 1.5 keeps the shared-audio and microphone-preservation fixes, prevents duplicate restarts, and
waits for the selected dance to finish before returning its tool result. This
allows the realtime conversation to produce a short spoken continuation when
the music and movement end naturally.

This module exposes:

- play_ahootsa_dance
- stop_ahootsa_dance

Movement JSON and audio files are loaded from:

    external_content/activities/vamos_a_bailar/

Audio is decoded with PyAV and pushed into the existing Reachy Mini playback
appsrc. No second WASAPI sink is opened and the microphone pipeline is never
stopped.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import threading
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import av
import numpy as np
from reachy_mini.motion.recorded_move import RecordedMove
from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies


logger = logging.getLogger(__name__)

AHOOTSA_DANCES_VERSION = "1.5"

TOOLS_DIRECTORY = Path(__file__).resolve().parent
EXTERNAL_CONTENT_DIRECTORY = TOOLS_DIRECTORY.parent
ACTIVITY_DIRECTORY = (
    EXTERNAL_CONTENT_DIRECTORY
    / "activities"
    / "vamos_a_bailar"
)
CATALOG_PATH = ACTIVITY_DIRECTORY / "catalogo_bailes.json"

DANCE_IDS: tuple[str, ...] = (
    "dance1",
    "dance2",
    "dance3",
    "las-ketchup",
    "michael-jackson-thriller",
    "spice-girls",
    "pharrell-williams-happy",
    "queen-we-will-rock-you",
    "the-white-stripes-seven-nation-army",
    "bohemian-rhapsody",
    "happy-birthday",
    "harry-potter",
    "star-wars",
    "the-lion-king",
    "titanic",
    "secret-dance",
)


@dataclass
class _ActiveDance:
    """In-memory state for the current local dance."""

    dance_id: str
    name: str
    started_at: float
    duration_seconds: float
    audio_path: str
    generation: int


@dataclass
class _AudioWorker:
    """Background PCM streamer using the existing Reachy playback appsrc."""

    generation: int
    stop_event: threading.Event
    thread: threading.Thread


_STATE_LOCK = threading.RLock()
_ACTIVE_DANCE: Optional[_ActiveDance] = None
_AUDIO_WORKER: Optional[_AudioWorker] = None
_CLEAR_TIMER: Optional[threading.Timer] = None
_GENERATION = 0


def _normalize(value: object) -> str:
    """Normalize a spoken or written dance name for matching."""
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _load_catalog() -> list[dict[str, Any]]:
    """Load and validate the Phase 5 local dance catalog."""
    if not CATALOG_PATH.is_file():
        raise FileNotFoundError(
            f"No existe el catálogo local de bailes: {CATALOG_PATH}"
        )

    try:
        document = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"El catálogo local no contiene JSON válido: {exc}"
        ) from exc

    moves = document.get("moves")
    if not isinstance(moves, list):
        raise ValueError("El catálogo local no contiene una lista 'moves'.")

    enabled_moves = [
        move
        for move in moves
        if isinstance(move, dict) and bool(move.get("enabled", True))
    ]
    enabled_moves.sort(key=lambda move: int(move.get("order", 9999)))

    found_ids = {
        str(move.get("id", "")).strip()
        for move in enabled_moves
    }
    missing = [dance_id for dance_id in DANCE_IDS if dance_id not in found_ids]
    if missing:
        raise ValueError(
            "Faltan movimientos seleccionados en el catálogo: "
            + ", ".join(missing)
        )

    return enabled_moves


def _catalog_index() -> dict[str, dict[str, Any]]:
    """Return the active catalog indexed by canonical dance ID."""
    return {
        str(move["id"]): move
        for move in _load_catalog()
    }


def _resolve_dance_id(requested: object) -> Optional[str]:
    """Resolve a canonical ID, display name or configured spoken alias."""
    requested_text = str(requested or "").strip()
    if not requested_text:
        return None

    catalog = _load_catalog()
    by_id = {str(move["id"]): move for move in catalog}

    if requested_text in by_id:
        return requested_text

    normalized_requested = _normalize(requested_text)
    for move in catalog:
        candidates = [
            move.get("id", ""),
            move.get("name", ""),
            move.get("short_name", ""),
            *(move.get("aliases") or []),
        ]
        if normalized_requested in {
            _normalize(candidate)
            for candidate in candidates
            if candidate
        }:
            return str(move["id"])

    return None


def _resource_path(move: dict[str, Any], field: str) -> Path:
    """Resolve and validate one resource path declared in the catalog."""
    raw_path = str(move.get(field, "")).strip()
    if not raw_path:
        raise ValueError(
            f"El movimiento {move.get('id')!r} no define {field}."
        )

    path = (ACTIVITY_DIRECTORY / raw_path).resolve()

    try:
        path.relative_to(ACTIVITY_DIRECTORY.resolve())
    except ValueError as exc:
        raise ValueError(
            f"Ruta no permitida para {move.get('id')!r}: {path}"
        ) from exc

    if not path.is_file():
        raise FileNotFoundError(
            f"No existe el recurso local de {move.get('id')!r}: {path}"
        )

    return path


def _build_recorded_move(move: dict[str, Any]) -> tuple[RecordedMove, Path]:
    """Construct the official SDK RecordedMove from local JSON and audio."""
    movement_path = _resource_path(move, "local_json")
    audio_path = _resource_path(move, "local_audio")

    try:
        movement_data = json.loads(
            movement_path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Movimiento JSON no válido: {movement_path}: {exc}"
        ) from exc

    recorded_move = RecordedMove(
        movement_data,
        sound_path=audio_path,
    )

    if float(recorded_move.duration) <= 0:
        raise ValueError(
            f"Duración no válida para {move.get('id')!r}."
        )

    return recorded_move, audio_path


def _decode_audio_to_pcm(
    audio_path: Path,
    sample_rate: int,
    channels: int,
) -> np.ndarray:
    """Decode a local audio file to contiguous float32 PCM.

    PyAV is already a dependency of the official conversation app.
    """
    if sample_rate <= 0:
        sample_rate = 16_000

    if channels not in (1, 2):
        channels = 2

    layout = "mono" if channels == 1 else "stereo"
    resampler = av.AudioResampler(
        format="fltp",
        layout=layout,
        rate=sample_rate,
    )

    pcm_parts: list[np.ndarray] = []

    with av.open(str(audio_path)) as container:
        audio_streams = list(container.streams.audio)
        if not audio_streams:
            raise ValueError(
                f"El archivo no contiene una pista de audio: {audio_path}"
            )

        stream = audio_streams[0]

        for frame in container.decode(stream):
            for output_frame in resampler.resample(frame):
                array = output_frame.to_ndarray()

                # fltp is planar: (channels, samples).
                if array.ndim == 2:
                    array = array.T
                elif array.ndim == 1:
                    array = array.reshape(-1, 1)
                else:
                    raise ValueError(
                        f"Formato PCM inesperado: shape={array.shape}"
                    )

                pcm_parts.append(
                    np.ascontiguousarray(
                        array,
                        dtype=np.float32,
                    )
                )

        for output_frame in resampler.resample(None):
            array = output_frame.to_ndarray()
            if array.ndim == 2:
                array = array.T
            elif array.ndim == 1:
                array = array.reshape(-1, 1)

            pcm_parts.append(
                np.ascontiguousarray(
                    array,
                    dtype=np.float32,
                )
            )

    if not pcm_parts:
        raise ValueError(
            f"No se ha podido decodificar audio PCM: {audio_path}"
        )

    pcm = np.concatenate(pcm_parts, axis=0)

    if pcm.shape[1] != channels:
        raise ValueError(
            f"Canales PCM inesperados: {pcm.shape[1]} != {channels}"
        )

    np.clip(pcm, -1.0, 1.0, out=pcm)
    return np.ascontiguousarray(pcm, dtype=np.float32)


def _clear_player_without_stopping_microphone(media: Any) -> bool:
    """Flush output audio while leaving the recording pipeline alive."""
    audio = getattr(media, "audio", None)
    clear_player = getattr(audio, "clear_player", None)

    if not callable(clear_player):
        logger.warning(
            "Audio backend has no clear_player(); output queue was not flushed"
        )
        return False

    clear_player()
    return True


def _stream_pcm_worker(
    media: Any,
    pcm: np.ndarray,
    sample_rate: int,
    stop_event: threading.Event,
    generation: int,
) -> None:
    """Push dance PCM through the existing conversation appsrc in real time."""
    chunk_frames = max(320, int(sample_rate * 0.05))  # 50 ms
    total_frames = int(pcm.shape[0])
    next_deadline = time.monotonic()

    logger.info(
        "Ahootsa shared audio worker started: generation=%d "
        "frames=%d sample_rate=%d channels=%d",
        generation,
        total_frames,
        sample_rate,
        int(pcm.shape[1]),
    )

    try:
        for offset in range(0, total_frames, chunk_frames):
            if stop_event.is_set():
                break

            end = min(offset + chunk_frames, total_frames)
            chunk = np.ascontiguousarray(
                pcm[offset:end],
                dtype=np.float32,
            )
            media.push_audio_sample(chunk)

            next_deadline += (end - offset) / sample_rate
            wait_seconds = max(0.0, next_deadline - time.monotonic())

            if stop_event.wait(wait_seconds):
                break
    except Exception:
        logger.exception(
            "Ahootsa shared audio worker failed: generation=%d",
            generation,
        )
    finally:
        logger.info(
            "Ahootsa shared audio worker finished: generation=%d stopped=%s",
            generation,
            stop_event.is_set(),
        )


def _cancel_clear_timer_locked() -> None:
    """Cancel the state-cleanup timer. Caller must hold _STATE_LOCK."""
    global _CLEAR_TIMER

    if _CLEAR_TIMER is not None:
        _CLEAR_TIMER.cancel()
        _CLEAR_TIMER = None


def _clear_state_if_generation(generation: int) -> None:
    """Clear completed dance state without affecting a newer dance."""
    global _ACTIVE_DANCE, _AUDIO_WORKER, _CLEAR_TIMER

    with _STATE_LOCK:
        if (
            _ACTIVE_DANCE is not None
            and _ACTIVE_DANCE.generation == generation
        ):
            logger.info(
                "Ahootsa local dance completed: dance_id=%s",
                _ACTIVE_DANCE.dance_id,
            )
            _ACTIVE_DANCE = None

        if (
            _AUDIO_WORKER is not None
            and _AUDIO_WORKER.generation == generation
        ):
            _AUDIO_WORKER = None

        _CLEAR_TIMER = None


def _schedule_state_cleanup_locked(
    duration_seconds: float,
    generation: int,
) -> None:
    """Schedule state cleanup shortly after the longest media duration."""
    global _CLEAR_TIMER

    _cancel_clear_timer_locked()

    timer = threading.Timer(
        max(0.1, float(duration_seconds) + 0.75),
        _clear_state_if_generation,
        args=(generation,),
    )
    timer.daemon = True
    _CLEAR_TIMER = timer
    timer.start()


def _finish_active_dance_if_generation(
    deps: ToolDependencies,
    generation: int,
) -> Optional[_ActiveDance]:
    """Finish one dance safely without clearing a newer replacement."""
    global _ACTIVE_DANCE, _AUDIO_WORKER, _GENERATION

    with _STATE_LOCK:
        if (
            _ACTIVE_DANCE is None
            or _ACTIVE_DANCE.generation != generation
        ):
            return None

        completed = _ACTIVE_DANCE
        worker = _AUDIO_WORKER

        _GENERATION += 1
        _cancel_clear_timer_locked()
        _ACTIVE_DANCE = None
        _AUDIO_WORKER = None

        if (
            worker is not None
            and worker.generation == generation
        ):
            worker.stop_event.set()
        else:
            worker = None

    if worker is not None and worker.thread.is_alive():
        worker.thread.join(timeout=0.75)

    deps.movement_manager.clear_move_queue()

    try:
        _clear_player_without_stopping_microphone(
            deps.reachy_mini.media
        )
    except Exception:
        logger.exception(
            "Failed to flush completed Ahootsa dance audio queue"
        )

    logger.info(
        "Ahootsa local dance completed and auto-stopped: "
        "dance_id=%s name=%s audio_mode=shared_appsrc "
        "microphone_preserved=true",
        completed.dance_id,
        completed.name,
    )
    return completed


def _get_running_same_dance(
    dance_id: str,
) -> Optional[Dict[str, Any]]:
    """Return current state when the same dance is already running."""
    with _STATE_LOCK:
        active = _ACTIVE_DANCE

        if active is None or active.dance_id != dance_id:
            return None

        elapsed = max(
            0.0,
            time.monotonic() - active.started_at,
        )
        remaining = max(
            0.0,
            active.duration_seconds - elapsed,
        )

        if remaining <= 0.15:
            return None

        return {
            "dance_id": active.dance_id,
            "name": active.name,
            "generation": active.generation,
            "elapsed_seconds": round(elapsed, 3),
            "remaining_seconds": round(remaining, 3),
        }


def _stop_active_dance(
    deps: ToolDependencies,
) -> Optional[_ActiveDance]:
    """Stop movement and audio without stopping microphone input."""
    global _ACTIVE_DANCE, _AUDIO_WORKER, _GENERATION

    with _STATE_LOCK:
        previous = _ACTIVE_DANCE
        worker = _AUDIO_WORKER

        _GENERATION += 1
        _cancel_clear_timer_locked()
        _ACTIVE_DANCE = None
        _AUDIO_WORKER = None

        if worker is not None:
            worker.stop_event.set()

    if worker is not None and worker.thread.is_alive():
        worker.thread.join(timeout=0.75)

    deps.movement_manager.clear_move_queue()

    try:
        _clear_player_without_stopping_microphone(
            deps.reachy_mini.media
        )
    except Exception:
        logger.exception(
            "Failed to flush Ahootsa shared audio queue"
        )

    if previous is not None:
        logger.info(
            "Ahootsa local dance stopped: dance_id=%s name=%s "
            "audio_mode=shared_appsrc microphone_preserved=true",
            previous.dance_id,
            previous.name,
        )
    else:
        logger.info(
            "Ahootsa stop requested with no active local dance "
            "audio_mode=shared_appsrc microphone_preserved=true"
        )

    return previous


class PlayAhootsaDance(Tool):
    """Play one selected local movement and its associated audio."""

    name = "play_ahootsa_dance"
    description = (
        "IMMEDIATE ACTION TOOL. When the user clearly selects a dance, call "
        "this tool in that same response before saying 'Vamos a bailar'. "
        "Never speak only a promise and defer the tool call to a later user "
        "turn. Call exactly once for each clear selection. A complaint about "
        "delay, counting, a brief sound, or another utterance while a dance "
        "is starting is not a new request and must not trigger a duplicate "
        "call. Play one dance from Ahootsa's local catalog after the user "
        "clearly chooses it. The complete available catalogue is: "
        "Baile 1=dance1; "
        "Baile 2=dance2; Baile 3=dance3; Las Ketchup or Asereje=las-ketchup; "
        "Michael Jackson Thriller or Thriller=michael-jackson-thriller; "
        "Spice Girls=spice-girls; Pharrell Williams Happy or Happy="
        "pharrell-williams-happy; Queen We Will Rock You="
        "queen-we-will-rock-you; The White Stripes Seven Nation Army="
        "the-white-stripes-seven-nation-army; Queen Bohemian Rhapsody="
        "bohemian-rhapsody; Cumpleaños feliz or Happy Birthday=happy-birthday; "
        "Harry Potter=harry-potter; Star Wars=star-wars; El rey leon or "
        "The Lion King=the-lion-king; Titanic=titanic; Baile secreto or "
        "Secret Dance=secret-dance. When the user asks what dances are "
        "available, answer verbally from this catalogue without calling a "
        "listing tool. Do not start a dance automatically or because of "
        "inactivity. Never call this tool again for the same dance while it "
        "is already starting or running. This tool remains active until the "
        "selected dance ends. When it returns status completed, continue the "
        "conversation with one brief positive sentence and one simple "
        "question."
    )
    needs_response = True
    parameters_schema = {
        "type": "object",
        "properties": {
            "dance_id": {
                "type": "string",
                "enum": list(DANCE_IDS),
                "description": (
                    "Canonical dance identifier selected by the user."
                ),
            },
        },
        "required": ["dance_id"],
        "additionalProperties": False,
    }

    async def __call__(
        self,
        deps: ToolDependencies,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Start the selected dance using the existing conversation audio sink."""
        global _ACTIVE_DANCE, _AUDIO_WORKER, _GENERATION

        requested = kwargs.get("dance_id")
        resolved_id = _resolve_dance_id(requested)

        logger.info(
            "Tool call: play_ahootsa_dance requested=%s resolved=%s",
            requested,
            resolved_id,
        )

        if resolved_id is None:
            return {
                "status": "error",
                "error": (
                    f"Baile desconocido: {requested!r}. "
                    f"Disponibles: {list(DANCE_IDS)}"
                ),
            }

        running_same_dance = await asyncio.to_thread(
            _get_running_same_dance,
            resolved_id,
        )

        if running_same_dance is not None:
            logger.warning(
                "Duplicate Ahootsa dance request ignored: "
                "dance_id=%s generation=%s remaining=%.3f",
                running_same_dance["dance_id"],
                running_same_dance["generation"],
                running_same_dance["remaining_seconds"],
            )
            return {
                "status": "already_running",
                "activity": "vamos_a_bailar",
                "dance_id": running_same_dance["dance_id"],
                "name": running_same_dance["name"],
                "remaining_seconds": running_same_dance[
                    "remaining_seconds"
                ],
                "duplicate_ignored": True,
                "restarted": False,
                "audio_mode": "shared_appsrc",
                "microphone_preserved": True,
                "follow_up_instruction": (
                    "No reinicies el baile. No digas que ha terminado. "
                    "El mismo baile ya está en marcha."
                ),
            }

        media = deps.reachy_mini.media
        sample_rate = int(media.get_output_audio_samplerate())
        channels = int(media.get_output_channels())

        try:
            move = _catalog_index()[resolved_id]
            recorded_move, audio_path = await asyncio.to_thread(
                _build_recorded_move,
                move,
            )
            pcm = await asyncio.to_thread(
                _decode_audio_to_pcm,
                audio_path,
                sample_rate,
                channels,
            )
        except Exception as exc:
            logger.exception(
                "Failed to prepare Ahootsa dance: %s",
                resolved_id,
            )
            return {
                "status": "error",
                "dance_id": resolved_id,
                "error": str(exc),
            }

        previous = await asyncio.to_thread(
            _stop_active_dance,
            deps,
        )
        replaced_previous = previous is not None

        audio_duration = float(pcm.shape[0]) / float(sample_rate)
        movement_duration = float(recorded_move.duration)
        activity_duration = max(audio_duration, movement_duration)

        with _STATE_LOCK:
            _GENERATION += 1
            generation = _GENERATION

            _clear_player_without_stopping_microphone(media)
            deps.movement_manager.queue_move(recorded_move)

            stop_event = threading.Event()
            thread = threading.Thread(
                target=_stream_pcm_worker,
                args=(
                    media,
                    pcm,
                    sample_rate,
                    stop_event,
                    generation,
                ),
                daemon=True,
                name=f"ahootsa-dance-audio-{generation}",
            )

            active = _ActiveDance(
                dance_id=resolved_id,
                name=str(
                    move.get("name")
                    or move.get("short_name")
                    or resolved_id
                ),
                started_at=time.monotonic(),
                duration_seconds=activity_duration,
                audio_path=str(audio_path),
                generation=generation,
            )
            worker = _AudioWorker(
                generation=generation,
                stop_event=stop_event,
                thread=thread,
            )

            _ACTIVE_DANCE = active
            _AUDIO_WORKER = worker
            # Fallback cleanup only. The normal path below performs a
            # generation-safe stop and then returns a result to the model.
            _schedule_state_cleanup_locked(
                activity_duration + 5.0,
                generation,
            )
            thread.start()

        logger.info(
            "Ahootsa local dance started: dance_id=%s name=%s "
            "movement_duration=%.3f audio_duration=%.3f audio=%s "
            "replaced_previous=%s audio_mode=shared_appsrc "
            "microphone_preserved=true",
            active.dance_id,
            active.name,
            movement_duration,
            audio_duration,
            active.audio_path,
            replaced_previous,
        )

        stopped_early = await asyncio.to_thread(
            stop_event.wait,
            active.duration_seconds + 0.75,
        )

        if stopped_early:
            with _STATE_LOCK:
                current = _ACTIVE_DANCE
                replaced_by_newer = (
                    current is not None
                    and current.generation != generation
                )

            if replaced_by_newer:
                logger.info(
                    "Ahootsa dance replaced before completion: "
                    "dance_id=%s generation=%d",
                    active.dance_id,
                    generation,
                )
                return {
                    "status": "replaced",
                    "activity": "vamos_a_bailar",
                    "dance_id": active.dance_id,
                    "name": active.name,
                    "follow_up_instruction": (
                        "No hables ahora: ya ha empezado otro baile."
                    ),
                }

            logger.info(
                "Ahootsa dance stopped before natural completion: "
                "dance_id=%s generation=%d",
                active.dance_id,
                generation,
            )
            return {
                "status": "stopped",
                "activity": "vamos_a_bailar",
                "dance_id": active.dance_id,
                "name": active.name,
                "audio_mode": "shared_appsrc",
                "microphone_preserved": True,
                "follow_up_instruction": (
                    "Retoma la conversación con una frase muy breve "
                    "y una sola pregunta sencilla."
                ),
            }

        completed = await asyncio.to_thread(
            _finish_active_dance_if_generation,
            deps,
            generation,
        )

        if completed is None:
            logger.info(
                "Ahootsa dance completion ignored because a newer "
                "dance is active: dance_id=%s generation=%d",
                active.dance_id,
                generation,
            )
            return {
                "status": "replaced",
                "activity": "vamos_a_bailar",
                "dance_id": active.dance_id,
                "name": active.name,
                "follow_up_instruction": (
                    "No hables ahora: ya ha empezado otro baile."
                ),
            }

        return {
            "status": "completed",
            "activity": "vamos_a_bailar",
            "dance_id": completed.dance_id,
            "name": completed.name,
            "duration_seconds": round(
                completed.duration_seconds,
                3,
            ),
            "movement_duration_seconds": round(
                movement_duration,
                3,
            ),
            "audio_duration_seconds": round(
                audio_duration,
                3,
            ),
            "audio": True,
            "audio_mode": "shared_appsrc",
            "microphone_preserved": True,
            "replaced_previous": replaced_previous,
            "auto_stopped": True,
            "follow_up_instruction": (
                "El baile ya ha terminado. Di una frase breve como "
                "'Ya hemos terminado el baile' y haz una sola "
                "pregunta sencilla para continuar, por ejemplo si le "
                "ha gustado o qué le apetece hacer ahora."
            ),
        }


class StopAhootsaDance(Tool):
    """Stop the current local dance and its audio immediately."""

    name = "stop_ahootsa_dance"
    description = (
        "Immediately stop Ahootsa's current local dance and its music. "
        "Before calling this tool, say a very short confirmation such as "
        "'Vale, lo paro'. Then call it without asking a question. Use it when "
        "the user says para, basta, detén el baile, stop, or an equivalent "
        "request."
    )
    needs_response = False
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }

    async def __call__(
        self,
        deps: ToolDependencies,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Stop dance audio while preserving the listening pipeline."""
        del kwargs

        logger.info("Tool call: stop_ahootsa_dance")
        previous = await asyncio.to_thread(
            _stop_active_dance,
            deps,
        )

        if previous is None:
            return {
                "status": "idle",
                "message": "No había ningún baile local activo.",
                "audio_mode": "shared_appsrc",
                "microphone_preserved": True,
            }

        return {
            "status": "stopped",
            "activity": "vamos_a_bailar",
            "previous_dance_id": previous.dance_id,
            "previous_name": previous.name,
            "audio_mode": "shared_appsrc",
            "microphone_preserved": True,
        }
