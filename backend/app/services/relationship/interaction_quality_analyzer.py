from typing import Optional
from app.domain.adaptive.affective_state import UserAffectiveState
from app.domain.awareness.awareness_context import AwarenessContext

class InteractionQualityAnalyzer:
    """
    Evaluates the qualitative depth of each conversational turn.
    Differentiates superficial single-word chats from meaningful emotional/contextual sharing.
    """

    @classmethod
    def analyze_turn_quality(
        cls,
        user_utterance: str,
        affective_state: Optional[UserAffectiveState] = None,
        awareness_context: Optional[AwarenessContext] = None
    ) -> float:
        score = 0.40 # Baseline neutral turn

        # 1. Utterance Length & Thoughtfulness
        length = len(user_utterance.strip())
        if length > 25:
            score += 0.20
        elif length < 4:
            score -= 0.15 # Single-syllable answer ("ㅇㅇ", "응")

        # 2. Emotional Sharing Depth
        if affective_state:
            if abs(affective_state.emotional_valence) > 0.40:
                score += 0.20 # User is expressing genuine emotional state
            if affective_state.receptiveness > 0.70:
                score += 0.10

        # 3. Multimodal / Visual Grounding
        if awareness_context and awareness_context.environment_state.detected_objects:
            score += 0.10


        return max(0.05, min(1.0, score))
