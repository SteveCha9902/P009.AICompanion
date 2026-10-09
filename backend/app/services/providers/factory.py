import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv(override=True)


from app.services.llm.base import BaseLLMProvider, LLMResponse
from app.services.llm.openai import OpenAIProvider
from app.services.voice.stt_provider_interface import BaseSTTProvider
from app.services.voice.tts_provider_interface import BaseTTSProvider
from app.services.voice.adapters.mock_stt_adapter import MockSTTProvider
from app.services.voice.adapters.mock_tts_adapter import MockTTSProvider
from app.services.voice.adapters.openai_adapter import OpenAI_STTProvider, OpenAI_TTSProvider
from app.services.voice.adapters.elevenlabs_adapter import ElevenLabsTTSProvider
from app.services.voice.adapters.edge_tts_adapter import EdgeTTSProvider
from app.services.vision.provider_interface import BaseVisionProvider
from app.services.vision.adapters.mock_vision_adapter import MockVisionProvider
from app.services.memory.embedding import BaseEmbeddingProvider, OpenAIEmbeddingProvider, MockEmbeddingProvider

logger = logging.getLogger(__name__)

# Reusable Mock LLM Provider
class MockLLMProvider(BaseLLMProvider):
    def __init__(self, output_text: str = "안녕하세요! 오늘도 좋은 하루 보내고 계신가요? 무엇이든 편하게 이야기해주세요."):
        self.output_text = output_text

    async def generate(self, messages) -> LLMResponse:
        return LLMResponse(content=self.output_text, model="mock-model")

    async def stream(self, messages):
        words = self.output_text.split(" ")
        for word in words:
            yield LLMResponse(content=word + " ", model="mock-model")

class ProviderFactory:
    """
    Independent Provider Factory based on environment variables:
    - LLM_PROVIDER: 'openai' | 'mock'
    - STT_PROVIDER: 'openai' | 'mock'
    - TTS_PROVIDER: 'openai' | 'mock'
    - VISION_PROVIDER: 'cloud' | 'mock'
    - EMBEDDING_PROVIDER: 'openai' | 'mock'
    """

    @staticmethod
    def get_llm_provider(provider_type: Optional[str] = None) -> BaseLLMProvider:
        selected = (provider_type or os.getenv("LLM_PROVIDER", "mock")).lower()
        if selected == "openai":
            logger.info("[ProviderFactory] Instantiating OpenAIProvider.")
            return OpenAIProvider()
        return MockLLMProvider()

    @staticmethod
    def get_stt_provider(provider_type: Optional[str] = None) -> BaseSTTProvider:
        selected = (provider_type or os.getenv("STT_PROVIDER", "mock")).lower()
        if selected == "openai":
            logger.info("[ProviderFactory] Instantiating OpenAI_STTProvider.")
            return OpenAI_STTProvider()
        return MockSTTProvider()

    @staticmethod
    def get_tts_provider(provider_type: Optional[str] = None) -> BaseTTSProvider:
        selected = (provider_type or os.getenv("TTS_PROVIDER", "mock")).lower()
        if selected in ("edge_tts", "edgetts", "edge"):
            logger.info("[ProviderFactory] Instantiating EdgeTTSProvider (Free Emotive Korean Neural).")
            return EdgeTTSProvider()
        elif selected == "openai":
            logger.info("[ProviderFactory] Instantiating OpenAI_TTSProvider.")
            return OpenAI_TTSProvider()
        elif selected == "elevenlabs":
            logger.info("[ProviderFactory] Instantiating ElevenLabsTTSProvider.")
            return ElevenLabsTTSProvider()
        return MockTTSProvider()

    @staticmethod
    def get_vision_provider(provider_type: Optional[str] = None) -> BaseVisionProvider:
        selected = (provider_type or os.getenv("VISION_PROVIDER", "mock")).lower()
        if selected == "cloud":
            from app.services.vision.adapters.cloud_vision_adapter import CloudVisionProvider
            return CloudVisionProvider()
        return MockVisionProvider()

    @staticmethod
    def get_embedding_provider(provider_type: Optional[str] = None) -> BaseEmbeddingProvider:
        selected = (provider_type or os.getenv("EMBEDDING_PROVIDER", "mock")).lower()
        if selected == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("[ProviderFactory] OPENAI_API_KEY missing for embedding, fallback to MockEmbeddingProvider.")
                return MockEmbeddingProvider()
            return OpenAIEmbeddingProvider()
        return MockEmbeddingProvider()
