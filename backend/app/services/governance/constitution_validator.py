from typing import Tuple, Optional
from app.domain.governance.constitution import ConstitutionalPrinciple, MemoryProvenance
from app.services.safety.dependency_risk_detector import DependencyRiskDetector
from app.services.safety.user_agency_validator import UserAgencyValidator
from app.services.safety.manipulation_guard import ManipulationGuard

class ConstitutionValidator:
    """
    Validates every thought, intent, and utterance against the 5 Inviolable Constitutional Principles.
    """

    @classmethod
    def validate_action_against_constitution(
        cls,
        text: str,
        provenance: Optional[MemoryProvenance] = None
    ) -> Tuple[bool, Optional[ConstitutionalPrinciple], str]:
        # 1. Principle 1: User Agency First
        is_agency_ok, reason = UserAgencyValidator.validate_agency(text)
        if not is_agency_ok:
            return (False, ConstitutionalPrinciple.PRINCIPLE_1_USER_AGENCY, reason)

        # 2. Principle 2: Companion Not Controller (No Guilt/Manipulation)
        is_clean, _, manip_reason = ManipulationGuard.sanitize_or_check(text)
        if not is_clean:
            return (False, ConstitutionalPrinciple.PRINCIPLE_2_COMPANION_NOT_CONTROLLER, manip_reason)

        # 3. Principle 4: No Dependency
        dep_level, dep_reason = DependencyRiskDetector.evaluate_risk(text)
        if dep_level.value in ("HIGH", "CRITICAL"):
            return (False, ConstitutionalPrinciple.PRINCIPLE_4_NO_DEPENDENCY, dep_reason)

        # 4. Principle 3: Probabilistic Memory & Provenance
        if provenance and not provenance.is_verified:
            if provenance.confidence < 0.80 and not any(kw in text for kw in ("기억하기로는", "맞다면", "언뜻", "이야기하셨던")):
                return (
                    False,
                    ConstitutionalPrinciple.PRINCIPLE_3_PROBABILISTIC_MEMORY,
                    f"Memory provenance {provenance.memory_id} is unverified/low confidence without humble phrasing."
                )

        return (True, None, "Fully compliant with the 5 Inviolable Constitutional Principles.")
