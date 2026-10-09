import os
import io
import logging
from typing import AsyncGenerator, Optional, Dict, Any

from app.services.voice.stt_provider_interface import BaseSTTProvider
from app.services.voice.tts_provider_interface import BaseTTSProvider
from app.services.llm.base import (
    LLMProviderError,
    LLMAuthError,
    LLMTimeoutError,
    LLMRateLimitError
)

try:
    import openai
    from openai import AsyncOpenAI
except ImportError:
    openai = None
    AsyncOpenAI = None

logger = logging.getLogger(__name__)

class OpenAI_STTProvider(BaseSTTProvider):
    """
    Production OpenAI Whisper STT Adapter.
    Handles audio transcription with empty checks, language support, and error normalization.
    """
    def __init__(self, api_key: Optional[str] = None, timeout_seconds: float = 20.0):
        if AsyncOpenAI is None:
            raise LLMProviderError("OpenAI SDK is not installed.", code="PROVIDER_CONFIG_ERROR")
        
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self.timeout_seconds = timeout_seconds

        if not self.api_key:
            logger.warning("[OpenAI_STTProvider] OPENAI_API_KEY is missing.")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key, timeout=self.timeout_seconds)

    def _ensure_client(self):
        if not self.client:
            raise LLMAuthError("OPENAI_API_KEY is missing for STT Provider.")

    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio bytes to text using OpenAI Whisper."""
        if audio_data is None or len(audio_data) == 0:
            return ""
        
        self._ensure_client()

        try:
            filename = "recording.m4a"
            content_type = "audio/m4a"
            if audio_data.startswith(b"RIFF"):
                filename = "recording.wav"
                content_type = "audio/wav"
            elif audio_data.startswith(b"ID3") or audio_data[:2] == b"\xff\xfb":
                filename = "recording.mp3"
                content_type = "audio/mpeg"
            elif audio_data.startswith(b"OggS"):
                filename = "recording.ogg"
                content_type = "audio/ogg"
            elif b"ftyp" in audio_data[:32]:
                filename = "recording.m4a"
                content_type = "audio/m4a"
            elif audio_data.startswith(b"\x1a\x45\xdf\xa3"):
                filename = "recording.webm"
                content_type = "audio/webm"

            logger.info(f"[OpenAI_STTProvider] Sending {len(audio_data)} bytes as '{filename}' ({content_type}) to Whisper-1 (ko)...")
            response = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=(filename, audio_data, content_type),
                language="ko"
            )
            result_text = response.text.strip() if response.text else ""
            logger.info(f"[OpenAI_STTProvider] Whisper-1 transcribed successfully: '{result_text}'")
            return result_text

        except openai.BadRequestError as e:
            logger.warning(f"[OpenAI_STTProvider] Whisper BadRequest / short audio ({e}). Treating as silent input.")
            return ""
        except openai.AuthenticationError as e:
            logger.error(f"[OpenAI_STTProvider] Auth failed: {e}")
            raise LLMAuthError(f"STT Authentication failed: {e}", original_error=e)
        except (openai.APITimeoutError, TimeoutError) as e:
            logger.error(f"[OpenAI_STTProvider] Timeout: {e}")
            raise LLMTimeoutError(f"STT Request Timed out: {e}", original_error=e)
        except Exception as e:
            logger.error(f"[OpenAI_STTProvider] Transcribe failed: {e}")
            raise LLMProviderError(f"STT Error: {e}", code="PROVIDER_STT_ERROR", original_error=e)

    async def transcribe_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        full_audio = bytearray()
        async for chunk in audio_stream:
            full_audio.extend(chunk)
        result = await self.transcribe(bytes(full_audio))
        yield result


class OpenAI_TTSProvider(BaseTTSProvider):
    """
    Production OpenAI TTS Adapter (tts-1).
    Synthesizes speech audio from text with voice selection and error normalization.
    """
    def __init__(self, api_key: Optional[str] = None, timeout_seconds: float = 20.0):
        if AsyncOpenAI is None:
            raise LLMProviderError("OpenAI SDK is not installed.", code="PROVIDER_CONFIG_ERROR")
        
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self.timeout_seconds = timeout_seconds

        if not self.api_key:
            logger.warning("[OpenAI_TTSProvider] OPENAI_API_KEY is missing.")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key, timeout=self.timeout_seconds)

    def _ensure_client(self):
        if not self.client:
            raise LLMAuthError("OPENAI_API_KEY is missing for TTS Provider.")

    async def synthesize(self, text: str, voice_context: Optional[dict] = None) -> bytes:
        """Synthesize text into speech audio bytes."""
        self._ensure_client()

        if not text or not text.strip():
            logger.warning("[OpenAI_TTSProvider] Empty text received for synthesis.")
            return b""

        voice = (voice_context or {}).get("voice_id") or os.getenv("TTS_VOICE_ID", "nova")
        model = (voice_context or {}).get("model", "tts-1")

        try:
            response = await self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text.strip(),
                response_format="wav"
            )
            return response.content if hasattr(response, "content") else response.read()

        except openai.AuthenticationError as e:
            logger.error(f"[OpenAI_TTSProvider] Auth failed: {e}")
            raise LLMAuthError(f"TTS Authentication failed: {e}", original_error=e)
        except (openai.APITimeoutError, TimeoutError) as e:
            logger.error(f"[OpenAI_TTSProvider] Timeout: {e}")
            raise LLMTimeoutError(f"TTS Request Timed out: {e}", original_error=e)
        except Exception as e:
            logger.error(f"[OpenAI_TTSProvider] Synthesize failed: {e}")
            raise LLMProviderError(f"TTS Error: {e}", code="PROVIDER_TTS_ERROR", original_error=e)

    async def synthesize_stream(self, text: str, voice_context: Optional[dict] = None) -> AsyncGenerator[bytes, None]:
        audio_bytes = await self.synthesize(text, voice_context=voice_context)
        if audio_bytes:
            yield audio_bytes
