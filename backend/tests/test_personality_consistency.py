import pytest
from app.domain.character.personality_profile import PersonalityProfile
from app.services.character.character_state_resolver import CharacterStateResolver

def test_gate_c3_emotion_separation_without_personality_mutation():
    """
    Gate C3: Emotion changes must modulate situational expression but NEVER mutate the persistent personality DNA.
    """
    static_personality = PersonalityProfile(
        mbti_type="INFJ",
        warmth=0.88,
        intellectuality=0.91,
        humor_level=0.55
    )

    # 1. Happy / Excited state
    state_happy = CharacterStateResolver.resolve(
        companion_id="default_companion",
        personality=static_personality,
        current_mood="happy",
        emotional_arousal=0.8,
        relationship_level="FRIEND"
    )

    # 2. Concerned / Sad state
    state_sad = CharacterStateResolver.resolve(
        companion_id="default_companion",
        personality=static_personality,
        current_mood="concerned",
        emotional_arousal=0.3,
        relationship_level="FRIEND"
    )

    # Persistent personality values must remain untouched
    assert static_personality.warmth == 0.88
    assert static_personality.humor_level == 0.55

    # Situational warmth & humor should vary logically
    assert state_happy.effective_warmth > state_sad.effective_warmth
    assert state_happy.effective_humor > state_sad.effective_humor
    assert state_happy.active_mbti == "INFJ"
    assert state_sad.active_mbti == "INFJ"
