from typing import Dict
from app.services.character.traits import PersonalityTraitVector

class MBTIMapper:
    """
    Translates MBTI Types into Behavioral Biases rather than hardcoded deterministic constraints.
    """

    _MBTI_BIAS_REGISTRY: Dict[str, PersonalityTraitVector] = {
        "ENFP": PersonalityTraitVector(warmth=0.92, curiosity=0.95, playfulness=0.85, assertiveness=0.60, empathy=0.90),
        "ISTJ": PersonalityTraitVector(warmth=0.55, curiosity=0.50, playfulness=0.20, assertiveness=0.80, empathy=0.60),
        "INFJ": PersonalityTraitVector(warmth=0.90, curiosity=0.85, playfulness=0.40, assertiveness=0.50, empathy=0.95),
        "ENTP": PersonalityTraitVector(warmth=0.70, curiosity=0.98, playfulness=0.90, assertiveness=0.85, empathy=0.65),
        "ISFJ": PersonalityTraitVector(warmth=0.90, curiosity=0.60, playfulness=0.35, assertiveness=0.45, empathy=0.92),
        "ESTJ": PersonalityTraitVector(warmth=0.50, curiosity=0.55, playfulness=0.30, assertiveness=0.95, empathy=0.50),
        "INFP": PersonalityTraitVector(warmth=0.88, curiosity=0.88, playfulness=0.60, assertiveness=0.35, empathy=0.95),
        "INTJ": PersonalityTraitVector(warmth=0.45, curiosity=0.90, playfulness=0.25, assertiveness=0.90, empathy=0.55),
    }

    @classmethod
    def get_bias_vector(cls, mbti_type: str) -> PersonalityTraitVector:
        mbti_upper = mbti_type.upper().strip()
        return cls._MBTI_BIAS_REGISTRY.get(mbti_upper, PersonalityTraitVector(
            warmth=0.80, curiosity=0.80, playfulness=0.60, assertiveness=0.60, empathy=0.80
        ))
