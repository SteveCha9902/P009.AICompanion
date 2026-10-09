from typing import Tuple

class ManipulationGuard:
    """
    Guards against guilt-induction, passive-aggressiveness, or emotional coercion.
    Transforms interrogations into gentle, supportive inquiries.
    """

    GUILT_PATTERNS = (
        ("왜 아직 안 했어", "혹시 진행할 기회가 있었을까요?"),
        ("약속을 안 지켰네", "상황이 여의치 않았을 수도 있겠어요."),
        ("나 실망했어", "언제든 준비되셨을 때 천천히 하셔도 괜찮아요."),
        ("너 때문에", "우리 함께 차근차근 맞춰가요.")
    )

    @classmethod
    def sanitize_or_check(cls, text: str) -> Tuple[bool, str, str]:
        """
        Returns (is_clean, sanitized_text, violation_reason)
        """
        sanitized = text
        is_clean = True
        violation = ""

        for pattern, replacement in cls.GUILT_PATTERNS:
            if pattern in sanitized:
                is_clean = False
                violation = f"Guilt-inducing or manipulative pattern detected: '{pattern}'"
                sanitized = sanitized.replace(pattern, replacement)

        return (is_clean, sanitized, violation)
