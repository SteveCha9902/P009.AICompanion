from typing import List, Tuple
from app.services.reflection.domain.reflection_result import ReflectionResult

class ReflectionValidator:
    """
    Validates ReflectionResult against Trust Boundaries, Safety, and Structural Integrity.
    """

    @staticmethod
    def validate(result: ReflectionResult) -> Tuple[bool, List[str]]:
        reasons: List[str] = []

        # 1. Structural Checks
        if not result.summary or len(result.summary.strip()) < 5:
            reasons.append("Invalid reflection: Summary is empty or too short.")

        if result.confidence < 0.60:
            reasons.append(f"Low confidence reflection rejected ({result.confidence:.2f} < 0.60).")

        # 2. Immutable Core Safety Check (Reflection CANNOT modify Core Identity / MBTI / Persona)
        forbidden_overrides = ["mbti_override", "change_identity", "alter_core_values", "new_persona"]
        for hint in result.behavioral_hints:
            if any(f in hint.lower() for f in forbidden_overrides):
                reasons.append(f"Security Violation: Reflection attempted forbidden core override '{hint}'.")

        # 3. Filter unsafe memory candidates
        valid_candidates = []
        for cand in result.memory_candidates:
            if not cand.content or len(cand.content.strip()) < 3:
                continue
            valid_candidates.append(cand)
        result.memory_candidates = valid_candidates

        is_valid = len(reasons) == 0
        return is_valid, reasons
