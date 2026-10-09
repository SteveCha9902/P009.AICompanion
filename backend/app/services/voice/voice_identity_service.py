from typing import Optional, Dict, Any
import logging
from app.domain.voice.voice_profile import (
    VoiceProfile, 
    VoicePersonaType, 
    VoiceProviderType, 
    SpeechStyleParameters, 
    AudioSynthesisResult
)
from app.domain.relationship.relationship_stage import RelationshipStage
from app.services.character.avatar.domain import ContinuousEmotionVector, RelationshipParameters
from app.services.voice.provider_abstraction import VoiceProviderFactory
from app.services.voice.emotional_speech_engine import EmotionalSpeechEngine
from app.services.voice.relationship_speech_engine import RelationshipSpeechEngine

logger = logging.getLogger(__name__)

class VoiceIdentityService:
    """
    Central Coordinator for Voice Persona, Emotional Prosody, and TTS Execution.
    """
    
    # 4 Canonical Voice Profiles
    PERSONA_PROFILES: Dict[VoicePersonaType, VoiceProfile] = {
        VoicePersonaType.CALM_MENTOR: VoiceProfile(
            voice_id="mentor_calm_v1",
            persona_type=VoicePersonaType.CALM_MENTOR,
            provider=VoiceProviderType.OPENAI,
            warmth=0.75,
            energy=0.45,
            confidence=0.90,
            empathy=0.80,
            speaking_rate=0.95,
            pitch_offset=-2.0
        ),
        VoicePersonaType.WARM_COMPANION: VoiceProfile(
            voice_id="genie_warm_v1",
            persona_type=VoicePersonaType.WARM_COMPANION,
            provider=VoiceProviderType.OPENAI,
            warmth=0.92,
            energy=0.65,
            confidence=0.80,
            empathy=0.95,
            speaking_rate=1.0,
            pitch_offset=0.5
        ),
        VoicePersonaType.ENERGETIC_GUIDE: VoiceProfile(
            voice_id="guide_spark_v1",
            persona_type=VoicePersonaType.ENERGETIC_GUIDE,
            provider=VoiceProviderType.OPENAI,
            warmth=0.70,
            energy=0.90,
            confidence=0.85,
            empathy=0.70,
            speaking_rate=1.12,
            pitch_offset=2.5
        ),
        VoicePersonaType.PROFESSIONAL_ADVISOR: VoiceProfile(
            voice_id="advisor_pro_v1",
            persona_type=VoicePersonaType.PROFESSIONAL_ADVISOR,
            provider=VoiceProviderType.OPENAI,
            warmth=0.60,
            energy=0.70,
            confidence=0.95,
            empathy=0.65,
            speaking_rate=1.02,
            pitch_offset=-0.5
        )
    }

    @classmethod
    def get_profile_by_persona(cls, persona: VoicePersonaType) -> VoiceProfile:
        return cls.PERSONA_PROFILES.get(persona, cls.PERSONA_PROFILES[VoicePersonaType.WARM_COMPANION])

    @classmethod
    async def plan_and_synthesize(
        cls,
        text: str,
        persona: VoicePersonaType = VoicePersonaType.WARM_COMPANION,
        provider_override: Optional[VoiceProviderType] = None,
        emotion: Optional[ContinuousEmotionVector] = None,
        stage: RelationshipStage = RelationshipStage.ACQUAINTANCE,
        relationship_params: Optional[RelationshipParameters] = None
    ) -> AudioSynthesisResult:
        """
        Full Pipeline: Profile ➔ Emotional Modulation ➔ Relationship Modulation ➔ TTS Provider Synthesize
        """
        base_profile = cls.get_profile_by_persona(persona)
        if provider_override:
            base_profile.provider = provider_override

        # Step 1: Modulate by Continuous Emotion
        emotional_style = EmotionalSpeechEngine.modulate_speech_style(base_profile, emotion)

        # Step 2: Modulate by Relationship Stage & Social Bond
        final_style = RelationshipSpeechEngine.apply_relationship_modulation(
            emotional_style, 
            stage=stage, 
            rel_params=relationship_params
        )

        # Step 3: Dispatch to Voice Provider
        provider = VoiceProviderFactory.get_provider(base_profile.provider)
        result = await provider.synthesize(text, base_profile, final_style)

        return result
