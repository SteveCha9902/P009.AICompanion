from typing import Optional
from app.domain.character.personality_profile import PersonalityProfile
from app.domain.character.character_state import CharacterState, ResponseStrategy

class CharacterStateResolver:
    """
    Combines static Personality DNA with dynamic runtime states (Emotion, Relationship, Mood)
    to calculate the effective situational behavior without mutating the persistent personality.
    """

    @staticmethod
    def resolve(
        companion_id: str,
        personality: PersonalityProfile,
        current_mood: str = "neutral",
        emotional_valence: float = 0.0,
        emotional_arousal: float = 0.5,
        relationship_level: str = "FRIEND",
        strategy: Optional[ResponseStrategy] = None
    ) -> CharacterState:
        # 1. Warmth modulation by Relationship & Mood
        rel_boost = 0.1 if relationship_level in ["CLOSE_FRIEND", "CONFIDANT", "SOULMATE"] else 0.0
        mood_boost = 0.08 if current_mood in ["happy", "excited", "warm"] else (-0.05 if current_mood in ["sad", "concerned"] else 0.0)
        effective_warmth = max(0.0, min(1.0, personality.warmth + rel_boost + mood_boost))

        # 2. Intellectuality modulation
        mood_int = 0.05 if current_mood in ["reflective", "curious", "focused"] else 0.0
        effective_intellectuality = max(0.0, min(1.0, personality.intellectuality + mood_int))

        # 3. Humor modulation by Energy/Arousal & Mood
        humor_mod = 0.1 if current_mood in ["playful", "happy"] and emotional_arousal > 0.5 else (-0.2 if current_mood in ["sad", "angry", "concerned"] else 0.0)
        effective_humor = max(0.0, min(1.0, personality.humor_level + humor_mod))

        # 4. Directness
        effective_directness = personality.communication_directness

        return CharacterState(
            companion_id=companion_id,
            active_mbti=personality.mbti_type or "INFJ",
            effective_warmth=round(effective_warmth, 2),
            effective_intellectuality=round(effective_intellectuality, 2),
            effective_humor=round(effective_humor, 2),
            effective_directness=round(effective_directness, 2),
            current_mood=current_mood,
            relationship_level=relationship_level,
            active_strategy=strategy or ResponseStrategy()
        )
