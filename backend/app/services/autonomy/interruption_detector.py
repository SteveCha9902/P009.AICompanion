from typing import Optional
from app.domain.awareness.awareness_context import AwarenessContext
from app.domain.adaptive.affective_state import UserAffectiveState

class InterruptionDetector:
    """
    Detects if the user is occupied, distracted, on a call, or looking away.
    Suppresses proactive autonomous speech when user focus should not be interrupted.
    """

    @classmethod
    def should_suppress_interruption(
        cls,
        user_utterance: str,
        awareness_context: Optional[AwarenessContext] = None,
        affective_state: Optional[UserAffectiveState] = None
    ) -> bool:
        # 1. Very short utterance / repetitive single words
        if len(user_utterance.strip()) <= 2 and user_utterance.strip() in ("ㅇ", "ㅇㅇ", "응", "음", "글쎄"):
            return True

        # 2. Low receptiveness or extreme focus/fatigue
        if affective_state:
            if affective_state.receptiveness < 0.35:
                return True

        # 3. Awareness indicators (e.g. user looking away from screen)
        if awareness_context and awareness_context.user_state:
            if awareness_context.user_state.gaze_direction in ("away", "looking_down"):
                if awareness_context.user_state.attention_level < 0.30:
                    return True

        return False
