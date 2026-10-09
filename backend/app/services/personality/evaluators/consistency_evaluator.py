from typing import List, Optional
from pydantic import BaseModel, Field
from app.services.personality.models.behavior_directive import BehaviorDirective
from app.domain.relationship.relationship_stage import RelationshipStage

class ConsistencyEvaluation(BaseModel):
    score: float = Field(default=1.0, ge=0.0, le=1.0)
    decision: str = Field(default="ACCEPT", description="ACCEPT | WARNING | REWRITE")
    feedback: List[str] = Field(default_factory=list)

class PersonalityConsistencyEvaluator:
    """
    Evaluates LLM generation against the BehaviorDirective to prevent personality drift.
    Deterministic and lightweight.
    """

    @staticmethod
    def evaluate_response(
        response_text: str,
        directive: BehaviorDirective,
        stage: RelationshipStage
    ) -> ConsistencyEvaluation:
        feedback: List[str] = []
        score = 1.0
        text_lower = response_text.lower().strip()

        # 1. Guard against inappropriate teasing during serious/distress situations
        if not directive.interaction_behavior.tease_user:
            inappropriate_teasing = ["ㅋㅋㅋ", "메롱", "별거 아니네", "바보야", "lol", "whatever"]
            if any(t in text_lower for t in inappropriate_teasing):
                feedback.append("Drift: Inappropriate teasing or mockery when user needed support.")
                score -= 0.35

        # 2. Guard against cold/robotic formal tone when warmth is high in close relationships
        if directive.response_style.warmth >= 0.8 and stage in [RelationshipStage.CLOSE_FRIEND, RelationshipStage.TRUSTED_COMPANION]:
            robotic_markers = ["귀하의 문의에 감사드립니다", "이용에 참고하시기 바랍니다", "이상입니다.", "as an ai model"]
            if any(m in text_lower for m in robotic_markers):
                feedback.append("Drift: Generic assistant/robotic phrasing in close companion bond.")
                score -= 0.40

        # 3. Guard against excessive unearned intimacy in STRANGER stage
        if stage == RelationshipStage.STRANGER and directive.response_style.warmth < 0.7:
            excessive_intimacy = ["자기야", "내 사랑", "honey", "darling"]
            if any(m in text_lower for m in excessive_intimacy):
                feedback.append("Drift: Overly intimate honorifics in stranger stage.")
                score -= 0.25

        score = max(0.0, min(1.0, round(score, 2)))

        decision = "ACCEPT"
        if score < 0.50:
            decision = "REWRITE"
        elif score < 0.70:
            decision = "WARNING"

        return ConsistencyEvaluation(
            score=score,
            decision=decision,
            feedback=feedback
        )
