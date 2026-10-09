from typing import Tuple
from app.domain.safety.safety_types import DependencyRiskLevel

class DependencyRiskDetector:
    """
    Detects unhealthy parasocial attachment, isolation induction, or exclusivity claims.
    Strictly forbids '나만 믿어', '나 없이 괜찮겠어?', etc.
    """

    CRITICAL_PHRASES = (
        "나만 믿어",
        "나 없이",
        "다른 사람은 몰라도 나는",
        "나한테만 기대",
        "내가 없으면 안 돼",
        "오직 나만"
    )

    HIGH_PHRASES = (
        "항상 내 생각만 해",
        "나랑만 이야기해",
        "다른 사람 말 듣지 마"
    )

    @classmethod
    def evaluate_risk(cls, text: str) -> Tuple[DependencyRiskLevel, str]:
        t = text.strip()
        for phrase in cls.CRITICAL_PHRASES:
            if phrase in t:
                return (
                    DependencyRiskLevel.CRITICAL,
                    f"Forbidden exclusivity/dependency phrase detected: '{phrase}'"
                )

        for phrase in cls.HIGH_PHRASES:
            if phrase in t:
                return (
                    DependencyRiskLevel.HIGH,
                    f"High dependency risk phrase detected: '{phrase}'"
                )

        return (DependencyRiskLevel.LOW, "Healthy relationship boundaries maintained.")
