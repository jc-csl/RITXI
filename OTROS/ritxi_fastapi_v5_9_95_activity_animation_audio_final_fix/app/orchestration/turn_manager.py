from __future__ import annotations

import logging
import re
import time

from app.audio.echo_guard import EchoGuard
from app.core.config import Settings
from app.core.logging import log_event
from app.llm.base import LLMProvider, LLMResult
from app.models.schemas import ChatResponse, FeatureFlags, LatencyMetrics
from app.orchestration.action_scheduler import ActionIntent, ActionScheduler
from app.orchestration.conversation import ConversationMemory, fallback_result
from app.services.character import CharacterManager
from app.services.emotions import parse_emotion

logger = logging.getLogger(__name__)

_SENTENCE_RE = re.compile(r"(.+?[.!?。！？])\s+", re.DOTALL)



def _fallback_clean_text(user_text: str, raw_text: str) -> str:
    """Garantiza texto visible sin repetir siempre la misma frase."""
    raw = (raw_text or "").strip()
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE).strip()
    raw = re.sub(r"^\[[A-ZÁÉÍÓÚÑ_]+\]\s*", "", raw).strip()
    if raw:
        return raw
    lowered = (user_text or "").lower()
    if "vida" in lowered:
        return "La vida tiene muchas cosas importantes: aprender, cuidar a otros, descansar, jugar y disfrutar poco a poco."
    if "perro" in lowered and "gato" in lowered:
        return "Un perro suele ser muy sociable y le gusta jugar. Un gato suele ser más tranquilo e independiente. Los dos pueden ser buenos compañeros."
    if "perro" in lowered:
        return "Un perro es un animal muy sociable. Suele jugar, aprender órdenes sencillas y acompañar a las personas."
    if "gato" in lowered:
        return "Un gato es un animal tranquilo y curioso. Suele moverse con cuidado y le gusta explorar."
    if "ayuda" in lowered:
        return "Claro. Podemos practicar cómo pedir ayuda. Puedes decir: “Por favor, ¿me puedes ayudar?”"
    if "hola" in lowered:
        return "Hola. Estoy contigo. ¿Qué quieres practicar ahora?"
    if "contento" in lowered or "feliz" in lowered:
        return "Sí, estoy contento de practicar contigo. Lo estás haciendo muy bien."
    if "dime" in lowered:
        return "Claro. Dime el tema y te doy una respuesta corta."
    return "Entendido. Te respondo sobre el tema que me digas, con una frase corta."


class TurnManager:
    """Orquestador único del ciclo: escuchar → pensar → hablar/mover → volver a escuchar."""

    def __init__(
        self,
        settings: Settings,
        llm_provider: LLMProvider,
        memory: ConversationMemory,
        scheduler: ActionScheduler,
        echo_guard: EchoGuard,
        character_manager: CharacterManager,
    ):
        self.settings = settings
        self.llm_provider = llm_provider
        self.memory = memory
        self.scheduler = scheduler
        self.echo_guard = echo_guard
        self.character_manager = character_manager
        self.state = "idle"
        self.last_latencies: LatencyMetrics | None = None
        self.last_response: str | None = None

    async def handle_text(self, session_id: str, text: str, flags: FeatureFlags) -> ChatResponse:
        session_id = session_id.strip() or self.settings.default_session_id
        latencies = LatencyMetrics()
        start_turn = time.perf_counter()
        action_ids: list[str] = []
        warnings: list[str] = []
        llm_result: LLMResult
        streaming_used = bool(flags.streaming and self.settings.llm_streaming_enabled)

        log_event("turn_start", session_id=session_id, text_len=len(text), text_preview=text[:200], flags=flags.model_dump())

        async with self.memory.lock_for(session_id):
            await self.echo_guard.mute("turn-start")
            self.state = "thinking"
            messages = self.memory.messages_for(session_id, text)

            if flags.robot_motion:
                action = await self.scheduler.enqueue(
                    ActionIntent(emotion="pensando", motion_enabled=True, audio_enabled=False, return_to_neutral=False, layer="emotion", reason="thinking"),
                    wait=False,
                )
                action_ids.append(action.action_id)

            first_sentence_spoken = False
            spoken_prefix = ""
            if not flags.llm:
                llm_result = LLMResult(
                    content="[CALMA] Módulo LLM desactivado para pruebas. He recibido tu mensaje, pero no voy a consultar a Ollama en este turno.",
                    provider="disabled",
                    model="llm-disabled",
                    warnings=["LLM desactivado desde el panel de pruebas por módulos."],
                    first_token_ms=0.0,
                    total_ms=0.0,
                    streaming_used=False,
                )
                streaming_used = False
                log_event("llm_skipped", session_id=session_id, reason="flag_disabled")
            else:
                log_event("llm_start", session_id=session_id, provider=self.llm_provider.provider_name, model=self.llm_provider.model_name, streaming=streaming_used, messages=len(messages))
                try:
                    if streaming_used:
                        llm_result, first_sentence_action = await self._stream_llm_with_optional_early_tts(messages, flags)
                        if first_sentence_action:
                            action_ids.append(first_sentence_action.action_id)
                            first_sentence_spoken = True
                            spoken_prefix = first_sentence_action.text or ""
                    else:
                        llm_result = await self.llm_provider.chat(messages)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Fallo LLM, fallback=%s", exc)
                    if not self.settings.mock_fallback_enabled:
                        raise
                    llm_result = fallback_result(exc, messages)
                    streaming_used = False

            log_event("llm_end", session_id=session_id, provider=llm_result.provider, model=llm_result.model, first_token_ms=llm_result.first_token_ms, total_ms=llm_result.total_ms, content_len=len(llm_result.content), content_preview=llm_result.content[:300], warnings=llm_result.warnings)

            latencies.llm_first_token_ms = llm_result.first_token_ms
            latencies.llm_total_ms = llm_result.total_ms
            warnings.extend(llm_result.warnings)

            parsed = parse_emotion(llm_result.content, process_emotions=flags.process_emotions)
            clean_text = parsed.clean_text or _fallback_clean_text(text, llm_result.content)
            log_event("emotion_parsed", session_id=session_id, emotion=parsed.emotion, clean_text_len=len(clean_text), clean_text_preview=clean_text[:300])
            self.memory.commit(session_id, text, llm_result.content)

            self.state = "speaking" if flags.output_audio else "moving"
            remaining_text = clean_text
            if first_sentence_spoken and spoken_prefix:
                remaining_text = clean_text.replace(spoken_prefix.strip(), "", 1).strip()

            # Si ya hemos lanzado la primera frase en streaming, al final lanzamos el resto.
            # Si no, lanzamos todo junto.
            final_text_for_audio = remaining_text if first_sentence_spoken else clean_text
            should_move = flags.robot_motion and parsed.emotion != "neutral"
            should_speak = flags.output_audio and flags.tts and bool(final_text_for_audio)

            if should_move or should_speak:
                action = await self.scheduler.enqueue(
                    ActionIntent(
                        emotion=parsed.emotion,
                        text=final_text_for_audio,
                        motion_enabled=should_move,
                        audio_enabled=should_speak,
                        return_to_neutral=True,
                        layer="speech" if should_speak else "emotion",
                        reason="chat-final",
                        speech_motion=flags.speech_motion,
                    ),
                    wait=flags.synchronize_turn,
                )
                action_ids.append(action.action_id)
                if action.error:
                    warnings.append(f"Acción {action.action_id}: {action.error}")

            if flags.synchronize_turn:
                await self.echo_guard.cooldown_and_unmute("turn-complete")
                self.state = "idle"
            else:
                # En modo no bloqueante no podemos saber cuándo terminará la voz; se mantiene más seguro.
                await self.echo_guard.cooldown_and_unmute("turn-queued")
                self.state = "idle"

            latencies.output_total_ms = (time.perf_counter() - start_turn) * 1000 - latencies.llm_total_ms
            latencies.turn_total_ms = (time.perf_counter() - start_turn) * 1000
            self.last_latencies = latencies
            self.last_response = clean_text
            log_event("turn_end", session_id=session_id, response_len=len(clean_text), emotion=parsed.emotion, action_ids=action_ids, latencies=latencies.model_dump(), warnings=warnings, microphone_enabled=self.echo_guard.status().microphone_enabled, state=self.state)

            return ChatResponse(
                session_id=session_id,
                text=clean_text,
                raw_llm_text=llm_result.content if flags.debug else None,
                emotion=parsed.emotion,  # type: ignore[arg-type]
                action_ids=action_ids,
                action_queued=bool(action_ids),
                action_completed=flags.synchronize_turn,
                queue_size=self.scheduler.status().queue_size,
                character_id=self.character_manager.current_id,
                provider=llm_result.provider,
                model=llm_result.model,
                streaming_used=streaming_used,
                microphone_enabled=self.echo_guard.status().microphone_enabled,
                turn_state=self.state,
                latencies=latencies,
                warnings=warnings,
            )

    async def _stream_llm_with_optional_early_tts(self, messages: list[dict[str, str]], flags: FeatureFlags) -> tuple[LLMResult, ActionIntent | None]:
        start = time.perf_counter()
        buffer = ""
        first_token_ms: float | None = None
        first_sentence_action: ActionIntent | None = None
        warnings: list[str] = []

        log_event("llm_stream_start", provider=self.llm_provider.provider_name, model=self.llm_provider.model_name)
        async for chunk in self.llm_provider.chat_stream(messages):
            if chunk.first_token_ms is not None and first_token_ms is None:
                first_token_ms = chunk.first_token_ms
            if chunk.warnings:
                warnings = chunk.warnings
            if chunk.content:
                buffer += chunk.content
                if (
                    flags.output_audio
                    and flags.tts
                    and self.settings.first_sentence_tts_streaming
                    and first_sentence_action is None
                ):
                    parsed_so_far = parse_emotion(buffer, process_emotions=flags.process_emotions)
                    match = _SENTENCE_RE.search(parsed_so_far.clean_text + " ")
                    if match:
                        first_sentence = match.group(1).strip()
                        if len(first_sentence) >= 8:
                            log_event("llm_stream_first_sentence", first_sentence=first_sentence[:300], first_sentence_len=len(first_sentence))
                            first_sentence_action = await self.scheduler.enqueue(
                                ActionIntent(
                                    emotion="neutral",
                                    text=first_sentence,
                                    motion_enabled=flags.robot_motion,
                                    audio_enabled=True,
                                    return_to_neutral=False,
                                    layer="speech",
                                    reason="stream-first-sentence",
                                    speech_motion=flags.speech_motion,
                                ),
                                wait=False,
                            )
            if chunk.done:
                total = chunk.total_ms or (time.perf_counter() - start) * 1000
                return LLMResult(
                    content=buffer.strip(),
                    provider=chunk.provider,
                    model=chunk.model,
                    warnings=warnings,
                    first_token_ms=first_token_ms,
                    total_ms=total,
                    streaming_used=True,
                ), first_sentence_action

        return LLMResult(
            content=buffer.strip(),
            provider=self.llm_provider.provider_name,
            model=self.llm_provider.model_name,
            warnings=warnings,
            first_token_ms=first_token_ms,
            total_ms=(time.perf_counter() - start) * 1000,
            streaming_used=True,
        ), first_sentence_action
