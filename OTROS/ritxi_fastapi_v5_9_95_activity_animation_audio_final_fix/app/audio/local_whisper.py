"""
v5.9.61 · STT local Whisper

Este módulo convierte audio WAV del navegador en texto:
- carga `faster-whisper`;
- transcribe frases del usuario;
- aplica vocabulario guiado solo cuando la actividad es cerrada;
- evita repeticiones/alucinaciones frecuentes de Whisper;
- no debe romper la respuesta si falla un filtro auxiliar.

Regla importante:
Las actividades `open_text` y `open_name` no deben pasar por vocabulario cerrado.
"""


from __future__ import annotations

import asyncio
import tempfile
import time
import difflib
import re
from pathlib import Path
from typing import Any
from collections import Counter

from fastapi import HTTPException, UploadFile

from app.core.config import Settings
from app.core.logging import log_event
from app.models.schemas import TranscribeResponse

_MODEL: Any | None = None
_MODEL_KEY: tuple[str, str] | None = None


ANIMAL_VOCAB = [
    "perro", "gato", "vaca", "oveja", "caballo", "burro", "cerdo", "gallina", "pollo",
    "pato", "rana", "león", "tigre", "mono", "elefante", "jirafa", "cebra", "oso",
    "lobo", "zorro", "conejo", "ratón", "pájaro", "pez", "serpiente", "cocodrilo",
]
SHORT_WORD_VOCAB = [
    "hola", "adiós", "sí", "no", "ayuda", "gracias", "por favor", "turno",
    "perro", "gato", "vaca", "oveja", "caballo", "león", "mono", "rana", "pato",
]
VOCAB_ALIASES = {
    "pero": "perro",
    "perros": "perro",
    "gado": "gato",
    "gata": "gato",
    "baca": "vaca",
    "vacas": "vaca",
    "bakas": "vaca",
    "ovejas": "oveja",
    "obeja": "oveja",
    "leon": "león",
    "lion": "león",
    "mono": "mono",
    "mona": "mono",
    "cabayo": "caballo",
    "caballos": "caballo",
    "pajaro": "pájaro",
    "pajaros": "pájaro",
    "si": "sí",
    "vale": "sí",
    "no.": "no",
}

def _normalize_for_match(text: str) -> str:
    t = (text or "").lower().strip()
    t = re.sub(r"[¿?¡!.,;:()\[\]\"']", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _simple_tokens(text: str) -> list[str]:
    """Tokenización simple usada por el filtro anti-repetición.

    En versiones anteriores faltaba esta función y el filtro lanzaba NameError,
    provocando HTTP 500 justo después de que Whisper terminara de cargar.
    """
    normalized = _normalize_for_match(text)
    return [w for w in normalized.split() if w]

def _apply_guided_vocabulary(text: str, vocabulary_hint: str | None) -> tuple[str, dict[str, Any]]:
    """Corrige STT corto cuando el ejercicio espera vocabulario cerrado.

    Reglas v5.9.25:
    - yes/no solo se acepta si la respuesta es muy corta.
    - animal/short solo corrigen frases cortas.
    - nunca extrae "no" o "sí" de una frase larga rara.
    """
    hint = (vocabulary_hint or "").strip().lower()
    original = text or ""
    normalized = _normalize_for_match(original)
    words = normalized.split()

    if not hint or not normalized:
        return original, {"vocabulary_hint": hint, "vocabulary_applied": False}

    # yes/no debe ser muy estricto: no extraer "no" de una frase larga.
    if hint in {"yes_no", "si_no", "sí_no"}:
        if len(words) > 4:
            return "", {
                "vocabulary_hint": hint,
                "vocabulary_applied": False,
                "rejected": True,
                "reason": "yes_no_response_too_long",
                "original": original,
                "normalized": normalized,
                "word_count": len(words),
            }
        joined = " ".join(words)
        yes_values = {"sí", "si", "vale", "claro", "ok", "okay", "afirmativo"}
        no_values = {"no", "nunca", "negativo"}
        if joined in yes_values or any(w in yes_values for w in words):
            return "sí", {"vocabulary_hint": hint, "vocabulary_applied": True, "method": "strict_yes", "original": original}
        if joined in no_values or any(w in no_values for w in words):
            return "no", {"vocabulary_hint": hint, "vocabulary_applied": True, "method": "strict_no", "original": original}
        match_yes = difflib.get_close_matches(joined, list(yes_values), n=1, cutoff=0.82)
        match_no = difflib.get_close_matches(joined, list(no_values), n=1, cutoff=0.82)
        if match_yes:
            return "sí", {"vocabulary_hint": hint, "vocabulary_applied": True, "method": "fuzzy_yes", "original": original}
        if match_no:
            return "no", {"vocabulary_hint": hint, "vocabulary_applied": True, "method": "fuzzy_no", "original": original}
        return "", {
            "vocabulary_hint": hint,
            "vocabulary_applied": False,
            "rejected": True,
            "reason": "yes_no_not_recognized",
            "original": original,
            "normalized": normalized,
        }

    if hint in {"animal", "animals", "animal_game"}:
        vocab = ANIMAL_VOCAB
        max_words_for_contains = 6
        fuzzy_cutoff = 0.72
    elif hint in {"short", "short_game", "activity", "actividad"}:
        vocab = SHORT_WORD_VOCAB
        max_words_for_contains = 5
        fuzzy_cutoff = 0.75
    else:
        vocab = SHORT_WORD_VOCAB
        max_words_for_contains = 5
        fuzzy_cutoff = 0.75

    # No corregir frases largas abiertas.
    if len(words) > max_words_for_contains:
        return original, {
            "vocabulary_hint": hint,
            "vocabulary_applied": False,
            "reason": "too_many_words_for_guided_vocabulary",
            "original": original,
            "normalized": normalized,
            "word_count": len(words),
        }

    # Alias exactos.
    for w in words:
        if w in VOCAB_ALIASES and VOCAB_ALIASES[w] in vocab:
            fixed = VOCAB_ALIASES[w]
            return fixed, {
                "vocabulary_hint": hint,
                "vocabulary_applied": True,
                "method": "alias",
                "original": original,
                "normalized": normalized,
                "matched": fixed,
            }

    # Contiene palabra esperada en frase corta.
    for candidate in vocab:
        c_norm = _normalize_for_match(candidate)
        if c_norm and re.search(rf"\b{re.escape(c_norm)}\b", normalized):
            return candidate, {
                "vocabulary_hint": hint,
                "vocabulary_applied": True,
                "method": "contains_short",
                "original": original,
                "normalized": normalized,
                "matched": candidate,
            }

    # Fuzzy matching solo para 1-3 palabras.
    if len(words) <= 3:
        choices = [_normalize_for_match(v) for v in vocab]
        match = difflib.get_close_matches(normalized, choices, n=1, cutoff=fuzzy_cutoff)
        if not match and len(words) == 1:
            match = difflib.get_close_matches(words[0], choices, n=1, cutoff=fuzzy_cutoff)
        if match:
            idx = choices.index(match[0])
            fixed = vocab[idx]
            return fixed, {
                "vocabulary_hint": hint,
                "vocabulary_applied": True,
                "method": "fuzzy_short",
                "original": original,
                "normalized": normalized,
                "matched": fixed,
                "score_target": match[0],
            }

    return original, {
        "vocabulary_hint": hint,
        "vocabulary_applied": False,
        "original": original,
        "normalized": normalized,
        "vocabulary_size": len(vocab),
    }

def _repetition_hallucination_score(text: str) -> dict[str, Any]:
    """Detecta bucles típicos de STT/Whisper en silencio, eco o ruido."""
    tokens = _simple_tokens(text)
    if len(tokens) < 12:
        return {"repetition_detected": False, "reason": "short", "tokens": len(tokens)}

    unique_ratio = len(set(tokens)) / max(len(tokens), 1)

    def ngram_counts(n: int) -> Counter[tuple[str, ...]]:
        return Counter(tuple(tokens[i:i+n]) for i in range(0, max(0, len(tokens)-n+1)))

    top = {}
    repeated_ngram = False
    for n in (2, 3, 4, 5):
        counts = ngram_counts(n)
        if counts:
            gram, count = counts.most_common(1)[0]
            top[str(n)] = {"gram": " ".join(gram), "count": count}
            if len(tokens) >= 18 and ((n == 2 and count >= 6) or (n == 3 and count >= 4) or (n >= 4 and count >= 3)):
                repeated_ngram = True
            if len(tokens) >= 16 and count >= 3 and unique_ratio < 0.40:
                repeated_ngram = True

    same_phrase_like = unique_ratio < 0.26 and len(tokens) >= 12
    detected = repeated_ngram or same_phrase_like

    return {
        "repetition_detected": detected,
        "tokens": len(tokens),
        "unique_ratio": round(unique_ratio, 3),
        "top_ngrams": top,
        "reason": "repeated_ngram_or_low_unique_ratio" if detected else "ok",
    }

def _filter_repetition_hallucination(text: str) -> tuple[str, dict[str, Any]]:
    info = _repetition_hallucination_score(text)
    if info.get("repetition_detected"):
        return "", {
            **info,
            "filtered": True,
            "original_preview": (text or "")[:240],
        }
    return text, {**info, "filtered": False}

def _load_model(settings: Settings):
    """Carga o reutiliza el modelo faster-whisper según tamaño/dispositivo."""
    global _MODEL, _MODEL_KEY
    key = (settings.stt_whisper_model_size, settings.stt_whisper_compute_type)
    if _MODEL is not None and _MODEL_KEY == key:
        return _MODEL
    try:
        from faster_whisper import WhisperModel
    except Exception as exc:  # pragma: no cover - depends on optional package
        raise RuntimeError(
            "No está instalado faster-whisper. Ejecuta: scripts\\setup_uv_stt_whisper_windows.bat"
        ) from exc
    log_event(
        "stt_whisper_model_loading",
        model_size=settings.stt_whisper_model_size,
        compute_type=settings.stt_whisper_compute_type,
    )
    _MODEL = WhisperModel(
        settings.stt_whisper_model_size,
        device="auto",
        compute_type=settings.stt_whisper_compute_type,
    )
    _MODEL_KEY = key
    log_event("stt_whisper_model_ready", model_size=settings.stt_whisper_model_size)
    return _MODEL


def _transcribe_sync(path: str, settings: Settings, language: str) -> tuple[str, dict[str, Any]]:
    model = _load_model(settings)
    segments, info = model.transcribe(
        path,
        language=language or settings.stt_whisper_language,
        vad_filter=True,
        beam_size=1,
        best_of=1,
        condition_on_previous_text=False,
        temperature=0.0,
    )
    pieces: list[str] = []
    segment_data: list[dict[str, Any]] = []
    for seg in segments:
        text = (getattr(seg, "text", "") or "").strip()
        if text:
            pieces.append(text)
        segment_data.append(
            {
                "start": getattr(seg, "start", None),
                "end": getattr(seg, "end", None),
                "text": text,
            }
        )
    metadata = {
        "language": getattr(info, "language", language),
        "language_probability": getattr(info, "language_probability", None),
        "duration": getattr(info, "duration", None),
        "segments": segment_data,
        "model_size": settings.stt_whisper_model_size,
        "compute_type": settings.stt_whisper_compute_type,
    }
    return " ".join(pieces).strip(), metadata


async def transcribe_audio_file(file: UploadFile, settings: Settings, language: str, vocabulary_hint: str | None = None) -> TranscribeResponse:
    start = time.perf_counter()
    suffix = Path(file.filename or "audio.wav").suffix or ".wav"
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Audio vacío.")
    if len(data) > 12 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio demasiado grande.")

    log_event(
        "stt_audio_upload",
        filename=file.filename,
        content_type=file.content_type,
        bytes=len(data),
        language=language,
    )

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        text, metadata = await asyncio.to_thread(_transcribe_sync, tmp_path, settings, language)
    except RuntimeError as exc:
        log_event("stt_whisper_unavailable", error=str(exc))
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        log_event("stt_whisper_error", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Error transcribiendo audio: {exc}") from exc
    finally:
        try:
            Path(locals().get("tmp_path", "")).unlink(missing_ok=True)
        except Exception:
            pass

    try:
        corrected_text, vocab_meta = _apply_guided_vocabulary(text, vocabulary_hint)
        if corrected_text != text:
            log_event(
                "stt_vocabulary_corrected",
                original=text,
                corrected=corrected_text,
                vocabulary_hint=vocabulary_hint,
                metadata=vocab_meta,
            )
        text = corrected_text
        metadata["vocabulary"] = vocab_meta
    except Exception as exc:  # noqa: BLE001
        metadata["vocabulary"] = {"error": str(exc), "vocabulary_hint": vocabulary_hint}
        log_event("stt_vocabulary_filter_error", error=str(exc), vocabulary_hint=vocabulary_hint)

    try:
        filtered_text, repetition_meta = _filter_repetition_hallucination(text)
        if filtered_text != text:
            log_event(
                "stt_repetition_filtered",
                original=text[:300],
                metadata=repetition_meta,
            )
        text = filtered_text
        metadata["repetition_filter"] = repetition_meta
    except Exception as exc:  # noqa: BLE001
        metadata["repetition_filter"] = {"error": str(exc), "filtered": False}
        log_event("stt_repetition_filter_error", error=str(exc))

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    log_event(
        "stt_whisper_result",
        text_len=len(text),
        text_preview=text[:160],
        latency_ms=elapsed_ms,
        metadata={k: v for k, v in metadata.items() if k != "segments"},
    )
    return TranscribeResponse(text=text, provider="local_whisper", warm=True, latency_ms=elapsed_ms, metadata=metadata)


async def warmup_whisper_model(settings: Settings) -> dict[str, Any]:
    """Carga el modelo Whisper en segundo plano para evitar la espera en el primer uso."""
    start = time.perf_counter()
    try:
        await asyncio.to_thread(_load_model, settings)
    except RuntimeError as exc:
        log_event("stt_whisper_warmup_unavailable", error=str(exc))
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        log_event("stt_whisper_warmup_error", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Error calentando Whisper: {exc}") from exc
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    log_event(
        "stt_whisper_warmup_ready",
        model_size=settings.stt_whisper_model_size,
        compute_type=settings.stt_whisper_compute_type,
        elapsed_ms=elapsed_ms,
    )
    return {
        "warm": True,
        "model_size": settings.stt_whisper_model_size,
        "compute_type": settings.stt_whisper_compute_type,
        "elapsed_ms": elapsed_ms,
    }
