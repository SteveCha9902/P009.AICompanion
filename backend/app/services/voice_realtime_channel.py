"""
Voice Realtime Channel Service (STEP 13)
Bi-directional Persistent WebSocket Session Handler for P009 (S25 Ultra) <-> P015 / Backend.
Provides:
- Handshake & Session Lifecycle: session.start -> session.ready -> session.end
- Real-time Audio Upload & Whisper STT: transcript.partial / transcript.final
- Real-time Chunk-by-Chunk Streaming LLM & Parallel TTS Audio Chunk emission
- Immediate Interruption (Barge-in) cancellation
- Heartbeat ping / pong & connection resilience
"""

import asyncio
import base64
import json
import logging
import time
import uuid
from typing import Any, Optional
from fastapi import WebSocket, WebSocketDisconnect

from app.services.companion.domain import NormalizedInput, InputType
from app.services.companion.orchestrator import CompanionOrchestrator
from app.services.voice.stt_provider_interface import BaseSTTProvider
from app.services.voice.tts_provider_interface import BaseTTSProvider

logger = logging.getLogger(__name__)


class VoiceRealtimeSessionHandler:
    def __init__(
        self,
        websocket: WebSocket,
        stt_provider: BaseSTTProvider,
        tts_provider: BaseTTSProvider,
        orchestrator: CompanionOrchestrator,
        db: Any = None,
        already_accepted: bool = False,
    ):
        self.websocket = websocket
        self.stt = stt_provider
        self.tts = tts_provider
        self.orchestrator = orchestrator
        self.db = db
        self.already_accepted = already_accepted

        self.session_id: str = str(uuid.uuid4())
        self.user_id: str = "default_user"
        self.companion_id: str = "default_companion"
        self.conversation_id: str = "default"
        self.is_active: bool = False
        self.current_turn_task: Optional[asyncio.Task] = None
        self._cancel_requested: bool = False

    async def send_event(self, event_type: str, data: Optional[dict] = None):
        """Helper to send structured JSON events over WebSocket."""
        payload = {
            "event": event_type,
            "session_id": self.session_id,
            "timestamp": int(time.time() * 1000),
            **(data or {}),
        }
        try:
            await self.websocket.send_text(json.dumps(payload, ensure_ascii=False))
        except Exception as e:
            logger.debug(f"[RealtimeChannel] Failed to send event {event_type}: {e}")

    async def run(self):
        """Main WebSocket loop handling incoming client events."""
        if not self.already_accepted:
            await self.websocket.accept()
        self.is_active = True
        client_host = getattr(self.websocket.client, "host", "unknown") if hasattr(self.websocket, "client") and self.websocket.client else "unknown"
        client_port = getattr(self.websocket.client, "port", "") if hasattr(self.websocket, "client") and self.websocket.client else ""
        logger.info(f"[RealtimeChannel][WS-SERVER] 🔌 Client connected from {client_host}:{client_port} (Session: {self.session_id})")

        try:
            while self.is_active:
                raw_msg = await self.websocket.receive_text()
                try:
                    msg = json.loads(raw_msg)
                except Exception:
                    await self.send_event("error", {"message": "Invalid JSON format"})
                    continue

                event = msg.get("event")
                if not event:
                    continue

                if event == "session.start":
                    await self._handle_session_start(msg)
                elif event == "audio.send" or event == "audio.chunk":
                    await self._handle_audio_send(msg)
                elif event == "interruption":
                    await self._handle_interruption(msg)
                elif event == "ping":
                    await self.send_event("pong", {"client_time": msg.get("timestamp")})
                elif event == "session.end":
                    logger.info(f"[RealtimeChannel][WS-SERVER] Session {self.session_id} ended by client.")
                    await self.send_event("session.ended")
                    break
                else:
                    logger.debug(f"[RealtimeChannel][WS-SERVER] Unhandled event: {event}")

        except WebSocketDisconnect as ws_disc:
            logger.info(f"[RealtimeChannel][WS-SERVER] 🔌 Client disconnected (Session: {self.session_id}, code: {getattr(ws_disc, 'code', 'unknown')})")
        except Exception as e:
            logger.error(f"[RealtimeChannel][WS-SERVER] WebSocket loop error: {e}")
        finally:
            self.is_active = False
            if self.current_turn_task and not self.current_turn_task.done():
                self.current_turn_task.cancel()

    async def _handle_session_start(self, msg: dict):
        self.session_id = msg.get("session_id") or self.session_id
        self.user_id = msg.get("user_id") or self.user_id
        self.companion_id = msg.get("companion_id") or self.companion_id
        self.conversation_id = msg.get("conversation_id") or self.conversation_id

        logger.info(f"[RealtimeChannel][WS-SERVER] 📥 session.start received: user={self.user_id}, companion={self.companion_id}, session_id={self.session_id}")
        await self.send_event("session.ready", {
            "status": "ready",
            "user_id": self.user_id,
            "companion_id": self.companion_id,
            "conversation_id": self.conversation_id,
        })

    async def _handle_interruption(self, msg: dict):
        """Immediate Barge-in interruption cancellation."""
        logger.info(f"[RealtimeChannel] ✋ Interruption received for session {self.session_id}")
        self._cancel_requested = True
        if self.current_turn_task and not self.current_turn_task.done():
            self.current_turn_task.cancel()
        await self.send_event("interrupted", {"reason": "user_barge_in"})

    async def _handle_audio_send(self, msg: dict):
        """Processes user voice audio turn via STT -> Chunked LLM -> Parallel TTS Audio Chunk Stream."""
        # Cancel any previous turn if still running
        if self.current_turn_task and not self.current_turn_task.done():
            self.current_turn_task.cancel()

        self._cancel_requested = False
        self.current_turn_task = asyncio.create_task(self._process_voice_turn(msg))

    async def _process_voice_turn(self, msg: dict):
        audio_b64 = msg.get("audio_base64", "")
        if not audio_b64:
            await self.send_event("error", {"message": "Empty audio data"})
            return

        image_b64 = msg.get("image_base64")
        camera_timestamp_ms = msg.get("camera_timestamp_ms")

        try:
            audio_bytes = base64.b64decode(audio_b64)
            image_bytes = base64.b64decode(image_b64.split(",")[-1]) if image_b64 else None
        except Exception as decode_err:
            await self.send_event("error", {"message": f"Base64 decode failed: {decode_err}"})
            return

        t_turn_start = time.perf_counter()

        # 1. STT Transcribe
        await self.send_event("transcript.start")
        try:
            transcript = await self.stt.transcribe(audio_bytes)
        except Exception as stt_err:
            logger.error(f"[RealtimeChannel] STT failed: {stt_err}")
            await self.send_event("error", {"message": f"STT failed: {stt_err}"})
            return

        if self._cancel_requested:
            return

        transcript = transcript or ""
        logger.info(f"[RealtimeChannel] 🎙️ STT Transcribed: '{transcript}'")
        await self.send_event("transcript.final", {"transcript": transcript})

        if not transcript.strip():
            cid_lower = self.companion_id.lower()
            if "mani" in cid_lower or "마니" in self.companion_id:
                response_text = "아빠, 목소리가 잘 안 들렸어요! 마이크 가까이에서 다시 한번 말씀해 주세요! 😊"
            elif "hana" in cid_lower or "하나" in self.companion_id:
                response_text = "목소리가 잘 안 들렸어! 마이크 가까이에서 다시 말해줄래?"
            else:
                response_text = "여보, 목소리가 잘 안 들렸어요. 마이크 가까이에서 다시 한번 말씀해 주실래요?"

            audio_data = await self.tts.synthesize(response_text)
            audio_out_b64 = base64.b64encode(audio_data).decode("utf-8") if audio_data else ""
            await self.send_event("audio.chunk", {
                "sequence_index": 0,
                "text": response_text,
                "audio_base64": audio_out_b64,
                "is_last": True,
            })
            await self.send_event("response.end", {"full_text": response_text, "duration_ms": 0})
            return

        # 2. Package NormalizedInput
        metadata = {
            "voice_session_id": self.session_id,
            "realtime_channel": True,
        }
        if image_bytes:
            metadata["image_data"] = image_bytes
            metadata["has_camera_frame"] = True
        if camera_timestamp_ms:
            metadata["camera_timestamp_ms"] = camera_timestamp_ms

        normalized_input = NormalizedInput(
            interaction_id=f"INT-WS-{uuid.uuid4().hex[:8]}",
            user_id=self.user_id,
            companion_id=self.companion_id,
            conversation_id=self.conversation_id,
            input_type=InputType.VOICE,
            content=transcript,
            metadata=metadata,
        )

        # 3. Resolve Voice Context
        selected_voice = "ko-KR-SunHiNeural"
        speaking_rate_str = "+0%"
        pitch_offset_str = "+0Hz"
        cid_lower = self.companion_id.lower()
        if "mani" in cid_lower or "마니" in self.companion_id:
            selected_voice = "ko-KR-JiMinNeural"
            speaking_rate_str = "+5%"
            pitch_offset_str = "+2Hz"
        elif "hana" in cid_lower or "하나" in self.companion_id:
            selected_voice = "ko-KR-SeoHyeonNeural"

        voice_context = {
            "voice_id": selected_voice,
            "edge_tts_voice": selected_voice,
            "speaking_rate_str": speaking_rate_str,
            "pitch_offset_str": pitch_offset_str,
        }

        # 4. Stream LLM Chunks and Parallel TTS Audio Chunks
        await self.send_event("response.start")
        sequence_index = 0
        full_response_text = ""
        t_llm_start = time.perf_counter()
        stt_duration_ms = (t_llm_start - t_turn_start) * 1000
        first_chunk_ms = 0.0
        first_audio_ms = 0.0

        try:
            async for chunk_text, is_last, av_state, current_full in self.orchestrator.process_interaction_stream_chunks(normalized_input):
                if self._cancel_requested:
                    logger.info("[RealtimeChannel][WS-SERVER] Turn processing aborted due to interruption.")
                    return

                full_response_text = current_full
                clean_chunk = chunk_text.strip()
                if not clean_chunk:
                    continue

                if sequence_index == 0:
                    first_chunk_ms = (time.perf_counter() - t_llm_start) * 1000
                    logger.info(f"[RealtimeChannel][WS-SERVER] ⚡ First Chunk Ready in {first_chunk_ms:.1f}ms: '{clean_chunk}'")

                # Emit Text Delta Event
                await self.send_event("response.chunk", {
                    "sequence_index": sequence_index,
                    "delta": chunk_text,
                    "avatar_state": av_state,
                })

                # Synthesize & Emit Audio Chunk in Parallel
                voice_context["avatar_state"] = av_state
                try:
                    t_tts_chunk_start = time.perf_counter()
                    chunk_audio = await self.tts.synthesize(clean_chunk, voice_context=voice_context)
                    chunk_audio_b64 = base64.b64encode(chunk_audio).decode("utf-8") if chunk_audio else ""
                    
                    if sequence_index == 0:
                        first_audio_ms = (time.perf_counter() - t_turn_start) * 1000
                        tts_first_ms = (time.perf_counter() - t_tts_chunk_start) * 1000
                        logger.info(f"[RealtimeChannel][WS-SERVER] 🔊 First Audio Chunk Ready in {first_audio_ms:.1f}ms from turn start (TTS: {tts_first_ms:.1f}ms, size: {len(chunk_audio or b'')}B)")

                    await self.send_event("audio.chunk", {
                        "sequence_index": sequence_index,
                        "text": clean_chunk,
                        "audio_base64": chunk_audio_b64,
                        "is_last": is_last,
                        "avatar_state": av_state,
                    })
                    sequence_index += 1
                except Exception as tts_err:
                    logger.warning(f"[RealtimeChannel][WS-SERVER] TTS chunk synthesis error: {tts_err}")

            t_turn_end = time.perf_counter()
            total_duration_ms = (t_turn_end - t_turn_start) * 1000
            await self.send_event("response.end", {
                "full_text": full_response_text,
                "total_chunks": sequence_index,
                "duration_ms": total_duration_ms,
            })
            logger.info(f"[RealtimeChannel][WS-SERVER] 🏁 Turn finished in {total_duration_ms:.1f}ms | STT: {stt_duration_ms:.1f}ms | First Chunk: {first_chunk_ms:.1f}ms | First Audio: {first_audio_ms:.1f}ms | Chunks: {sequence_index}")

        except asyncio.CancelledError:
            logger.info("[RealtimeChannel] Turn task cancelled.")
        except Exception as turn_err:
            logger.error(f"[RealtimeChannel] Voice turn processing error: {turn_err}")
            await self.send_event("error", {"message": str(turn_err)})
