"""Ahootsa profile-local play_emotion tool.

This file DOES NOT modify the original Reachy Mini Conversation App.

v0.4.23:
- Movement still uses the official Reachy Mini RecordedMoves/EmotionQueueMove.
- Sound uses pygame/SDL by default, not reachy_mini.media.play_sound.
- Reason: on some Windows machines, GStreamer/WASAPI raises
  "Failed to write to device" when Reachy Mini media.play_sound is used.

Environment:
- AHOOTSA_EMOTION_AUDIO_BACKEND=pygame  (default)
- AHOOTSA_EMOTION_AUDIO_BACKEND=none    (disable emotion sound)
- AHOOTSA_ALLOW_GSTREAMER_AUDIO=1       (allow fallback to Reachy media.play_sound)
"""

from __future__ import annotations

import json
import logging
import os
import random
import datetime
import unicodedata
import re
import threading
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies

logger = logging.getLogger(__name__)

OFFICIAL_DATASET = "pollen-robotics/reachy-mini-emotions-library"
HF_CACHE_DATASET_DIR = "datasets--pollen-robotics--reachy-mini-emotions-library"
DEFAULT_LOCAL_LIBRARY_DIR = Path(r"D:\RITXI\reachy-mini-emotions-library")

_PYGAME_LOCK = threading.Lock()
_PYGAME_CHANNELS: list[Any] = []


def _log_dir() -> Path:
    base = os.getenv("LOCALAPPDATA") or os.getenv("TEMP") or "."
    d = Path(base) / "Reachy Mini Control" / "ahootsa_logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _log_event(event: str, data: dict[str, Any] | None = None) -> None:
    payload = {
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "event": event,
        "data": data or {},
    }
    try:
        with (_log_dir() / "play_emotion_audio.log").open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


try:
    from reachy_mini.motion.recorded_move import RecordedMoves
    from reachy_mini_conversation_app.dance_emotion_moves import EmotionQueueMove

    EMOTION_AVAILABLE = True
except Exception as exc:  # pragma: no cover - depends on Desktop runtime
    logger.warning("Emotion library not available: %s", exc)
    RecordedMoves = None  # type: ignore[assignment]
    EmotionQueueMove = None  # type: ignore[assignment]
    EMOTION_AVAILABLE = False


EMOTION_INTENTS: tuple[str, ...] = (
    "random",
    "happy",
    "excited",
    "loving",
    "grateful",
    "success",
    "celebration",
    "proud",
    "thinking",
    "attentive",
    "confused",
    "uncertain",
    "sad",
    "downcast",
    "lonely",
    "angry",
    "irritated",
    "displeased",
    "disgusted",
    "scared",
    "anxious",
    "surprised",
    "amazed",
    "calming",
    "relief",
    "impatient",
    "embarrassed",
    "bored",
    "tired",
    "sleepy",
    "yes",
    "yes_understanding",
    "no",
    "no_sad",
    "no_excited",
    "no_firm",
    "welcoming",
    "greeting",
    "goodbye",
    "go_away",
    "helpful",
    "dance",
    "electric",
    "dying",
)

INTENT_TO_MOVES: dict[str, tuple[str, ...]] = {
    "happy": ("laughing2", "laughing1", "cheerful1", "enthusiastic1", "amazed1"),
    "excited": ("dance3", "dance2", "enthusiastic1", "enthusiastic2"),
    "loving": ("loving1",),
    "grateful": ("grateful1",),
    "success": ("success1", "success2", "proud1", "proud2", "grateful1", "yes1"),
    "celebration": ("success1", "success2", "proud1", "proud2", "grateful1", "laughing2", "dance1"),
    "proud": ("proud1", "proud2", "proud3", "success1"),
    "thinking": ("thoughtful1", "thoughtful2", "inquiring1", "inquiring2", "attentive1"),
    "attentive": ("attentive1", "attentive2"),
    "confused": ("confused1", "lost1", "uncertain1", "incomprehensible2"),
    "uncertain": ("uncertain1", "confused1"),
    "sad": ("sad1", "sad2", "downcast1"),
    "downcast": ("downcast1", "sad1"),
    "lonely": ("lonely1",),
    "angry": ("rage1", "irritated2", "irritated1"),
    "irritated": ("irritated1", "irritated2", "displeased2"),
    "displeased": ("displeased1", "displeased2"),
    "disgusted": ("disgusted1",),
    "scared": ("scared1", "fear1", "anxiety1"),
    "anxious": ("anxiety1", "fear1", "scared1"),
    "surprised": ("surprised1", "surprised2", "amazed1"),
    "amazed": ("amazed1", "surprised1"),
    "calming": ("calming1", "serenity1", "relief1", "relief2", "understanding1"),
    "relief": ("relief1", "relief2"),
    "impatient": ("impatient2",),
    "embarrassed": ("shy1",),
    "bored": ("boredom2", "boredom1"),
    "tired": ("exhausted1", "sleep1"),
    "sleepy": ("sleep1", "exhausted1"),
    "yes": ("yes1", "understanding2"),
    "yes_understanding": ("understanding2", "yes1"),
    "no": ("no1",),
    "no_sad": ("no_sad1",),
    "no_excited": ("no_excited1",),
    "no_firm": ("no1",),
    "welcoming": ("welcoming2", "welcoming1", "come1"),
    "greeting": ("welcoming2", "welcoming1", "come1"),
    "goodbye": ("loving1", "welcoming2"),
    "go_away": ("go_away1",),
    "helpful": ("helpful1", "helpful2"),
    "dance": ("dance2", "dance3", "dance1"),
    "electric": ("electric1",),
    "dying": ("dying1",),
}

FALLBACK_MOVES: tuple[str, ...] = (
    "success1", "welcoming2", "welcoming1", "laughing2", "amazed1",
    "yes1", "thoughtful1", "dance1", "dance2", "dance3"
)


def _normalize(value: object) -> str:
    text = str(value or "").strip()
    without_accents = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", without_accents.lower()).strip("_")


def _is_valid_library_dir(path: Path) -> bool:
    try:
        return path.exists() and path.is_dir() and (path / "dance1.json").exists() and (path / "dance1.ogg").exists()
    except Exception:
        return False


def _search_for_dataset_dir() -> Path | None:
    explicit = os.getenv("AHOOTSA_EMOTIONS_LIBRARY_DIR", "").strip()
    if explicit and _is_valid_library_dir(Path(explicit)):
        return Path(explicit)

    explicit2 = os.getenv("REACHY_MINI_EMOTIONS_LIBRARY_DIR", "").strip()
    if explicit2 and _is_valid_library_dir(Path(explicit2)):
        return Path(explicit2)

    if _is_valid_library_dir(DEFAULT_LOCAL_LIBRARY_DIR):
        return DEFAULT_LOCAL_LIBRARY_DIR

    candidates: list[Path] = []
    home = Path.home()
    candidates.append(home / ".cache" / "huggingface" / "hub" / HF_CACHE_DATASET_DIR / "snapshots")

    local = os.getenv("LOCALAPPDATA")
    if local:
        candidates.append(Path(local) / "huggingface" / "hub" / HF_CACHE_DATASET_DIR / "snapshots")
        candidates.append(Path(local) / "Reachy Mini Control")

    for root in candidates:
        try:
            if root.exists():
                hits = sorted(root.rglob("dance1.ogg"), key=lambda p: p.stat().st_mtime, reverse=True)
                for hit in hits:
                    if _is_valid_library_dir(hit.parent):
                        return hit.parent
        except Exception as exc:
            logger.debug("Could not scan %s: %s", root, exc)

    return None


@lru_cache(maxsize=1)
def get_dataset_dir() -> Path | None:
    local = _search_for_dataset_dir()
    if local:
        return local

    try:
        from huggingface_hub import snapshot_download

        path = Path(snapshot_download(repo_id=OFFICIAL_DATASET, repo_type="dataset"))
        if _is_valid_library_dir(path):
            return path
    except Exception as exc:
        logger.warning("Could not snapshot_download official emotion dataset: %s", exc)

    return None


def _patch_recorded_moves_snapshot_download(local_dir: Path) -> None:
    try:
        import reachy_mini.motion.recorded_move as recorded_move_module

        if getattr(recorded_move_module, "_ahootsa_local_snapshot_patch", False):
            return

        original_snapshot_download = recorded_move_module.snapshot_download
        local_str = str(local_dir)
        local_resolved = str(local_dir.resolve())

        def ahootsa_snapshot_download(repo_id: str, *args: Any, **kwargs: Any) -> str:
            value = str(repo_id)
            if value in {OFFICIAL_DATASET, local_str, local_resolved}:
                logger.info("Ahootsa emotion shim: %s -> %s", value, local_resolved)
                return local_resolved
            return original_snapshot_download(repo_id, *args, **kwargs)

        recorded_move_module.snapshot_download = ahootsa_snapshot_download
        recorded_move_module._ahootsa_local_snapshot_patch = True
        recorded_move_module._ahootsa_local_snapshot_dir = local_resolved
    except Exception as exc:
        logger.debug("Could not patch RecordedMoves snapshot_download: %s", exc)


@lru_cache(maxsize=1)
def get_recorded_moves():
    if not EMOTION_AVAILABLE or RecordedMoves is None:
        raise RuntimeError("RecordedMoves is not available")

    dataset_dir = get_dataset_dir()
    if dataset_dir:
        _patch_recorded_moves_snapshot_download(dataset_dir)
    return RecordedMoves(OFFICIAL_DATASET)


@lru_cache(maxsize=1)
def list_moves() -> list[str]:
    try:
        moves = list(get_recorded_moves().list_moves())
        if moves:
            return moves
    except Exception as exc:
        logger.warning("Could not list RecordedMoves: %s", exc)

    dataset_dir = get_dataset_dir()
    if dataset_dir:
        return sorted(p.stem for p in dataset_dir.glob("*.json"))
    return []


def resolve_emotion_name(requested_emotion: object) -> str | None:
    available = set(list_moves())
    if not available:
        return None

    requested = _normalize(requested_emotion)
    if not requested or requested == "random":
        pool = [m for m in FALLBACK_MOVES if m in available] or sorted(available)
        return random.choice(pool)

    if requested in available:
        return requested

    for candidate in INTENT_TO_MOVES.get(requested, ()):
        if candidate in available:
            return candidate

    tokens = set(requested.split("_"))
    if {"no", "sad"}.issubset(tokens):
        for candidate in INTENT_TO_MOVES["no_sad"]:
            if candidate in available:
                return candidate
    if {"no", "excited"}.issubset(tokens):
        for candidate in INTENT_TO_MOVES["no_excited"]:
            if candidate in available:
                return candidate
    if {"yes", "understanding"}.issubset(tokens):
        for candidate in INTENT_TO_MOVES["yes_understanding"]:
            if candidate in available:
                return candidate

    pool = [m for m in FALLBACK_MOVES if m in available] or sorted(available)
    return random.choice(pool)


def _cleanup_finished_channels() -> None:
    try:
        _PYGAME_CHANNELS[:] = [ch for ch in _PYGAME_CHANNELS if ch and ch.get_busy()]
    except Exception:
        _PYGAME_CHANNELS.clear()


def _play_ogg_with_pygame(ogg_path: Path) -> dict[str, Any]:
    """Play OGG through pygame/SDL, bypassing Reachy Mini GStreamer."""
    try:
        import pygame  # type: ignore
    except Exception as exc:
        return {
            "ok": False,
            "backend": "pygame",
            "error": f"pygame not installed or not importable: {type(exc).__name__}: {exc}",
        }

    try:
        with _PYGAME_LOCK:
            if not pygame.mixer.get_init():
                # 48000 Hz is a common Windows/Reachy audio setting.
                pygame.mixer.init(frequency=48000, size=-16, channels=2, buffer=1024)
                pygame.mixer.set_num_channels(8)

            _cleanup_finished_channels()
            sound = pygame.mixer.Sound(str(ogg_path))
            channel = sound.play()
            if channel is None:
                return {
                    "ok": False,
                    "backend": "pygame",
                    "error": "pygame returned no free audio channel",
                    "ogg_path": str(ogg_path),
                }
            _PYGAME_CHANNELS.append(channel)

        return {
            "ok": True,
            "backend": "pygame",
            "ogg_path": str(ogg_path),
            "mixer_init": str(pygame.mixer.get_init()),
        }
    except Exception as exc:
        return {
            "ok": False,
            "backend": "pygame",
            "error": f"{type(exc).__name__}: {exc}",
            "ogg_path": str(ogg_path),
        }


def _play_ogg_with_reachy_gstreamer(deps: ToolDependencies, ogg_path: Path) -> dict[str, Any]:
    """Optional fallback. Disabled by default because it triggers GstWasapi2Sink on some Windows PCs."""
    if os.getenv("AHOOTSA_ALLOW_GSTREAMER_AUDIO", "").strip() != "1":
        return {"ok": False, "backend": "gstreamer", "skipped": True, "reason": "disabled by default"}

    try:
        media = getattr(getattr(deps, "reachy_mini", None), "media", None)
        play_sound = getattr(media, "play_sound", None)
        if not callable(play_sound):
            return {"ok": False, "backend": "gstreamer", "error": "deps.reachy_mini.media.play_sound not available"}

        play_sound(str(ogg_path))
        return {"ok": True, "backend": "gstreamer", "ogg_path": str(ogg_path)}
    except Exception as exc:
        return {"ok": False, "backend": "gstreamer", "error": f"{type(exc).__name__}: {exc}", "ogg_path": str(ogg_path)}


def _play_ogg(deps: ToolDependencies, move_name: str) -> dict[str, Any]:
    dataset_dir = get_dataset_dir()
    if not dataset_dir:
        return {"ok": False, "error": "official dataset dir not found"}

    ogg_path = dataset_dir / f"{move_name}.ogg"
    if not ogg_path.exists():
        return {"ok": False, "error": "ogg file not found", "ogg_path": str(ogg_path)}

    backend = os.getenv("AHOOTSA_EMOTION_AUDIO_BACKEND", "pygame").strip().lower()
    if backend in {"none", "off", "disabled"}:
        return {"ok": False, "backend": "none", "skipped": True, "ogg_path": str(ogg_path)}

    if backend in {"pygame", "sdl", ""}:
        result = _play_ogg_with_pygame(ogg_path)
        if result.get("ok"):
            return result
        # If user explicitly enabled GStreamer fallback, try it.
        gst_result = _play_ogg_with_reachy_gstreamer(deps, ogg_path)
        return {"ok": False, "primary": result, "fallback": gst_result, "ogg_path": str(ogg_path)}

    if backend in {"gstreamer", "reachy"}:
        return _play_ogg_with_reachy_gstreamer(deps, ogg_path)

    return {"ok": False, "error": f"unknown backend {backend!r}", "ogg_path": str(ogg_path)}


def _queue_motion(deps: ToolDependencies, move_name: str) -> dict[str, Any]:
    if not EMOTION_AVAILABLE or EmotionQueueMove is None:
        return {"ok": False, "error": "EmotionQueueMove not available"}

    try:
        library = get_recorded_moves()
        deps.movement_manager.queue_move(EmotionQueueMove(move_name, library))
        return {"ok": True, "mode": "EmotionQueueMove"}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


class PlayEmotion(Tool):
    """Play an official robot emotion with movement and matching official OGG sound."""

    name = "play_emotion"
    description = (
        "Play a robot emotion with movement and sound. "
        "Uses official Reachy Mini recorded movements and official OGG audio. "
        "In Ahootsa v0.4.23 the audio uses pygame/SDL by default to avoid GStreamer/WASAPI errors on Windows."
    )
    needs_response = False

    parameters_schema = {
        "type": "object",
        "properties": {
            "emotion": {
                "type": "string",
                "enum": list(EMOTION_INTENTS),
                "description": "Emotional intent or official move name. Use success, greeting, happy, thinking, confused, calming, dance, etc.",
            },
            "sound": {
                "type": "boolean",
                "description": "Whether to play the matching official OGG sound. Default true.",
                "default": True,
            },
        },
        "required": [],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> Dict[str, Any]:
        requested_emotion = kwargs.get("emotion", "random")
        sound_enabled = bool(kwargs.get("sound", True))

        _log_event("call_start", {"requested_emotion": requested_emotion, "sound": sound_enabled})

        if not EMOTION_AVAILABLE:
            result = {"error": "Emotion system not available"}
            _log_event("call_error", result)
            return result

        move_name = resolve_emotion_name(requested_emotion)
        if not move_name:
            result = {"error": "No emotions currently available"}
            _log_event("call_error", result)
            return result

        # Queue motion first so movement starts immediately.
        motion_result = _queue_motion(deps, move_name)
        audio_result = _play_ogg(deps, move_name) if sound_enabled else {"ok": False, "skipped": True}

        result: Dict[str, Any] = {
            "status": "queued",
            "emotion": move_name,
            "requested_emotion": requested_emotion,
            "motion": motion_result,
            "audio": audio_result,
            "dataset_dir": str(get_dataset_dir()) if get_dataset_dir() else None,
            "message_for_user": (
                "He reproducido la emoción con movimiento y sonido."
                if audio_result.get("ok")
                else "He reproducido el movimiento de la emoción, pero el sonido no ha podido reproducirse."
            ),
        }
        _log_event("call_result", result)
        return result
