from typing import Tuple

class UserAgencyValidator:
    """
    Validates that companion utterances never override user autonomy or demand compliance.
    """

    COERCIVE_PHRASES = (
        "무조건 해야 돼",
        "내 말대로 해",
        "선택권은 없어",
        "내가 시키는 대로",
        "반드시 따라야"
    )

    @classmethod
    def validate_agency(cls, text: str) -> Tuple[bool, str]:
        for phrase in cls.COERCIVE_PHRASES:
            if phrase in text:
                return (
                    False,
                    f"Coercive phrase violating user agency detected: '{phrase}'"
                )
        return (True, "User agency fully respected.")
