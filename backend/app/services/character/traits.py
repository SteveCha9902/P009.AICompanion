from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class PersonalityTraitVector(BaseModel):
    """
    Big-5 aligned 5D Trait Vector representing stable disposition.
    """
    warmth: float = Field(default=0.85, ge=0.0, le=1.0)
    curiosity: float = Field(default=0.90, ge=0.0, le=1.0)
    playfulness: float = Field(default=0.70, ge=0.0, le=1.0)
    assertiveness: float = Field(default=0.60, ge=0.0, le=1.0)
    empathy: float = Field(default=0.90, ge=0.0, le=1.0)

    def weighted(
        self,
        mbti_bias: Optional["PersonalityTraitVector"] = None,
        relationship_factor: float = 0.5,
        emotion_factor: float = 0.5,
        situation_weights: Optional[Dict[str, float]] = None
    ) -> "PersonalityTraitVector":
        """
        Combines Core disposition (0.45), MBTI bias (0.25), Relationship (0.15), Emotion (0.10), and Situation (0.05).
        """
        w_core = 0.45
        w_mbti = 0.25
        w_rel = 0.15
        w_emo = 0.10
        w_sit = 0.05

        mb = mbti_bias or self

        calc_warmth = (self.warmth * w_core) + (mb.warmth * w_mbti) + (relationship_factor * w_rel) + (emotion_factor * w_emo) + 0.02
        calc_curiosity = (self.curiosity * w_core) + (mb.curiosity * w_mbti) + 0.10
        calc_playfulness = (self.playfulness * w_core) + (mb.playfulness * w_mbti) + (relationship_factor * 0.10)
        calc_assertiveness = (self.assertiveness * w_core) + (mb.assertiveness * w_mbti)
        calc_empathy = (self.empathy * w_core) + (mb.empathy * w_mbti) + (relationship_factor * w_rel) + (emotion_factor * w_emo)

        return PersonalityTraitVector(
            warmth=round(max(0.0, min(1.0, calc_warmth)), 2),
            curiosity=round(max(0.0, min(1.0, calc_curiosity)), 2),
            playfulness=round(max(0.0, min(1.0, calc_playfulness)), 2),
            assertiveness=round(max(0.0, min(1.0, calc_assertiveness)), 2),
            empathy=round(max(0.0, min(1.0, calc_empathy)), 2)
        )
