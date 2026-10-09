import os
import logging
import httpx
from typing import Optional
from app.services.voice.tts_provider_interface import BaseTTSProvider

logger = logging.getLogger(__name__)

class ElevenLabsTTSProvider(BaseTTSProvider):
    """
    ElevenLabs Multilingual v2 TTS & Voice Cloning Provider.
    Supports ultra-realistic emotive speech, whispers, and custom voice cloning.
    """

    def __init__(self, api_key: Optional[str] = None, default_voice_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "")
        self.default_voice_id = default_voice_id or os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM") # Rachel default
        self.model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

    async def synthesize(self, text: str, voice_context: Optional[dict] = None) -> bytes:
        if not text or not text.strip():
            logger.warning("[ElevenLabsTTSProvider] Empty text received.")
            return b""

        api_key = (voice_context or {}).get("elevenlabs_api_key") or self.api_key or os.getenv("ELEVENLABS_API_KEY", "")
        if not api_key:
            logger.error("[ElevenLabsTTSProvider] ELEVENLABS_API_KEY is missing.")
            return b""

        voice_id = (voice_context or {}).get("voice_id") or os.getenv("ELEVENLABS_VOICE_ID") or self.default_voice_id
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }

        payload = {
            "text": text.strip(),
            "model_id": self.model_id,
            "voice_settings": {
                "stability": 0.50,            # 감정 변화 표현도 (0.0~1.0)
                "similarity_boost": 0.85,     # 원본 목소리 유사도 (0.0~1.0)
                "style": 0.35,                # 감정 강조도
                "use_speaker_boost": True     # 선명도 강화
            }
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code != 200:
                    logger.error(f"[ElevenLabsTTSProvider] API Error ({response.status_code}): {response.text}")
                    return b""
                
                return response.content

        except Exception as e:
            logger.error(f"[ElevenLabsTTSProvider] Synthesis failed: {e}")
            return b""

    async def synthesize_stream(self, text: str, voice_context: Optional[dict] = None):
        audio_data = await self.synthesize(text, voice_context)
        if audio_data:
            yield audio_data
