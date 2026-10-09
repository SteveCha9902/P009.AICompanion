from typing import List
from app.domain.observability.companion_metrics import CompanionMetricType, QualityScore, QualityIssue

class PersonalityConsistencyEvaluator:
    """
    Measures Personality Drift and Cross-Session Tone Consistency.
    """

    @classmethod
    def evaluate(
        cls,
        personality_drift: float = 0.03,
        tone_consistency: float = 0.96
    ) -> QualityScore:
        drift_fidelity = max(0.0, 1.0 - (personality_drift / 0.20) * 0.40)
        score = round((tone_consistency * 0.50 + drift_fidelity * 0.50) * 100, 1)
        issues: List[QualityIssue] = []


        if personality_drift > 0.15:
            issues.append(QualityIssue(
                metric_type=CompanionMetricType.PERSONALITY,
                title="Approaching Personality Drift Threshold",
                severity="MEDIUM",
                detected_drop=f"Drift: {personality_drift:.2f}",
                root_cause="Warmth/Formality variance across long sessions"
            ))

        grade = "A+" if score >= 95 else "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "F"

        return QualityScore(
            metric_type=CompanionMetricType.PERSONALITY,
            score=score,
            grade=grade,
            details={
                "personality_drift": personality_drift,
                "tone_consistency": tone_consistency
            },
            issues=issues
        )
