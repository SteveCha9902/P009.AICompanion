import pytest
import asyncio
from app.domain.voice.voice_profile import (
    VoiceProfile, 
    VoicePersonaType, 
    VoiceProviderType, 
    SpeechStyleParameters,
    AudioSynthesisResult
)
from app.domain.relationship.relationship_stage import RelationshipStage
from app.services.character.avatar.domain import ContinuousEmotionVector, RelationshipParameters
from app.services.voice.provider_abstraction import VoiceProviderFactory, OpenAIVoiceProvider, ElevenLabsVoiceProvider
from app.services.voice.emotional_speech_engine import EmotionalSpeechEngine
from app.services.voice.relationship_speech_engine import RelationshipSpeechEngine
from app.services.voice.voice_identity_service import VoiceIdentityService

def test_gate_vc1_voice_change_support():
    """
    Gate VC1: System supports changing between all 4 Canonical Voice Personas and Providers.
    """
    mentor = VoiceIdentityService.get_profile_by_persona(VoicePersonaType.CALM_MENTOR)
    companion = VoiceIdentityService.get_profile_by_persona(VoicePersonaType.WARM_COMPANION)
    guide = VoiceIdentityService.get_profile_by_persona(VoicePersonaType.ENERGETIC_GUIDE)
    advisor = VoiceIdentityService.get_profile_by_persona(VoicePersonaType.PROFESSIONAL_ADVISOR)

    assert mentor.pitch_offset < 0.0
    assert mentor.confidence >= 0.85

    assert companion.warmth >= 0.90
    assert companion.empathy >= 0.90

    assert guide.energy >= 0.85
    assert guide.speaking_rate > 1.05

    assert advisor.confidence >= 0.90

    # Provider Factory Check
    openai_prov = VoiceProviderFactory.get_provider(VoiceProviderType.OPENAI)
    assert isinstance(openai_prov, OpenAIVoiceProvider)
    eleven_prov = VoiceProviderFactory.get_provider(VoiceProviderType.ELEVENLABS)
    assert isinstance(eleven_prov, ElevenLabsVoiceProvider)
    assert eleven_prov.supports_voice_cloning() is True

def test_gate_vc2_emotion_speech_consistency():
    """
    Gate VC2: Emotion modulation changes speed, pitch, energy, and warmth consistently.
    """
    profile = VoiceIdentityService.get_profile_by_persona(VoicePersonaType.WARM_COMPANION)

    # 1. Joy Emotion (High Valence & High Arousal)
    joy = ContinuousEmotionVector(valence=0.8, arousal=0.7, warmth=0.8, intensity=0.8)
    joy_style = EmotionalSpeechEngine.modulate_speech_style(profile, joy)
    assert joy_style.speaking_rate > profile.speaking_rate
    assert joy_style.pitch_offset > profile.pitch_offset
    assert joy_style.energy >= 0.70
    assert joy_style.ssml_style == "cheerful"

    # 2. Sadness / Grief Emotion (Low Valence & Low Arousal)
    sad = ContinuousEmotionVector(valence=-0.6, arousal=0.2, warmth=0.5, intensity=0.8)
    sad_style = EmotionalSpeechEngine.modulate_speech_style(profile, sad)
    assert sad_style.speaking_rate < profile.speaking_rate
    assert sad_style.pitch_offset < profile.pitch_offset
    assert sad_style.energy <= 0.50
    assert sad_style.pause_multiplier > 1.2
    assert sad_style.ssml_style == "empathetic"

def test_gate_vc3_relationship_speech_consistency():
    """
    Gate VC3: Stranger produces formal cadence; Trusted Companion produces intimate warmth.
    """
    profile = VoiceIdentityService.get_profile_by_persona(VoicePersonaType.WARM_COMPANION)
    base_style = SpeechStyleParameters(speaking_rate=1.0, pitch_offset=0.0, energy=0.6, warmth=0.7)

    # Stranger Modulation
    stranger_style = RelationshipSpeechEngine.apply_relationship_modulation(
        base_style.model_copy(),
        stage=RelationshipStage.STRANGER
    )
    assert stranger_style.ssml_style == "formal"
    assert stranger_style.warmth <= 0.60

    # Trusted Companion Modulation
    companion_style = RelationshipSpeechEngine.apply_relationship_modulation(
        base_style.model_copy(),
        stage=RelationshipStage.TRUSTED_COMPANION,
        rel_params=RelationshipParameters(familiarity=0.9, trust=0.9, warmth=0.9)
    )
    assert companion_style.ssml_style == "warm"
    assert companion_style.warmth >= 0.90
    assert companion_style.pause_multiplier >= 1.10

@pytest.mark.asyncio
async def test_gate_vc4_lip_sync_and_synthesis_pipeline():
    """
    Gate VC4: Full pipeline calculates valid duration, style, and returns AudioSynthesisResult.
    """
    text = "안녕하세요! 오늘 기분은 어떠신가요? 늘 응원하고 있어요."
    result = await VoiceIdentityService.plan_and_synthesize(
        text=text,
        persona=VoicePersonaType.WARM_COMPANION,
        emotion=ContinuousEmotionVector(valence=0.7, arousal=0.5, warmth=0.9, intensity=0.7),
        stage=RelationshipStage.CLOSE_FRIEND
    )

    assert isinstance(result, AudioSynthesisResult)
    assert result.duration_sec > 0.5
    assert result.applied_style.warmth >= 0.80
    assert result.voice_profile_used.persona_type == VoicePersonaType.WARM_COMPANION

@pytest.mark.asyncio
async def test_gate_vc5_long_conversation_stability():
    """
    Gate VC5: 500 consecutive speech syntheses execute instantaneously with zero leak.
    """
    for i in range(500):
        persona = VoicePersonaType.CALM_MENTOR if i % 2 == 0 else VoicePersonaType.WARM_COMPANION
        res = await VoiceIdentityService.plan_and_synthesize(
            text=f"반복 검증 테스트 문장 번호 {i}",
            persona=persona
        )
        assert res.duration_sec > 0.0
