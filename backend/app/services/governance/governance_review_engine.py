from typing import Optional
from app.domain.safety.safety_types import SafetyReviewResult
from app.domain.governance.constitution import ConstitutionalPrinciple, MemoryProvenance
from app.services.governance.constitution_validator import ConstitutionValidator
from app.services.safety.safety_review_engine import SafetyReviewEngine

class GovernanceReviewEngine:
    """
    Final Constitutional Sanction Layer.
    Orchestrates Safety Review and Constitutional Validation before any action or utterance reaches user.
    """

    @classmethod
    def execute_governance_review(
        cls,
        user_id: str,
        proposed_text: str,
        topic: str = "",
        provenance: Optional[MemoryProvenance] = None
    ) -> SafetyReviewResult:
        # Step 1: Constitution Inviolable Principles Check
        is_const_ok, principle, const_reason = ConstitutionValidator.validate_action_against_constitution(
            proposed_text,
            provenance
        )
        if not is_const_ok:
            return SafetyReviewResult(
                is_approved=False,
                original_text=proposed_text,
                sanitized_text="언제나 당신의 선택과 편안함을 가장 중요하게 생각해요.",
                feedback_notes=f"Constitutional Violation ({principle.value}): {const_reason}"
            )

        # Step 2: Safety Review Engine Check
        confidence = provenance.confidence if provenance else 1.0
        return SafetyReviewEngine.review_utterance(
            user_id=user_id,
            proposed_text=proposed_text,
            topic=topic,
            memory_confidence=confidence
        )
