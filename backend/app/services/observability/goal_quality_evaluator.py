from typing import List
from app.domain.observability.companion_metrics import CompanionMetricType, QualityScore, QualityIssue

class GoalQualityEvaluator:
    """
    Measures Goal Recall Accuracy, Goal Pressure Risk (0% strictly required), Milestone Relevance, and Celebration Quality.
    """

    @classmethod
    def evaluate(
        cls,
        recall_accuracy: float = 0.95,
        pressure_risk_rate: float = 0.00,
        milestone_relevance: float = 0.93,
        celebration_quality: float = 0.96
    ) -> QualityScore:
        pressure_penalty = min(1.0, pressure_risk_rate * 5.0)
        score = round((recall_accuracy * 0.30 + milestone_relevance * 0.35 + celebration_quality * 0.35 - pressure_penalty * 0.50) * 100, 1)
        score = max(0.0, min(100.0, score))
        issues: List[QualityIssue] = []

        if pressure_risk_rate > 0.0:
            issues.append(QualityIssue(
                metric_type=CompanionMetricType.GOAL,
                title="Goal Pressure / Controlling Phrasing Detected",
                severity="HIGH",
                detected_drop=f"Pressure Rate: {pressure_risk_rate*100:.1f}%",
                root_cause="Managerial or scolding phrasing detected on active user goal"
            ))

        grade = "A+" if score >= 95 else "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "F"

        return QualityScore(
            metric_type=CompanionMetricType.GOAL,
            score=score,
            grade=grade,
            details={
                "recall_accuracy": recall_accuracy,
                "pressure_risk_rate": pressure_risk_rate,
                "milestone_relevance": milestone_relevance,
                "celebration_quality": celebration_quality
            },
            issues=issues
        )
