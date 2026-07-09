"""Ahootsa profile-local play_emotion tool.

0.4.57.2:
- Reads delay/audio configuration from play_timing_config.json.
- Supports delay_before_play_seconds parameter.
- Keeps AHOOTSA_ACTION_PLAY_DELAY_SECONDS environment variable for runtime override.

This file does not modify the original Reachy Mini Conversation App.
"""

from __future__ import annotations

import asyncio
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

def _load_debug_logger():
    try:
        import ahootsa_debug_logger  # type: ignore
        return ahootsa_debug_logger
    except Exception:
        try:
            import importlib.util
            import sys
            from pathlib import Path
            path = Path(__file__).resolve().with_name("ahootsa_debug_logger.py")
            name = "ahootsa_debug_logger_runtime"
            if name in sys.modules:
                return sys.modules[name]
            spec = importlib.util.spec_from_file_location(name, path)
            if not (spec and spec.loader):
                return None
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
            return mod
        except Exception:
            return None


def _log_tool_start(tool_name: str, kwargs: dict | None = None) -> None:
    mod = _load_debug_logger()
    if mod:
        mod.log_tool_start(tool_name, kwargs or {})


def _log_tool_result(tool_name: str, result) -> None:
    mod = _load_debug_logger()
    if mod:
        mod.log_tool_result(tool_name, result)


def _log_tool_exception(tool_name: str, exc: BaseException, data: dict | None = None) -> None:
    mod = _load_debug_logger()
    if mod:
        mod.log_exception("tool_exception", exc, data or {}, tool=tool_name)



def _load_play_timing_config() -> dict[str, Any]:
    try:
        path = Path(__file__).resolve().with_name("play_timing_config.json")
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _ahootsa_emotion_audio_disabled() -> bool:
    try:
        env_value = os.getenv("AHOOTSA_DISABLE_EMOTION_AUDIO")
        if env_value is not None and env_value.strip() != "":
            return env_value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(_load_play_timing_config().get("disable_emotion_audio", False))
    except Exception:
        return False


def _ahootsa_action_delay_seconds(kwargs: dict[str, Any] | None = None) -> float:
    """Optional pre-play delay. In 0.4.57.2 the default is 0."""
    kwargs = kwargs or {}
    raw = kwargs.get("delay_before_play_seconds")
    if raw is None:
        raw = os.getenv("AHOOTSA_ACTION_PLAY_DELAY_SECONDS")
    if raw is None or str(raw).strip() == "":
        raw = _load_play_timing_config().get("action_play_delay_seconds", 0.0)
    try:
        value = float(raw)
    except Exception:
        value = 0.0
    return max(0.0, min(10.0, value))


def _ahootsa_post_play_wait_seconds(kwargs: dict[str, Any] | None = None) -> float:
    """Wait after starting movement/audio, so the final spoken response does not overlap."""
    kwargs = kwargs or {}
    raw = kwargs.get("post_play_wait_seconds")
    if raw is None:
        raw = os.getenv("AHOOTSA_POST_PLAY_WAIT_SECONDS")
    if raw is None or str(raw).strip() == "":
        raw = _load_play_timing_config().get("post_play_wait_seconds", 3.0)
    try:
        value = float(raw)
    except Exception:
        value = 3.0
    return max(0.0, min(20.0, value))






OFFICIAL_DATASET = "pollen-robotics/reachy-mini-emotions-library"
HF_CACHE_DATASET_DIR = "datasets--pollen-robotics--reachy-mini-emotions-library"
DEFAULT_LOCAL_LIBRARY_DIR = Path(r"D:\RITXI\reachy-mini-emotions-library")

_PYGAME_LOCK = threading.Lock()
_PYGAME_CHANNELS: list[Any] = []
_PYGAME_SOUND_REFS: list[Any] = []


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


def _repair_mojibake(text: str) -> str:
    """Repair common UTF-8 mojibake produced by Windows consoles/STT traces.

    Examples: "elÃ©ctrico" -> "eléctrico", "nÃºmero" -> "número".
    If repair is not possible, return the original text.
    """
    if not isinstance(text, str):
        text = str(text or "")
    for enc in ("latin-1", "cp1252"):
        try:
            repaired = text.encode(enc, errors="strict").decode("utf-8", errors="strict")
            if repaired and repaired != text:
                return repaired
        except Exception:
            pass
    return text


def _normalize(value: object) -> str:
    text = _repair_mojibake(str(value or "").strip())
    without_accents = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", without_accents.lower()).strip("_")



@lru_cache(maxsize=1)
def _spanish_resource_maps() -> dict[str, dict[str, str]]:
    """Load Spanish aliases/display names for emotions and small dances."""
    alias_to_technical: dict[str, str] = {}
    display_names: dict[str, str] = {}

    def add_alias(alias: object, technical: object) -> None:
        if alias and technical:
            alias_to_technical[_normalize(alias)] = str(technical)

    try:
        root = Path(__file__).resolve().parents[2]
        tools_dir = root / "tools"
        res_path = tools_dir / "resources_bailes_emociones_es.json"
        if res_path.exists():
            data = json.loads(res_path.read_text(encoding="utf-8"))
            for alias, technical in data.get("emotion_aliases", {}).items():
                add_alias(alias, technical)
            for technical, label in data.get("display_names", {}).items():
                display_names[str(technical)] = str(label)
                add_alias(label, technical)
        cat_path = tools_dir / "emotions_catalog_es.json"
        if cat_path.exists():
            cat = json.loads(cat_path.read_text(encoding="utf-8"))
            for item in cat.get("emotions", []):
                technical = item.get("technical_id") or item.get("id")
                if not technical:
                    continue
                display_names.setdefault(str(technical), str(item.get("name_es") or technical))
                add_alias(item.get("id"), technical)
                add_alias(item.get("name_es"), technical)
                add_alias(technical, technical)
                for alias in item.get("aliases", []) or []:
                    add_alias(alias, technical)
                for example in item.get("example_user_requests", []) or []:
                    add_alias(example, technical)
    except Exception:
        pass
    builtin = {
        "baile": "dance1", "baila": "dance1", "danza": "dance1", "fiesta": "dance1", "play": "dance1", "olay": "dance1", "ole": "dance1", "olé": "dance1",
        "baile uno": "dance1", "baile 1": "dance1", "primer baile": "dance1", "baile alegre": "dance1", "baile alegre uno": "dance1",
        "baile dos": "dance2", "baile 2": "dance2", "play dos": "dance2", "olay dos": "dance2", "ole dos": "dance2", "segundo baile": "dance2", "baile animado": "dance2", "baile animado dos": "dance2",
        "baile numero dos": "dance2", "baile número dos": "dance2", "baile nÃºmero dos": "dance2", "baile n2": "dance2", "numero dos": "dance2", "número dos": "dance2", "dos": "dance2",
        "baile tres": "dance3", "baile 3": "dance3", "play tres": "dance3", "olay tres": "dance3", "ole tres": "dance3", "tercer baile": "dance3", "baile energia": "dance3", "baile energía": "dance3", "baile con energia": "dance3", "baile con energía": "dance3",
        "baile numero tres": "dance3", "baile número tres": "dance3", "baile nÃºmero tres": "dance3", "baile n3": "dance3", "numero tres": "dance3", "número tres": "dance3", "tres": "dance3",
        "saludo": "welcoming2", "saluda": "welcoming2", "hola": "welcoming2",
        "saludos": "welcoming2", "un saludo": "welcoming2", "haz un saludo": "welcoming2", "saludo ahootsa": "welcoming2", "saluda ahootsa": "welcoming2", "sluod": "welcoming2", "sludo": "welcoming2", "salud": "welcoming2",
        "celebracion": "success1", "celebración": "success1", "celebraciÃ³n": "success1", "celebra": "success1", "aplauso": "success1", "bravo": "success1",
        "calma": "calming1", "tranquila": "calming1", "tranquilo": "calming1", "relajate": "calming1", "relájate": "calming1",
        "pensar": "thoughtful1", "piensa": "thoughtful1", "sorpresa": "amazed1", "asombro": "amazed1", "electrico": "electric1", "eléctrico": "electric1", "elÃ©ctrico": "electric1", "electrico uno": "electric1", "eléctrico uno": "electric1",
        "si": "yes1", "sí": "yes1", "asiente": "yes1", "no": "no1", "risa": "laughing2", "feliz": "laughing2", "dormir": "sleep1", "sueño": "sleep1",
    }
    for alias, technical in builtin.items():
        add_alias(alias, technical)
    display_names.update({
        "dance1": display_names.get("dance1", "baile alegre uno"),
        "dance2": display_names.get("dance2", "baile animado dos"),
        "dance3": display_names.get("dance3", "baile con energía tres"),
    })
    return {"aliases": alias_to_technical, "display_names": display_names}


def display_name_for_move(move_name: object) -> str:
    maps = _spanish_resource_maps()
    return maps.get("display_names", {}).get(str(move_name), str(move_name))


def available_examples_es(limit: int = 12) -> list[str]:
    available = set(list_moves())
    maps = _spanish_resource_maps()
    names = []
    preferred = ["dance1", "dance2", "dance3", "success1", "welcoming2", "calming1", "electric1", "thoughtful1", "amazed1", "laughing2", "yes1", "sleep1"]
    for mid in preferred:
        if mid in available:
            names.append(maps.get("display_names", {}).get(mid, mid))
    return names[:limit]


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
    """Return the union of moves known by RecordedMoves and JSON files on disk.

    In some Desktop/RecordedMoves versions list_moves() can be incomplete even when
    the local dataset contains dance2.json/dance3.json. If we only trusted that
    list, Spanish aliases such as "baile dos" or "baile tres" were rejected before
    trying to queue the move. The filesystem union makes recognition robust while
    still using RecordedMoves for execution.
    """
    moves: set[str] = set()
    try:
        moves.update(str(x) for x in get_recorded_moves().list_moves())
    except Exception as exc:
        logger.warning("Could not list RecordedMoves: %s", exc)

    dataset_dir = get_dataset_dir()
    if dataset_dir:
        try:
            moves.update(p.stem for p in dataset_dir.glob("*.json"))
        except Exception as exc:
            logger.warning("Could not scan dataset JSON files: %s", exc)
    return sorted(moves)


def resolve_emotion_name(requested_emotion: object) -> str | None:
    available = set(list_moves())
    if not available:
        return None
    requested = _normalize(requested_emotion)
    maps = _spanish_resource_maps()
    alias_map = maps.get("aliases", {})
    # Ahootsa 7.0.18: reglas tempranas para errores de voz frecuentes.
    # El STT a veces transcribe "baile" como "play", "olay", "olé" u "ole".
    # Resolver antes de la búsqueda por subcadena evita que "baile número dos" caiga en "baile" => dance1.
    tokens = set(requested.split("_"))
    if ("dos" in tokens or "2" in tokens or "segundo" in tokens) and (tokens & {"baile", "baila", "danza", "play", "olay", "ole", "olé"} or "dance" in tokens):
        if "dance2" in available:
            return "dance2"
    if ("tres" in tokens or "3" in tokens or "tercer" in tokens or "tercero" in tokens) and (tokens & {"baile", "baila", "danza", "play", "olay", "ole", "olé"} or "dance" in tokens):
        if "dance3" in available:
            return "dance3"
    if ("uno" in tokens or "1" in tokens or "primer" in tokens or "primero" in tokens or requested in {"play", "olay", "ole", "olé"}) and (tokens & {"baile", "baila", "danza", "play", "olay", "ole", "olé"} or requested in {"play", "olay", "ole", "olé"}):
        if "dance1" in available:
            return "dance1"
    if requested in {"electrico", "eléctrico", "elÃ©ctrico", "electric", "algo_electrico", "algo_elÃ©ctrico"}:
        if "electric1" in available:
            return "electric1"

    if not requested or requested == "random":
        pool = [m for m in FALLBACK_MOVES if m in available] or sorted(available)
        return random.choice(pool)
    if requested in available:
        return requested
    technical = alias_map.get(requested)
    if technical in available:
        return technical
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
    for alias, technical in sorted(alias_map.items(), key=lambda kv: len(kv[0] or ""), reverse=True):
        if technical in available and alias and len(alias) >= 3 and (alias in requested or requested in alias):
            return technical
    return None


def _cleanup_finished_channels() -> None:
    """Keep pygame Sound objects alive while their channels are playing."""
    try:
        kept = []
        for item in list(_PYGAME_SOUND_REFS):
            try:
                sound, channel, started = item
                if channel and channel.get_busy():
                    kept.append(item)
            except Exception:
                pass
        _PYGAME_SOUND_REFS[:] = kept
        _PYGAME_CHANNELS[:] = [item[1] for item in kept if item and item[1]]
    except Exception:
        _PYGAME_SOUND_REFS.clear()
        _PYGAME_CHANNELS.clear()


def _pygame_driver_candidates() -> list[str]:
    raw = os.getenv("AHOOTSA_PYGAME_AUDIO_DRIVERS", "").strip()
    if raw:
        return [x.strip() for x in raw.split(",") if x.strip()]
    # Windows-friendly order. Empty string means "use pygame/SDL default".
    return ["directsound", "wasapi", "winmm", ""]


def _init_pygame_mixer(pygame: Any) -> dict[str, Any]:
    """Try several SDL audio drivers and keep the first working mixer."""
    if pygame.mixer.get_init():
        return {"ok": True, "driver": os.getenv("SDL_AUDIODRIVER", "default"), "mixer_init": str(pygame.mixer.get_init())}

    last_error = ""
    tried: list[str] = []
    for driver in _pygame_driver_candidates():
        try:
            if driver:
                os.environ["SDL_AUDIODRIVER"] = driver
                tried.append(driver)
            else:
                os.environ.pop("SDL_AUDIODRIVER", None)
                tried.append("default")

            try:
                pygame.mixer.quit()
            except Exception:
                pass

            pygame.mixer.pre_init(frequency=48000, size=-16, channels=2, buffer=1024)
            pygame.mixer.init()
            pygame.mixer.set_num_channels(16)
            return {
                "ok": True,
                "driver": driver or "default",
                "tried": tried,
                "mixer_init": str(pygame.mixer.get_init()),
            }
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            continue

    return {"ok": False, "tried": tried, "error": last_error or "pygame.mixer.init failed"}


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
            init_result = _init_pygame_mixer(pygame)
            if not init_result.get("ok"):
                return {
                    "ok": False,
                    "backend": "pygame",
                    "stage": "mixer_init",
                    **init_result,
                    "ogg_path": str(ogg_path),
                }

            _cleanup_finished_channels()

            sound = pygame.mixer.Sound(str(ogg_path))
            try:
                volume = float(os.getenv("AHOOTSA_EMOTION_AUDIO_VOLUME", "1.0"))
                sound.set_volume(max(0.0, min(1.0, volume)))
            except Exception:
                pass

            channel = sound.play()
            if channel is None:
                return {
                    "ok": False,
                    "backend": "pygame",
                    "error": "pygame returned no free audio channel",
                    "ogg_path": str(ogg_path),
                    "mixer": init_result,
                }

            # Important: keep Sound object alive; otherwise short sounds can stop or not start in some runtimes.
            _PYGAME_SOUND_REFS.append((sound, channel, time.time()))
            _PYGAME_CHANNELS.append(channel)

        return {
            "ok": True,
            "backend": "pygame",
            "ogg_path": str(ogg_path),
            "mixer": init_result,
            "busy": bool(channel.get_busy()) if channel else False,
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
        return {"ok": True, "mode": "EmotionQueueMove", "queued": True}
    except Exception as exc:
        msg = f"{type(exc).__name__}: {exc}"
        # En MuJoCo algunos movimientos oficiales pueden generar avisos IK
        # (pose no alcanzable / posible colisión) aunque parte del movimiento
        # se haya enviado o ejecutado. No lo confundimos con fallo total.
        lowered = msg.lower()
        if "collision" in lowered or "not achievable" in lowered or "ik error" in lowered:
            return {"ok": True, "partial": True, "mode": "EmotionQueueMove", "warning": msg, "mujoco_ik_warning": True}
        return {"ok": False, "error": msg}


def _classify_play_result(motion_result: dict[str, Any], audio_result: dict[str, Any]) -> dict[str, Any]:
    """Return top-level status for the tool.

    The important part for the user is whether the robot movement was queued.
    Audio errors or MuJoCo IK warnings must not be presented as a failed dance
    when the robot visibly moved in MuJoCo.
    """
    motion_ok = bool(isinstance(motion_result, dict) and motion_result.get("ok"))
    audio_ok = bool(isinstance(audio_result, dict) and audio_result.get("ok"))
    audio_skipped = bool(isinstance(audio_result, dict) and audio_result.get("skipped"))
    if motion_ok:
        status = "played"
        ok = True
    elif audio_ok:
        status = "audio_played_motion_not_confirmed"
        ok = True
    else:
        status = "not_played"
        ok = False
    warnings = []
    if isinstance(motion_result, dict) and (motion_result.get("warning") or motion_result.get("mujoco_ik_warning")):
        warnings.append("MuJoCo/IK avisó de una pose difícil, pero no se trata como fallo si el movimiento fue visible.")
    if isinstance(audio_result, dict) and not audio_ok and not audio_skipped:
        warnings.append("El audio de la emoción no se pudo confirmar, pero el movimiento puede haberse ejecutado.")
    return {"ok": ok, "status": status, "motion_ok": motion_ok, "audio_ok": audio_ok, "warnings": warnings}


class PlayEmotion(Tool):
    """Play an official robot emotion with movement and matching official OGG sound."""

    name = "play_emotion"
    description = (
        "Play a robot emotion with movement and sound. "
        "Reproduce recursos oficiales de Reachy Mini con nombres en español y audio OGG. "
        "In Ahootsa 7.0.18 the audio uses a reinforced pygame/SDL backend with driver fallback and persistent Sound references."
    )
    needs_response = False

    parameters_schema = {
        "type": "object",
        "properties": {
            "emotion": {
                "type": "string",
                "description": "Nombre en español o técnico de emoción/baile. Ejemplos: baile uno, baile dos, baile tres, saludo, celebración, calma, eléctrico, success1, dance1. Acepta errores frecuentes como sludo/sluod para saludo.",
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
        _log_tool_start("play_emotion", kwargs)
        requested_emotion = kwargs.get("emotion", "random")
        delay_seconds = _ahootsa_action_delay_seconds(kwargs)
        post_wait_seconds = _ahootsa_post_play_wait_seconds(kwargs)
        sound_enabled = bool(False if _ahootsa_emotion_audio_disabled() else kwargs.get("sound", True))
        delay_seconds = _ahootsa_action_delay_seconds(kwargs)

        _log_event("call_start", {"requested_emotion": requested_emotion, "sound": sound_enabled, "delay_seconds": delay_seconds, "post_wait_seconds": post_wait_seconds})

        if not EMOTION_AVAILABLE:
            result = {"error": "Emotion system not available"}
            _log_event("call_error", result)
            return result

        move_name = resolve_emotion_name(requested_emotion)
        if not move_name:
            result = {"ok": False, "error": "No se ha reconocido la emoción o baile solicitado", "requested_emotion": requested_emotion, "available_examples": available_examples_es()}
            _log_event("call_error", result)
            return result

        # Delay before movement/audio so the robot can speak first.
        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)

        # Queue motion after the spoken phrase delay.
        motion_result = _queue_motion(deps, move_name)
        audio_result = _play_ogg(deps, move_name) if sound_enabled else {"ok": False, "skipped": True}

        if post_wait_seconds > 0:
            await asyncio.sleep(post_wait_seconds)

        classification = _classify_play_result(motion_result, audio_result)
        result: Dict[str, Any] = {
            "ok": classification["ok"],
            "status": classification["status"],
            "emotion": move_name,
            "requested_emotion": requested_emotion,
            "motion": motion_result,
            "audio": audio_result,
            "motion_ok": classification["motion_ok"],
            "audio_ok": classification["audio_ok"],
            "warnings": classification["warnings"],
            "mujoco_note": "Los avisos IK de MuJoCo son advertencias si el baile se ve ejecutado.",
            "dataset_dir": str(get_dataset_dir()) if get_dataset_dir() else None,
            "message_for_user": f"He reproducido {display_name_for_move(move_name)}.",
        }
        _log_event("call_result", result)
        _log_tool_result("play_emotion", result)
        return result
