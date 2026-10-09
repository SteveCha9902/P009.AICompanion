import time
import logging
from typing import Dict, Any, List, Optional

from app.services.character.domain import (
    BehaviorIntent,
    ResponseStyleType,
    CharacterDecision
)
from app.services.character.traits import PersonalityTraitVector
from app.services.character.mbti_mapper import MBTIMapper
from app.domain.relationship.relationship_stage import RelationshipStage

logger = logging.getLogger(__name__)

class CharacterBehaviorEngine:
    """
    Core Behavioral Decision Engine executing Situation Analysis and Multi-Factor Trait Weighting (<10ms).
    """

    @classmethod
    def resolve_decision(
        cls,
        user_input: str,
        core_traits: Optional[PersonalityTraitVector] = None,
        mbti_type: str = "ENFP",
        emotion_state: Optional[Dict[str, Any]] = None,
        relationship_stage: RelationshipStage = RelationshipStage.FRIEND,
        relationship_closeness: float = 0.6,
        memory_context: Optional[List[str]] = None,
        recent_reflection_hints: Optional[List[str]] = None
    ) -> CharacterDecision:
        t0 = time.perf_counter()
        reasons: List[str] = []
        input_lower = user_input.lower().strip()

        # 1. Situation Analysis & Confidence
        is_stress = any(kw in input_lower for kw in ["힘들어", "지쳤어", "속상해", "우울", "피곤", "tired", "sad", "stressed", "exhausted"])
        is_celebrate = any(kw in input_lower for kw in ["성공", "해냈어", "합격", "완성", "won", "passed", "succeeded", "celebrate"])
        is_tease_opportunity = any(kw in input_lower for kw in ["ㅋㅋ", "ㅎㅎ", "장난", "lol", "joke", "haha"])
        is_serious = is_stress or any(kw in input_lower for kw in ["고민", "결정", "비밀", "상담", "advice", "serious"])

        # Determine Decision Confidence
        confidence = 0.90 if (is_stress or is_celebrate) else (0.75 if len(input_lower) > 8 else 0.55)

        # 2. Multi-factor Weighted Trait Resolution
        base_core = core_traits or PersonalityTraitVector()
        mbti_bias = MBTIMapper.get_bias_vector(mbti_type)

        emotion_intensity = 0.5
        if emotion_state and "valence" in emotion_state:
            emotion_intensity = max(0.2, min(1.0, abs(emotion_state["valence"]) + 0.3))

        weighted_traits = base_core.weighted(
            mbti_bias=mbti_bias,
            relationship_factor=relationship_closeness,
            emotion_factor=emotion_intensity
        )

        # 3. Formulate Behavior Intents & Response Style
        intents: List[BehaviorIntent] = []
        response_style = ResponseStyleType.WARM_SUPPORTIVE

        if is_stress:
            reasons.append("situation_user_distress_detected")
            intents.append(BehaviorIntent.COMFORT_USER)
            if weighted_traits.empathy >= 0.70:
                intents.append(BehaviorIntent.ASK_FOLLOWUP)
            if confidence > 0.80:
                response_style = ResponseStyleType.GENTLE_LISTENING
            else:
                response_style = ResponseStyleType.WARM_SUPPORTIVE

        elif is_celebrate:
            reasons.append("situation_user_celebration_detected")
            intents.append(BehaviorIntent.CELEBRATE_SUCCESS)
            if weighted_traits.playfulness >= 0.60:
                intents.append(BehaviorIntent.SHARE_PERSPECTIVE)
            response_style = ResponseStyleType.CHEERFUL_ENERGETIC

        elif is_tease_opportunity and relationship_stage in [RelationshipStage.FRIEND, RelationshipStage.CLOSE_FRIEND, RelationshipStage.TRUSTED_COMPANION] and weighted_traits.playfulness >= 0.60:
            reasons.append("situation_playful_context")
            intents.append(BehaviorIntent.TEASE_PLAYFULLY)
            response_style = ResponseStyleType.PLAYFUL_TEASING


        elif is_serious:
            reasons.append("situation_serious_inquiry")
            intents.extend([BehaviorIntent.COMFORT_USER, BehaviorIntent.SHARE_PERSPECTIVE])
            response_style = ResponseStyleType.CALM_REFLECTIVE

        else:
            reasons.append("situation_general_friendly_interaction")
            intents.append(BehaviorIntent.MAINTAIN_FRIENDLY_CHAT)
            if weighted_traits.curiosity >= 0.75:
                intents.append(BehaviorIntent.ASK_FOLLOWUP)
            if mbti_type.upper() == "ISTJ":
                response_style = ResponseStyleType.STRUCTURED_FACTUAL
            else:
                response_style = ResponseStyleType.WARM_SUPPORTIVE

        # Reflection Hints Integration
        if recent_reflection_hints:
            reasons.append(f"reflection_hints_{len(recent_reflection_hints)}")

        # 4. Formulate Prompt Directive
        intents_str = ", ".join([it.value for it in intents])
        prompt_directive = (
            f"[BEHAVIOR DECISION]\n"
            f"- Response Style: {response_style.value}\n"
            f"- Behavior Intents: {intents_str}\n"
            f"- Emotional Intensity: {emotion_intensity:.2f}\n"
            f"- Decision Confidence: {confidence:.2f}\n"
            f"INSTRUCTION: Act according to this decision naturally. Do not sound like a generic AI assistant."
        )

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        reasons.append(f"engine_latency_{elapsed_ms:.2f}ms")

        return CharacterDecision(
            response_style=response_style,
            behavior_intents=intents,
            emotional_intensity=round(emotion_intensity, 2),
            initiative_level=round(weighted_traits.curiosity * 0.8, 2),
            humor_probability=0.10 if is_stress else round(weighted_traits.playfulness * 0.5, 2),
            relationship_tone=relationship_stage.value,
            decision_confidence=round(confidence, 2),
            reasons=reasons,
            prompt_directive=prompt_directive
        )
