from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from app.domain.voice.voice_profile import VoiceProfile, SpeechStyleParameters, AudioSynthesisResult, VoiceProviderType

logger = logging.getLogger(__name__)

class BaseVoiceProvider(ABC):
    """
    Standard Abstract Interface for Voice TTS Providers.
    Decouples Character Voice Engine from specific TTS Vendors.
    """
    
    @abstractmethod
    async def synthesize(
        self, 
        text: str, 
        voice_profile: VoiceProfile, 
        style: SpeechStyleParameters
    ) -> AudioSynthesisResult:
        pass

    @abstractmethod
    def supports_ssml(self) -> bool:
        pass

    @abstractmethod
    def supports_voice_cloning(self) -> bool:
        pass


class OpenAIVoiceProvider(BaseVoiceProvider):
    """
    OpenAI Audio TTS Provider (alloy, echo, fable, onyx, nova, shimmer).
    Fast, natural, low latency, standard pricing.
    """
    async def synthesize(
        self, 
        text: str, 
        voice_profile: VoiceProfile, 
        style: SpeechStyleParameters
    ) -> AudioSynthesisResult:
        # Maps profile persona to OpenAI voice models
        voice_mapping = {
            "CALM_MENTOR": "onyx",
            "WARM_COMPANION": "nova",
            "ENERGETIC_GUIDE": "shimmer",
            "PROFESSIONAL_ADVISOR": "alloy"
        }
        selected_voice = voice_mapping.get(voice_profile.persona_type.value, "nova")
        
        # Approximate duration based on word count & speaking rate
        words = len(text.split())
        est_duration = max(0.8, (words / (2.5 * style.speaking_rate)))
        
        return AudioSynthesisResult(
            audio_format="mp3",
            audio_base64=None,
            duration_sec=round(est_duration, 2),
            visemes=[],
            voice_profile_used=voice_profile,
            applied_style=style
        )

    def supports_ssml(self) -> bool:
        return False

    def supports_voice_cloning(self) -> bool:
        return False


class ElevenLabsVoiceProvider(BaseVoiceProvider):
    """
    ElevenLabs Voice Provider (Hyper-realistic expressive AI speech + Voice Cloning).
    """
    async def synthesize(
        self, 
        text: str, 
        voice_profile: VoiceProfile, 
        style: SpeechStyleParameters
    ) -> AudioSynthesisResult:
        words = len(text.split())
        est_duration = max(0.8, (words / (2.5 * style.speaking_rate)))
        
        return AudioSynthesisResult(
            audio_format="mp3",
            audio_base64=None,
            duration_sec=round(est_duration, 2),
            visemes=[],
            voice_profile_used=voice_profile,
            applied_style=style
        )

    def supports_ssml(self) -> bool:
        return True

    def supports_voice_cloning(self) -> bool:
        return True


class AzureSpeechVoiceProvider(BaseVoiceProvider):
    """
    Azure Cognitive Speech Provider (Rich SSML, precise viseme stream, 100+ languages).
    """
    async def synthesize(
        self, 
        text: str, 
        voice_profile: VoiceProfile, 
        style: SpeechStyleParameters
    ) -> AudioSynthesisResult:
        words = len(text.split())
        est_duration = max(0.8, (words / (2.5 * style.speaking_rate)))
        
        return AudioSynthesisResult(
            audio_format="wav",
            audio_base64=None,
            duration_sec=round(est_duration, 2),
            visemes=[],
            voice_profile_used=voice_profile,
            applied_style=style
        )

    def supports_ssml(self) -> bool:
        return True

    def supports_voice_cloning(self) -> bool:
        return True


class VoiceProviderFactory:
    _providers: Dict[VoiceProviderType, BaseVoiceProvider] = {
        VoiceProviderType.OPENAI: OpenAIVoiceProvider(),
        VoiceProviderType.ELEVENLABS: ElevenLabsVoiceProvider(),
        VoiceProviderType.AZURE: AzureSpeechVoiceProvider(),
        VoiceProviderType.MOCK: OpenAIVoiceProvider()
    }

    @classmethod
    def get_provider(cls, provider_type: VoiceProviderType) -> BaseVoiceProvider:
        return cls._providers.get(provider_type, cls._providers[VoiceProviderType.OPENAI])
