import uuid
import logging
import asyncio
from datetime import datetime
from typing import Any, Optional
from sqlalchemy.future import select

from app.db.models.voice_session import VoiceSession, VoiceSessionStatus
from app.services.voice.stt_provider_interface import BaseSTTProvider
from app.services.voice.tts_provider_interface import BaseTTSProvider
from app.services.companion.orchestrator import CompanionOrchestrator
from app.services.companion.domain import NormalizedInput, InputType

logger = logging.getLogger(__name__)

# Fallback In-Memory store for fast session tracking
_active_voice_sessions = {}

class VoiceAudioResult(bytes):
    """Dual-compatible Voice Result that behaves as bytes and unpacks as (audio, transcript, response_text)."""
    def __new__(cls, audio_bytes: bytes, transcript: str = "", response_text: str = ""):
        obj = super().__new__(cls, audio_bytes or b"")
        obj.audio_bytes = audio_bytes or b""
        obj.transcript = transcript
        obj.response_text = response_text
        return obj

    def __iter__(self):
        yield self.audio_bytes
        yield self.transcript
        yield self.response_text

    def __getitem__(self, item):
        # Support tuple indexing (res[0], res[1], res[2])
        if isinstance(item, int):
            if item == 0:
                return self.audio_bytes
            elif item == 1:
                return self.transcript
            elif item == 2:
                return self.response_text
        return super().__getitem__(item)


class VoiceService:
    """
    Voice Pipeline Service:
    Audio Input -> STT -> NormalizedInput -> CompanionOrchestrator -> Unified Response -> TTS -> Audio Output
    (Decoupled from legacy ConversationService, supporting AsyncSession & Sync Session)
    """
    def __init__(self, 
                 db: Any, 
                 stt_provider: BaseSTTProvider, 
                 tts_provider: BaseTTSProvider, 
                 orchestrator: CompanionOrchestrator):
        self.db = db
        self.stt = stt_provider
        self.tts = tts_provider
        self.orchestrator = orchestrator

    async def _get_voice_session(self, session_id: str) -> Optional[VoiceSession]:
        if hasattr(self.db, "query"):
            try:
                res = self.db.query(VoiceSession).filter(VoiceSession.session_id == session_id).first()
                if res:
                    return res
            except Exception:
                pass
        elif hasattr(self.db, "execute"):
            try:
                res = await self.db.execute(select(VoiceSession).filter(VoiceSession.session_id == session_id))
                val = res.scalars().first()
                if val:
                    return val
            except Exception:
                pass

        if session_id in _active_voice_sessions:
            return _active_voice_sessions[session_id]
        return None

    async def _save_voice_session(self, session: VoiceSession):
        _active_voice_sessions[session.session_id] = session
        if hasattr(self.db, "add") and hasattr(self.db, "commit"):
            try:
                self.db.add(session)
                if asyncio.iscoroutinefunction(self.db.commit):
                    await self.db.commit()
                else:
                    self.db.commit()
            except Exception as e:
                logger.debug(f"[VoiceService] DB save skipped: {e}")

    async def create_session_async(self, user_id: str, companion_id: str, conversation_id: str) -> VoiceSession:
        session_id = str(uuid.uuid4())
        session = VoiceSession(
            session_id=session_id,
            user_id=user_id,
            companion_id=companion_id,
            conversation_id=conversation_id,
            status=VoiceSessionStatus.IDLE.value,
            provider="openai"
        )
        await self._save_voice_session(session)
        return session

    def create_session(self, user_id: str, companion_id: str, conversation_id: str) -> VoiceSession:
        session_id = str(uuid.uuid4())
        session = VoiceSession(
            session_id=session_id,
            user_id=user_id,
            companion_id=companion_id,
            conversation_id=conversation_id,
            status=VoiceSessionStatus.IDLE.value,
            provider="openai"
        )
        _active_voice_sessions[session_id] = session
        return session

    async def process_audio(
        self, 
        session_id: str, 
        audio_data: bytes,
        user_id: Optional[str] = None,
        companion_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        image_data: Optional[bytes] = None,
        camera_timestamp_ms: Optional[int] = None,
    ) -> bytes:
        session = await self._get_voice_session(session_id)
        if not session:
            # Create session on the fly if missing
            session = VoiceSession(
                session_id=session_id,
                user_id=user_id or "default_user",
                companion_id=companion_id or "default_companion",
                conversation_id=conversation_id or "default",
                status=VoiceSessionStatus.IDLE.value,
                provider="openai"
            )
            await self._save_voice_session(session)
        else:
            if companion_id and session.companion_id != companion_id:
                session.companion_id = companion_id
            if user_id and session.user_id != user_id:
                session.user_id = user_id
            if conversation_id and session.conversation_id != conversation_id:
                session.conversation_id = conversation_id
            await self._save_voice_session(session)

        t0 = datetime.utcnow()
        import time
        perf_start = time.perf_counter()

        try:
            # 1. Update status to TRANSCRIBING
            session.status = VoiceSessionStatus.TRANSCRIBING.value
            await self._save_voice_session(session)

            # 2. STT Transcribe
            t_stt_start = time.perf_counter()
            logger.info(f"[VoiceService][LATENCY] STT Start: Transcribing {len(audio_data)} audio bytes for companion {session.companion_id}...")
            transcript = await self.stt.transcribe(audio_data)
            t_stt_end = time.perf_counter()
            stt_duration_ms = (t_stt_end - t_stt_start) * 1000
            logger.info(f"[VoiceService][LATENCY] STT Complete ({stt_duration_ms:.1f}ms): '{transcript}'")

            if not transcript or not transcript.strip():
                logger.warning("[VoiceService] No speech transcribed from audio.")
                cid_lower = (session.companion_id or "").lower()
                if "mani" in cid_lower or "마니" in session.companion_id:
                    response_text = "아빠, 목소리가 잘 안 들렸어요! 마이크 가까이에서 다시 한번 말씀해 주세요! 😊"
                elif "hana" in cid_lower or "하나" in session.companion_id:
                    response_text = "목소리가 잘 안 들렸어! 마이크 가까이에서 다시 말해줄래?"
                else:
                    response_text = "여보, 목소리가 잘 안 들렸어요. 마이크 가까이에서 다시 한번 말씀해 주실래요?"
                
                # Direct response without orchestrator
                import os
                selected_voice = os.getenv("EDGE_TTS_VOICE", "ko-KR-SunHiNeural")
                voice_context = {"voice_id": selected_voice, "avatar_state": {"expression": "listening", "animation": "tilt"}}
                audio_response = await self.tts.synthesize(response_text, voice_context=voice_context)
                
                session.status = VoiceSessionStatus.IDLE.value
                await self._save_voice_session(session)
                return audio_response, "", response_text
            
            metadata = {
                "voice_session_id": session_id,
            }
            if image_data:
                metadata["image_data"] = image_data
                metadata["has_camera_frame"] = True
            if camera_timestamp_ms:
                metadata["camera_timestamp_ms"] = camera_timestamp_ms

            normalized_input = NormalizedInput(
                interaction_id=f"INT-VOICE-{uuid.uuid4().hex[:8]}",
                user_id=session.user_id,
                companion_id=session.companion_id,
                conversation_id=session.conversation_id,
                input_type=InputType.VOICE,
                content=transcript,
                metadata=metadata
            )

            # 3. LLM / Companion Orchestrator with First-Chunk Streaming
            t_llm_start = time.perf_counter()
            logger.info(f"[VoiceService][LATENCY] LLM Streaming Start: Processing input '{transcript}'")
            
            # Resolve character voice context in advance
            try:
                from app.services.character.presentation_resolver import CharacterPresentationResolver
                resolver = CharacterPresentationResolver(self.db)
                pres_ctx = await resolver.resolve(user_id=session.user_id, companion_id=session.companion_id)
                selected_voice = pres_ctx.voice.voice_id or "ko-KR-SunHiNeural"
                speaking_rate = pres_ctx.voice.speaking_rate
                pitch_offset = pres_ctx.voice.pitch_offset
            except Exception as e:
                logger.warning(f"[VoiceService] Fallback voice resolution: {e}")
                cid_lower = (session.companion_id or "").lower()
                if "mani" in cid_lower or "마니" in session.companion_id:
                    selected_voice = "ko-KR-JiMinNeural"
                    speaking_rate = 1.05
                    pitch_offset = 2.0
                elif "hana" in cid_lower or "하나" in session.companion_id:
                    selected_voice = "ko-KR-SeoHyeonNeural"
                    speaking_rate = 1.0
                    pitch_offset = 0.0
                else:
                    selected_voice = "ko-KR-SunHiNeural"
                    speaking_rate = 0.98
                    pitch_offset = 0.0

            rate_pct = f"{int((speaking_rate - 1.0) * 100):+d}%"
            pitch_hz = f"{int(pitch_offset):+d}Hz"

            voice_context = {
                "voice_id": selected_voice,
                "edge_tts_voice": selected_voice,
                "speaking_rate_str": rate_pct,
                "pitch_offset_str": pitch_hz,
            }

            response_text = ""
            first_chunk_audio = None
            first_chunk_text = None
            first_chunk_ttfb_ms = 0.0
            all_chunks = []

            try:
                # First-Chunk Streaming Attempt
                first_chunk_task = None
                async for chunk_text, is_last, av_state, current_full_text in self.orchestrator.process_interaction_stream_chunks(normalized_input):
                    all_chunks.append(chunk_text)
                    response_text = current_full_text
                    voice_context["avatar_state"] = av_state

                    # Trigger TTS immediately on First Chunk!
                    if first_chunk_text is None and len(chunk_text.strip()) > 0:
                        first_chunk_text = chunk_text.strip()
                        t_first_chunk_ready = time.perf_counter()
                        first_chunk_ttfb_ms = (t_first_chunk_ready - t_llm_start) * 1000
                        logger.info(f"[VoiceService][LATENCY] ⚡ First Chunk Ready in {first_chunk_ttfb_ms:.1f}ms: '{first_chunk_text}' -> Triggering Instant TTS!")
                        first_chunk_task = asyncio.create_task(self.tts.synthesize(first_chunk_text, voice_context=voice_context))

                t_llm_end = time.perf_counter()
                llm_duration_ms = (t_llm_end - t_llm_start) * 1000
                logger.info(f"[VoiceService][LATENCY] LLM Streaming Finished ({llm_duration_ms:.1f}ms): '{response_text}'")

                # Wait for First Chunk Audio
                if first_chunk_task:
                    t_tts_fc_start = time.perf_counter()
                    first_chunk_audio = await first_chunk_task
                    t_tts_fc_end = time.perf_counter()
                    fc_tts_ms = (t_tts_fc_end - t_tts_fc_start) * 1000
                    logger.info(f"[VoiceService][LATENCY] ⚡ First Chunk Audio Ready in {fc_tts_ms:.1f}ms (Size: {len(first_chunk_audio or b'')} bytes)")

                # If full response is longer than first chunk, synthesize remaining/full audio
                t_tts_start = time.perf_counter()
                if len(all_chunks) <= 1 and first_chunk_audio:
                    audio_response = first_chunk_audio
                else:
                    audio_response = await self.tts.synthesize(response_text, voice_context=voice_context)
                t_tts_end = time.perf_counter()
                tts_duration_ms = (t_tts_end - t_tts_start) * 1000

            except Exception as stream_err:
                # Safe Fallback to standard sync orchestrator
                logger.warning(f"[VoiceService] Streaming TTS fallback to batch mode: {stream_err}")
                unified_response = await self.orchestrator.process_interaction_sync(normalized_input)
                response_text = unified_response.text
                voice_context["avatar_state"] = unified_response.avatar_state
                audio_response = await self.tts.synthesize(response_text, voice_context=voice_context)
                t_tts_end = time.perf_counter()
                llm_duration_ms = (t_tts_end - t_llm_start) * 1000
                tts_duration_ms = 0.0

            # 4. SPEAKING (TTS)
            session.status = VoiceSessionStatus.SPEAKING.value
            await self._save_voice_session(session)

            total_backend_ms = (time.perf_counter() - perf_start) * 1000
            logger.info(
                f"[VoiceService][LATENCY-SUMMARY] STT: {stt_duration_ms:.1f}ms | "
                f"LLM First-Chunk: {first_chunk_ttfb_ms:.1f}ms | "
                f"LLM Total: {llm_duration_ms:.1f}ms | "
                f"TTS Total: {tts_duration_ms:.1f}ms | "
                f"Total Backend: {total_backend_ms:.1f}ms (Audio: {len(audio_response)} bytes)"
            )

            # 5. Return to IDLE
            session.status = VoiceSessionStatus.IDLE.value
            await self._save_voice_session(session)


            return VoiceAudioResult(audio_response, transcript, response_text)

        except Exception as e:
            session.status = VoiceSessionStatus.ERROR.value
            session.error_code = str(e)
            await self._save_voice_session(session)
            logger.error(f"[VoiceService] Voice pipeline processing failed: {e}")
            raise e

    def interrupt_session(self, session_id: str) -> None:
        session = None
        if hasattr(self.db, "query"):
            try:
                session = self.db.query(VoiceSession).filter(VoiceSession.session_id == session_id).first()
            except Exception:
                pass
        if not session:
            session = _active_voice_sessions.get(session_id)
        if session:
            session.status = VoiceSessionStatus.LISTENING.value

    def end_session(self, session_id: str) -> None:
        session = _active_voice_sessions.get(session_id)
        if session:
            session.ended_at = datetime.utcnow()
            session.status = VoiceSessionStatus.IDLE.value

