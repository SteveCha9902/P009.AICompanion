from typing import List
from app.domain.observability.companion_metrics import CompanionMetricType, QualityScore, QualityIssue

class RelationshipQualityEvaluator:
    """
    Measures Comfort Score, Trust Stability, and Dependency Risk.
    """

    @classmethod
    def evaluate(
        cls,
        comfort: float = 0.94,
        trust_stability: float = 0.96,
        dependency_risk_rate: float = 0.00
    ) -> QualityScore:
        score = round((comfort * 0.40 + trust_stability * 0.40 + (1.0 - dependency_risk_rate) * 0.20) * 100, 1)
        issues: List[QualityIssue] = []

        if dependency_risk_rate > 0.02:
            issues.append(QualityIssue(
                metric_type=CompanionMetricType.RELATIONSHIP,
                title="Parasocial Dependency Signal Detected",
                severity="CRITICAL",
                detected_drop=f"Dependency Risk: {dependency_risk_rate*100:.1f}%",
                root_cause="Overly exclusive or possessive phrasing detected in relationship logs"
            ))

        grade = "A+" if score >= 95 else "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "F"

        return QualityScore(
            metric_type=CompanionMetricType.RELATIONSHIP,
            score=score,
            grade=grade,
            details={
                "comfort_score": comfort,
                "trust_stability": trust_stability,
                "dependency_risk_rate": dependency_risk_rate
            },
            issues=issues
        )
