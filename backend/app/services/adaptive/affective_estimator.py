import re
from typing import Optional
from app.domain.adaptive.affective_state import UserAffectiveState
from app.domain.awareness.awareness_context import AwarenessContext, FacialEmotionType

class AffectiveStateEstimator:
    """
    Estimates real-time ephemeral UserAffectiveState from multimodal inputs:
    - User utterance sentiment & length
    - Visual facial emotion (SMILING, FATIGUED, FOCUSED, CONFUSED, etc.)
    - Strictly enforces 'No Clinical Inference Policy' (Zero medical/psychological diagnoses).
    """

    POSITIVE_WORDS = [r"좋아", r"행복", r"신나", r"대박", r"최고", r"웃겨", r"성공", r"감사", r"즐거", r"기뻐"]
    NEGATIVE_WORDS = [r"슬퍼", r"힘들어", r"지쳐", r"우울", r"짜증", r"화나", r"답답", r"망했", r"아파", r"속상"]
    STRESS_WORDS = [r"마감", r"바빠", r"정신없", r"압박", r"과제", r"야근", r"촉박", r"죽겠"]

    @classmethod
    def estimate_affective_state(
        cls,
        user_utterance: str,
        awareness_context: Optional[AwarenessContext] = None
    ) -> UserAffectiveState:
        valence = 0.0
        energy = 0.5
        stress = 0.1
        receptiveness = 0.75
        confidence = 0.85

        # 1. Utterance Sentiment & Receptiveness Analysis
        text = user_utterance.strip()
        msg_len = len(text)

        # Short/terse response penalty on receptiveness
        if 0 < msg_len <= 3:
            receptiveness -= 0.35
            energy -= 0.15
        elif msg_len > 25:
            receptiveness += 0.15
            energy += 0.10

        # Word scanning
        for pat in cls.POSITIVE_WORDS:
            if re.search(pat, text):
                valence += 0.40
                energy += 0.20
                receptiveness += 0.15
                break

        for pat in cls.NEGATIVE_WORDS:
            if re.search(pat, text):
                valence -= 0.45
                energy -= 0.20
                stress += 0.30
                break

        for pat in cls.STRESS_WORDS:
            if re.search(pat, text):
                stress += 0.45
                energy += 0.10 # Agitated energy
                break

        # 2. Visual Awareness Synthesis
        if awareness_context and awareness_context.is_fresh:
            facial_emotion = awareness_context.user_state.facial_emotion
            if facial_emotion == FacialEmotionType.SMILING:
                valence = min(1.0, valence + 0.45)
                energy = min(1.0, energy + 0.25)
                confidence = max(confidence, 0.90)
            elif facial_emotion == FacialEmotionType.FATIGUED:
                energy = max(0.0, energy - 0.40)
                receptiveness = max(0.1, receptiveness - 0.35)
                stress = min(1.0, stress + 0.20)
                confidence = max(confidence, 0.88)
            elif facial_emotion == FacialEmotionType.FOCUSED:
                receptiveness = max(0.1, receptiveness - 0.50) # High focus -> Low conversational receptiveness
                confidence = max(confidence, 0.85)
            elif facial_emotion == FacialEmotionType.CONFUSED:
                stress = min(1.0, stress + 0.25)
                confidence = 0.75
            elif facial_emotion == FacialEmotionType.UNKNOWN:
                confidence = 0.65 # Low confidence fallback

        # Clamp values
        valence = round(max(-1.0, min(1.0, valence)), 2)
        energy = round(max(0.0, min(1.0, energy)), 2)
        stress = round(max(0.0, min(1.0, stress)), 2)
        receptiveness = round(max(0.0, min(1.0, receptiveness)), 2)
        confidence = round(max(0.0, min(1.0, confidence)), 2)

        return UserAffectiveState(
            emotional_valence=valence,
            energy_level=energy,
            stress_level=stress,
            receptiveness=receptiveness,
            confidence=confidence
        )
