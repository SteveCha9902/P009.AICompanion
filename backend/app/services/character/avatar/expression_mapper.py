from typing import Optional, List, Tuple
from app.services.character.avatar.domain import ContinuousEmotionVector, ExpressionParameters, RelationshipParameters, VisemeType

class EmotionToExpressionMapper:
    """
    Deterministically transforms ContinuousEmotionVector into renderer-agnostic ExpressionParameters.
    Supports Multi-Emotion Blending and Relationship Bias Modifiers (Sprint 44).
    """

    @staticmethod
    def map_emotion_to_expression(
        emotion: ContinuousEmotionVector,
        relationship: Optional[RelationshipParameters] = None
    ) -> ExpressionParameters:
        v = emotion.valence
        a = emotion.arousal
        w = emotion.warmth
        intensity = emotion.intensity

        # 1. Smile Strength
        if v > 0.0:
            raw_smile = min(1.0, max(0.0, (v * 0.7 + w * 0.3) * intensity))
        else:
            raw_smile = 0.0

        # Apply Relationship Bias if present
        if relationship:
            rel_factor = 0.7 + 0.3 * relationship.familiarity
            smile_strength = round(min(1.0, raw_smile * rel_factor + 0.15 * relationship.warmth), 3)
            warmth_alpha = round(min(1.0, max(0.0, (w * 0.6 + relationship.warmth * 0.4))), 2)
            eye_softness = round(min(1.0, max(0.0, (w * 0.5 + relationship.trust * 0.5))), 3)
        else:
            smile_strength = round(raw_smile, 3)
            warmth_alpha = round(min(1.0, max(0.0, w * 0.8 + 0.2)), 2)
            eye_softness = round(min(1.0, max(0.0, (w * 0.6 + max(0.0, v) * 0.4))), 3)

        # 2. Brow Raise / Furrow (-1.0 to +1.0)
        if v < -0.1:
            brow = round(max(-1.0, v * intensity), 3) # Furrowed
        elif a > 0.6:
            brow = round(min(1.0, (a - 0.5) * 2.0 * intensity), 3) # Raised / Attentive
        else:
            brow = 0.0

        # 3. Subtle Head Orientation (Degrees)
        head_pitch = round(-2.0 * v * intensity, 2)
        head_roll = round(3.0 * w * (1.0 if v >= 0 else -1.0), 2)
        head_yaw = 0.0
        eye_openness = 1.0 if a >= 0.4 else 0.85

        return ExpressionParameters(
            smile_strength=smile_strength,
            eye_softness=eye_softness,
            eye_openness=eye_openness,
            blink_value=0.0,
            brow_raise=brow,
            mouth_open=0.0,
            viseme=VisemeType.CLOSED,
            head_pitch=head_pitch,
            head_yaw=head_yaw,
            head_roll=head_roll,
            warmth_alpha=warmth_alpha
        )

    @classmethod
    def blend_emotions(cls, weighted_emotions: List[Tuple[ContinuousEmotionVector, float]]) -> ContinuousEmotionVector:
        """
        Synthesizes a blended ContinuousEmotionVector from a list of (emotion, weight) tuples.
        """
        total_weight = sum(w for _, w in weighted_emotions) or 1.0
        v = sum(emo.valence * (w / total_weight) for emo, w in weighted_emotions)
        a = sum(emo.arousal * (w / total_weight) for emo, w in weighted_emotions)
        w_val = sum(emo.warmth * (w / total_weight) for emo, w in weighted_emotions)
        c = sum(emo.confidence * (w / total_weight) for emo, w in weighted_emotions)
        i = sum(emo.intensity * (w / total_weight) for emo, w in weighted_emotions)

        return ContinuousEmotionVector(
            valence=round(v, 3),
            arousal=round(a, 3),
            warmth=round(w_val, 3),
            confidence=round(c, 3),
            intensity=round(i, 3)
        )
