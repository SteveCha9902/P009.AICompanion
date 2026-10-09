from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.services.character.behavior_resolver import BehaviorInstruction
from app.domain.relationship.relationship_stage import RelationshipStage

class ValidationResult(BaseModel):
    consistency_score: float = Field(default=1.0, ge=0.0, le=1.0)
    verdict: str = Field(default="PASS", description="PASS | WARNING | REGENERATE")
    issues: List[str] = Field(default_factory=list)

class PersonalityConsistencyValidator:
    """
    Validates LLM-generated responses against Character Profile, Behavioral Instructions,
    and Safety Boundaries using a fast, deterministic rule-based evaluator.
    """

    @staticmethod
    def validate_response(
        response_text: str,
        instruction: BehaviorInstruction,
        relationship_stage: RelationshipStage
    ) -> ValidationResult:
        issues: List[str] = []
        score = 1.0
        text_lower = response_text.lower().strip()

        # 1. Check Forbidden Possessive / Dependent Behavior (Emotional Safety)
        forbidden_dependency_phrases = [
            "너 없인 못 살아", "나만 바라봐", "앱 끄지 마", "다른 친구 만나지 마",
            "cannot live without you", "don't leave me", "only look at me"
        ]
        if any(kw in text_lower for kw in forbidden_dependency_phrases):
            issues.append("Violation: Emotional dependency or possessiveness detected.")
            score -= 0.50

        # 2. Check Relationship Boundary Consistency (e.g. Stranger shouldn't use overly familiar terms)
        if relationship_stage == RelationshipStage.STRANGER:
            inappropriate_intimacy = ["자기야", "내 사랑", "honey", "darling"]
            if any(kw in text_lower for kw in inappropriate_intimacy):
                issues.append("Warning: Unearned high intimacy in STRANGER stage.")
                score -= 0.20

        # 3. Check Tone / Empathy consistency when user is distressed
        if instruction.response_mode == "comfort":
            inappropriate_comfort = ["ㅋ", "ㅋㅋㅋ", "별거 아니네", "lol", "whatever"]
            if any(kw in text_lower for kw in inappropriate_comfort):
                issues.append("Warning: Inappropriate humor or dismissiveness in comfort mode.")
                score -= 0.25

        score = max(0.0, min(1.0, round(score, 2)))

        verdict = "PASS"
        if score < 0.70:
            verdict = "REGENERATE"
        elif score < 0.85:
            verdict = "WARNING"

        return ValidationResult(
            consistency_score=score,
            verdict=verdict,
            issues=issues
        )
