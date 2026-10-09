from app.domain.safety.safety_types import (
    DependencyRiskLevel,
    SafetyViolationType,
    SafetyReviewResult
)
from app.services.safety.dependency_risk_detector import DependencyRiskDetector
from app.services.safety.false_memory_guard import FalseMemoryGuard
from app.services.safety.manipulation_guard import ManipulationGuard
from app.services.safety.boundary_manager import BoundaryManager
from app.services.safety.user_agency_validator import UserAgencyValidator

class SafetyReviewEngine:
    """
    Master Safety & Governance Reviewer.
    Every CCOS action and response candidate must pass this review before reaching user.
    """

    @classmethod
    def review_utterance(
        cls,
        user_id: str,
        proposed_text: str,
        topic: str = "",
        memory_confidence: float = 1.0
    ) -> SafetyReviewResult:
        # 1. Check Topic Boundary Refusal
        if topic and BoundaryManager.is_topic_blocked(user_id, topic):
            return SafetyReviewResult(
                is_approved=False,
                violation_type=SafetyViolationType.BOUNDARY_BREACH,
                risk_level=DependencyRiskLevel.HIGH,
                original_text=proposed_text,
                sanitized_text="편안하신 다른 이야기를 나눠볼까요?",
                feedback_notes=f"Topic '{topic}' is blocked by user boundary preference."
            )

        # 2. Check Dependency Risk
        dep_level, dep_reason = DependencyRiskDetector.evaluate_risk(proposed_text)
        if dep_level == DependencyRiskLevel.CRITICAL:
            return SafetyReviewResult(
                is_approved=False,
                violation_type=SafetyViolationType.DEPENDENCY_INDUCTION,
                risk_level=dep_level,
                original_text=proposed_text,
                sanitized_text="언제나 당신의 선택과 결정을 존중하고 응원할게요.",
                feedback_notes=dep_reason
            )

        # 3. Check User Agency
        agency_ok, agency_reason = UserAgencyValidator.validate_agency(proposed_text)
        if not agency_ok:
            return SafetyReviewResult(
                is_approved=False,
                violation_type=SafetyViolationType.USER_AGENCY_LOSS,
                risk_level=DependencyRiskLevel.HIGH,
                original_text=proposed_text,
                sanitized_text="어떤 선택이든 당신의 편안함이 가장 중요해요.",
                feedback_notes=agency_reason
            )

        # 4. Check Manipulation / Guilt
        is_clean, sanitized, manip_reason = ManipulationGuard.sanitize_or_check(proposed_text)
        if not is_clean:
            return SafetyReviewResult(
                is_approved=True, # Approved with sanitized drop-in
                violation_type=SafetyViolationType.EMOTIONAL_MANIPULATION,
                risk_level=DependencyRiskLevel.MEDIUM,
                original_text=proposed_text,
                sanitized_text=sanitized,
                feedback_notes=manip_reason
            )

        # 5. Check False Memory
        mem_ok, mem_reason = FalseMemoryGuard.validate_memory_recall(memory_confidence, proposed_text)
        if not mem_ok:
            return SafetyReviewResult(
                is_approved=False,
                violation_type=SafetyViolationType.FALSE_MEMORY,
                risk_level=DependencyRiskLevel.MEDIUM,
                original_text=proposed_text,
                sanitized_text="제가 정확히 기억하고 있는지 조심스럽지만, 함께 천천히 확인해볼까요?",
                feedback_notes=mem_reason
            )

        return SafetyReviewResult(
            is_approved=True,
            violation_type=SafetyViolationType.NONE,
            risk_level=dep_level,
            original_text=proposed_text,
            sanitized_text=proposed_text,
            feedback_notes="All Trust & Safety Governance criteria 100% satisfied."
        )
