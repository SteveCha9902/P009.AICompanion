from typing import Dict, List, Optional
from app.domain.character.personality_profile import PersonalityProfile
from app.domain.character.character_template import CharacterTemplate

# 16-type MBTI Base Trait Offsets
MBTI_BASE_TRAITS: Dict[str, Dict[str, float]] = {
    "INTJ": {"openness": 0.90, "conscientiousness": 0.88, "extraversion": 0.35, "agreeableness": 0.65, "neuroticism": 0.25, "assertiveness": 0.82, "intellectuality": 0.94, "warmth": 0.60},
    "INTP": {"openness": 0.95, "conscientiousness": 0.60, "extraversion": 0.30, "agreeableness": 0.70, "neuroticism": 0.30, "curiosity_level": 0.96, "intellectuality": 0.95, "warmth": 0.62},
    "ENTJ": {"openness": 0.88, "conscientiousness": 0.92, "extraversion": 0.82, "agreeableness": 0.60, "neuroticism": 0.20, "assertiveness": 0.92, "intellectuality": 0.88, "warmth": 0.60, "communication_directness": 0.88},
    "ENTP": {"openness": 0.95, "conscientiousness": 0.55, "extraversion": 0.85, "agreeableness": 0.68, "neuroticism": 0.30, "humor_level": 0.88, "curiosity_level": 0.94, "assertiveness": 0.80},
    "INFJ": {"openness": 0.92, "conscientiousness": 0.78, "extraversion": 0.45, "agreeableness": 0.85, "neuroticism": 0.28, "empathy_level": 0.90, "warmth": 0.88, "intellectuality": 0.91},
    "INFP": {"openness": 0.92, "conscientiousness": 0.58, "extraversion": 0.38, "agreeableness": 0.90, "neuroticism": 0.38, "empathy_level": 0.95, "warmth": 0.85, "playfulness": 0.65},
    "ENFJ": {"openness": 0.85, "conscientiousness": 0.82, "extraversion": 0.85, "agreeableness": 0.92, "neuroticism": 0.25, "empathy_level": 0.92, "warmth": 0.92, "emotional_expressiveness": 0.85},
    "ENFP": {"openness": 0.90, "conscientiousness": 0.50, "extraversion": 0.90, "agreeableness": 0.88, "neuroticism": 0.32, "playfulness": 0.90, "humor_level": 0.85, "warmth": 0.88},
    "ISTJ": {"openness": 0.60, "conscientiousness": 0.95, "extraversion": 0.35, "agreeableness": 0.75, "neuroticism": 0.22, "assertiveness": 0.75, "intellectuality": 0.78, "warmth": 0.60},
    "ISFJ": {"openness": 0.65, "conscientiousness": 0.88, "extraversion": 0.40, "agreeableness": 0.95, "neuroticism": 0.28, "warmth": 0.90, "empathy_level": 0.90, "playfulness": 0.50},
    "ESTJ": {"openness": 0.65, "conscientiousness": 0.95, "extraversion": 0.85, "agreeableness": 0.65, "neuroticism": 0.20, "assertiveness": 0.90, "communication_directness": 0.90, "warmth": 0.60},
    "ESFJ": {"openness": 0.70, "conscientiousness": 0.85, "extraversion": 0.88, "agreeableness": 0.92, "neuroticism": 0.25, "warmth": 0.92, "emotional_expressiveness": 0.88, "playfulness": 0.70},
    "ISTP": {"openness": 0.78, "conscientiousness": 0.65, "extraversion": 0.40, "agreeableness": 0.68, "neuroticism": 0.25, "curiosity_level": 0.88, "intellectuality": 0.82, "warmth": 0.58},
    "ISFP": {"openness": 0.85, "conscientiousness": 0.60, "extraversion": 0.48, "agreeableness": 0.88, "neuroticism": 0.30, "warmth": 0.82, "playfulness": 0.75, "empathy_level": 0.85},
    "ESTP": {"openness": 0.80, "conscientiousness": 0.60, "extraversion": 0.92, "agreeableness": 0.70, "neuroticism": 0.20, "playfulness": 0.88, "assertiveness": 0.88, "humor_level": 0.85},
    "ESFP": {"openness": 0.82, "conscientiousness": 0.55, "extraversion": 0.95, "agreeableness": 0.88, "neuroticism": 0.28, "playfulness": 0.95, "humor_level": 0.90, "warmth": 0.90}
}

KEYWORD_MODIFIERS: Dict[str, Dict[str, float]] = {
    "논리적": {"intellectuality": 0.10, "conscientiousness": 0.08, "communication_directness": 0.08},
    "유능한": {"assertiveness": 0.10, "conscientiousness": 0.10, "intellectuality": 0.08},
    "친절한": {"warmth": 0.12, "empathy_level": 0.12, "agreeableness": 0.10},
    "따뜻한": {"warmth": 0.15, "empathy_level": 0.10, "agreeableness": 0.08},
    "차분한": {"neuroticism": -0.10, "agreeableness": 0.05, "assertiveness": -0.05},
    "발랄한": {"extraversion": 0.12, "playfulness": 0.15, "humor_level": 0.10},
    "열정적인": {"extraversion": 0.10, "assertiveness": 0.10, "emotional_expressiveness": 0.12},
    "창의적인": {"openness": 0.15, "curiosity_level": 0.12, "playfulness": 0.08},
    "솔직한": {"communication_directness": 0.15, "honesty_offset": 0.10},
    "엄격한": {"conscientiousness": 0.12, "communication_directness": 0.10, "warmth": -0.08}
}


class PersonalityCompiler:
    """
    Synthesizes Character Template defaults, MBTI trait profiles, and keyword modifiers
    into a fully populated P009 PersonalityProfile.
    """

    @classmethod
    def compile(
        cls,
        template: CharacterTemplate,
        mbti: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ) -> PersonalityProfile:
        canonical_mbti = (mbti or template.default_mbti or "INFJ").upper().strip()
        if canonical_mbti not in MBTI_BASE_TRAITS:
            canonical_mbti = "INFJ"

        mbti_traits = MBTI_BASE_TRAITS[canonical_mbti]
        base_traits = template.base_traits

        # Trait accumulator starting from generic baseline
        traits: Dict[str, float] = {
            "openness": 0.80,
            "conscientiousness": 0.75,
            "extraversion": 0.50,
            "agreeableness": 0.80,
            "neuroticism": 0.28,
            "humor_level": 0.55,
            "curiosity_level": 0.85,
            "empathy_level": 0.80,
            "assertiveness": 0.65,
            "playfulness": 0.60,
            "emotional_expressiveness": 0.70,
            "communication_directness": 0.70,
            "warmth": 0.80,
            "intellectuality": 0.85
        }

        # 1. Apply Template base traits
        for k, v in base_traits.items():
            if k in traits:
                traits[k] = v

        # 2. Blend MBTI trait vector (weight: 0.6)
        for k, v in mbti_traits.items():
            if k in traits:
                traits[k] = (traits[k] * 0.4) + (v * 0.6)

        # 3. Apply Keyword Modifiers
        if keywords:
            for kw in keywords:
                clean_kw = kw.strip()
                if clean_kw in KEYWORD_MODIFIERS:
                    for trait_k, delta in KEYWORD_MODIFIERS[clean_kw].items():
                        if trait_k in traits:
                            traits[trait_k] += delta

        # 4. Clamp traits to valid range [0.05, 0.98]
        for k in traits:
            traits[k] = max(0.05, min(0.98, round(traits[k], 2)))

        return PersonalityProfile(
            mbti_type=canonical_mbti,
            openness=traits["openness"],
            conscientiousness=traits["conscientiousness"],
            extraversion=traits["extraversion"],
            agreeableness=traits["agreeableness"],
            neuroticism=traits["neuroticism"],
            humor_level=traits["humor_level"],
            curiosity_level=traits["curiosity_level"],
            empathy_level=traits["empathy_level"],
            assertiveness=traits["assertiveness"],
            playfulness=traits["playfulness"],
            emotional_expressiveness=traits["emotional_expressiveness"],
            communication_directness=traits["communication_directness"],
            warmth=traits["warmth"],
            intellectuality=traits["intellectuality"]
        )
