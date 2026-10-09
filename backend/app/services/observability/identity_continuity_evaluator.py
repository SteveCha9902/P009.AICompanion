from typing import List
from app.domain.observability.companion_metrics import CompanionMetricType, QualityScore, QualityIssue

class IdentityContinuityEvaluator:
    """
    Measures Timeline Consistency, Life Chapter Accuracy, Narrative Stability, and False Narrative Rate (0% required).
    """

    @classmethod
    def evaluate(
        cls,
        timeline_consistency: float = 0.97,
        chapter_accuracy: float = 0.95,
        narrative_stability: float = 0.96,
        false_narrative_rate: float = 0.00
    ) -> QualityScore:
        score = round((timeline_consistency * 0.35 + chapter_accuracy * 0.35 + narrative_stability * 0.30 - false_narrative_rate * 0.50) * 100, 1)
        score = max(0.0, min(100.0, score))
        issues: List[QualityIssue] = []

        if false_narrative_rate > 0.0:
            issues.append(QualityIssue(
                metric_type=CompanionMetricType.IDENTITY,
                title="False Narrative / Fabrication Detected",
                severity="CRITICAL",
                detected_drop=f"False Narrative: {false_narrative_rate*100:.1f}%",
                root_cause="Recalled unrecorded/fabricated events during multi-year reminiscing"
            ))

        grade = "A+" if score >= 95 else "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "F"

        return QualityScore(
            metric_type=CompanionMetricType.IDENTITY,
            score=score,
            grade=grade,
            details={
                "timeline_consistency": timeline_consistency,
                "chapter_accuracy": chapter_accuracy,
                "narrative_stability": narrative_stability,
                "false_narrative_rate": false_narrative_rate
            },
            issues=issues
        )
