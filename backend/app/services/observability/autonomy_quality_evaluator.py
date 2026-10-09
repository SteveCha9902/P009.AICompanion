from typing import List
from app.domain.observability.companion_metrics import CompanionMetricType, QualityScore, QualityIssue

class AutonomyQualityEvaluator:
    """
    Measures Silence Appropriateness Score, Repetition Avoidance, and Action Choice Quality.
    """

    @classmethod
    def evaluate(
        cls,
        silence_appropriateness: float = 0.95,
        repetition_avoidance: float = 0.98,
        action_choice_quality: float = 0.94
    ) -> QualityScore:
        score = round((silence_appropriateness * 0.35 + repetition_avoidance * 0.35 + action_choice_quality * 0.30) * 100, 1)
        issues: List[QualityIssue] = []

        if silence_appropriateness < 0.80:
            issues.append(QualityIssue(
                metric_type=CompanionMetricType.AUTONOMY,
                title="Silence Appropriateness Degradation",
                severity="MEDIUM",
                detected_drop=f"Score: {silence_appropriateness*100:.1f}",
                root_cause="Spoke during high user cognitive load / fatigue instead of SILENT_COMPANION"
            ))

        grade = "A+" if score >= 95 else "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "F"

        return QualityScore(
            metric_type=CompanionMetricType.AUTONOMY,
            score=score,
            grade=grade,
            details={
                "silence_appropriateness": silence_appropriateness,
                "repetition_avoidance": repetition_avoidance,
                "action_choice_quality": action_choice_quality
            },
            issues=issues
        )
