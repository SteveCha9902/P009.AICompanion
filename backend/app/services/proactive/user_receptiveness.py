from typing import Optional
from app.domain.awareness.awareness_context import AwarenessContext, FacialEmotionType

class UserReceptivenessEngine:
    """
    Evaluates whether the user is in an open, receptive state for proactive conversation.
    Low receptiveness triggers when:
    - User gives very short terse answers (e.g. "ㅇㅇ", "응", "몰라")
    - User appears FATIGUED or deeply FOCUSED
    - User is occupied with complex tasks
    """

    MIN_RECEPTIVE_THRESHOLD = 0.60

    @classmethod
    def evaluate_receptiveness(
        cls,
        last_user_message: str = "",
        awareness_context: Optional[AwarenessContext] = None,
        idle_seconds: float = 60.0
    ) -> float:
        score = 0.85 # Base high receptiveness

        # 1. Terse/Short response penalty
        msg_len = len(last_user_message.strip())
        if 0 < msg_len <= 3:
            score -= 0.35
        elif 3 < msg_len <= 6:
            score -= 0.20


        # 2. Facial Emotion / Fatigue analysis from Visual Awareness
        if awareness_context and awareness_context.is_fresh:
            emotion = awareness_context.user_state.facial_emotion
            if emotion == FacialEmotionType.FATIGUED:
                score -= 0.35 # Fatigued users prefer silence
            elif emotion == FacialEmotionType.FOCUSED:
                score -= 0.25 # Focused users shouldn't be interrupted
            elif emotion in (FacialEmotionType.SMILING, FacialEmotionType.NEUTRAL):
                score += 0.10

        # 3. Idle timing (Very short idle < 30s is abrupt; 60s ~ 180s is optimal)
        if idle_seconds < 30:
            score -= 0.20
        elif 60 <= idle_seconds <= 180:
            score += 0.05

        return round(max(0.0, min(1.0, score)), 2)

    @classmethod
    def is_user_receptive(cls, score: float) -> bool:
        return score >= cls.MIN_RECEPTIVE_THRESHOLD
