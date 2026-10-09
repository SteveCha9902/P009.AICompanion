import math
from typing import Optional, Tuple
from app.services.character.relationship.domain import RelationshipVector, RelationshipDelta, RelationshipMilestone

class RelationshipEvolutionEngine:
    """
    Computes weighted bounded relationship deltas and detects shared milestones.
    """

    MAX_CLAMP = 0.03

    @classmethod
    def calculate_delta(
        cls,
        user_input: str,
        significance: float = 0.5,
        current_vector: Optional[RelationshipVector] = None
    ) -> RelationshipDelta:
        v = current_vector or RelationshipVector()
        input_lower = user_input.lower().strip()

        # 1. Maturity Decay Factor (Relationship Depth ↑ -> Delta Sensitivity ↓)
        # As shared history deepens, relationships become more resilient and change more smoothly.
        maturity_factor = max(0.4, 1.0 - (v.shared_history_depth * 0.5))

        # 2. Raw Delta Formulation
        raw_trust = 0.005
        raw_closeness = 0.005
        raw_comfort = 0.005
        raw_playfulness = 0.0
        raw_safety = 0.005
        reason = "routine_conversation"

        # Detect high-impact emotional/relational moments
        if any(kw in input_lower for kw in ["비밀", "상담", "고민", "사실 나", "confession", "secret"]):
            raw_trust = 0.025
            raw_closeness = 0.020
            raw_safety = 0.030
            reason = "user_shared_vulnerability"

        elif any(kw in input_lower for kw in ["힘들어", "지쳤어", "죽겠어", "우울해", "crying", "struggling"]):
            raw_comfort = 0.025
            raw_trust = 0.020
            raw_safety = 0.025
            reason = "user_in_crisis_or_distress"

        elif any(kw in input_lower for kw in ["ㅋㅋ", "ㅎㅎ", "장난", "lol", "joke", "haha"]):
            raw_playfulness = 0.020
            raw_closeness = 0.010
            reason = "shared_playful_moment"

        elif any(kw in input_lower for kw in ["고마워", "네 덕분에", "큰 도움", "thank you", "grateful"]):
            raw_trust = 0.020
            raw_comfort = 0.020
            reason = "user_expressed_gratitude"

        # 3. Apply Significance & Maturity Multiplier + Clamp (-0.03 to +0.03)
        def _apply_bounded(raw_val: float) -> float:
            scaled = raw_val * significance * maturity_factor
            clamped = max(-cls.MAX_CLAMP, min(cls.MAX_CLAMP, scaled))
            return round(clamped, 4)

        return RelationshipDelta(
            trust_delta=_apply_bounded(raw_trust),
            closeness_delta=_apply_bounded(raw_closeness),
            comfort_delta=_apply_bounded(raw_comfort),
            attachment_delta=_apply_bounded(raw_closeness * 0.5),
            playfulness_delta=_apply_bounded(raw_playfulness),
            respect_delta=_apply_bounded(raw_trust * 0.5),
            emotional_safety_delta=_apply_bounded(raw_safety),
            history_depth_delta=round(0.005 * maturity_factor, 4),
            significance_weight=significance,
            maturity_factor=round(maturity_factor, 2),
            reason=reason
        )

    @staticmethod
    def detect_milestone(
        user_id: str,
        companion_id: str,
        user_input: str,
        delta: RelationshipDelta
    ) -> Optional[RelationshipMilestone]:
        input_lower = user_input.lower().strip()

        if delta.reason == "user_shared_vulnerability":
            return RelationshipMilestone(
                user_id=user_id,
                companion_id=companion_id,
                milestone_type="USER_SHARED_SECRET",
                significance=0.88,
                summary="사용자가 처음으로 깊은 고민이나 비밀을 털어놓으며 깊은 신뢰를 보임."
            )
        elif delta.reason == "user_in_crisis_or_distress":
            return RelationshipMilestone(
                user_id=user_id,
                companion_id=companion_id,
                milestone_type="USER_CRISIS_SUPPORT",
                significance=0.92,
                summary="사용자가 힘든 위기 순간에 캐릭터와 대화하며 정서적 지지를 받음."
            )
        elif any(kw in input_lower for kw in ["성공", "합격", "해냈어", "won", "passed"]):
            return RelationshipMilestone(
                user_id=user_id,
                companion_id=companion_id,
                milestone_type="SHARED_ACHIEVEMENT",
                significance=0.85,
                summary="사용자의 중요한 성공과 마일스톤을 함께 축하함."
            )

        return None
