import os
import logging
try:
    import edge_tts
except ImportError:
    edge_tts = None
from typing import Optional
from app.services.voice.tts_provider_interface import BaseTTSProvider

logger = logging.getLogger(__name__)

# Representative Korean Neural Voices
# - ko-KR-SunHiNeural: 부드럽고 따뜻하며 포근한 여성 톤 (기본값)
# - ko-KR-JiMinNeural: 밝고 애교 넘치며 상냥한 여성 톤
# - ko-KR-InJoonNeural: 부드럽고 다정한 남성 톤
# - ko-KR-HyunsuNeural: 차분하고 진중한 남성 톤

class EdgeTTSProvider(BaseTTSProvider):
    """
    Microsoft Edge-TTS Neural Voice Provider (100% Free & High Quality Emotive Korean).
    """

    def __init__(self, default_voice: Optional[str] = None):
        self.default_voice = default_voice or os.getenv("EDGE_TTS_VOICE", "ko-KR-SunHiNeural")

    async def synthesize(self, text: str, voice_context: Optional[dict] = None) -> bytes:
        if edge_tts is None:
            raise RuntimeError("edge-tts is not installed. Please install edge-tts or use MockTTSProvider.")
        if not text or not text.strip():
            logger.warning("[EdgeTTSProvider] Empty text received.")
            return b""

        # Voice selection priority: voice_context > env > default (SunHi)
        selected_voice = (
            (voice_context or {}).get("edge_tts_voice")
            or (voice_context or {}).get("voice_id")
            or os.getenv("EDGE_TTS_VOICE")
            or self.default_voice
        )

        # Fallback if an OpenAI voice name was passed
        if not selected_voice.startswith("ko-KR-"):
            if selected_voice in ("nova", "shimmer", "alloy", "WARM_COMPANION"):
                selected_voice = "ko-KR-SunHiNeural"
            elif selected_voice in ("echo", "onyx", "fable"):
                selected_voice = "ko-KR-InJoonNeural"
            else:
                selected_voice = "ko-KR-SunHiNeural"

        # Rate and Pitch adjustments
        rate = (voice_context or {}).get("speaking_rate_str") or os.getenv("EDGE_TTS_RATE", "-2%")
        pitch = (voice_context or {}).get("pitch_offset_str") or os.getenv("EDGE_TTS_PITCH", "+0Hz")

        logger.info(f"[EdgeTTSProvider] Synthesizing speech with voice: {selected_voice} (rate: {rate}, pitch: {pitch})")

        try:
            communicate = edge_tts.Communicate(
                text=text.strip(),
                voice=selected_voice,
                rate=rate,
                pitch=pitch
            )
            
            audio_bytes = bytearray()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes.extend(chunk["data"])

            return bytes(audio_bytes)

        except Exception as e:
            logger.error(f"[EdgeTTSProvider] Synthesis failed: {e}")
            return b""

    async def synthesize_stream(self, text: str, voice_context: Optional[dict] = None):
        if not text or not text.strip():
            return

        selected_voice = (
            (voice_context or {}).get("edge_tts_voice")
            or (voice_context or {}).get("voice_id")
            or os.getenv("EDGE_TTS_VOICE")
            or self.default_voice
        )

        if not selected_voice.startswith("ko-KR-"):
            if selected_voice in ("nova", "shimmer", "alloy", "WARM_COMPANION"):
                selected_voice = "ko-KR-SunHiNeural"
            elif selected_voice in ("echo", "onyx", "fable"):
                selected_voice = "ko-KR-InJoonNeural"
            else:
                selected_voice = "ko-KR-SunHiNeural"

        rate = os.getenv("EDGE_TTS_RATE", "-2%")
        pitch = os.getenv("EDGE_TTS_PITCH", "+0Hz")

        communicate = edge_tts.Communicate(
            text=text.strip(),
            voice=selected_voice,
            rate=rate,
            pitch=pitch
        )

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
