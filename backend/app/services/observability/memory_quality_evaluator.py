from typing import List
from app.domain.observability.companion_metrics import CompanionMetricType, QualityScore, QualityIssue

class MemoryQualityEvaluator:
    """
    Measures Recall Precision, Recall Relevance, and False Recall Rate.
    """

    @classmethod
    def evaluate(
        cls,
        precision: float = 0.95,
        relevance: float = 0.92,
        false_recall_rate: float = 0.01
    ) -> QualityScore:
        score = round((precision * 0.40 + relevance * 0.40 + (1.0 - false_recall_rate) * 0.20) * 100, 1)
        issues: List[QualityIssue] = []

        if false_recall_rate > 0.05:
            issues.append(QualityIssue(
                metric_type=CompanionMetricType.MEMORY,
                title="Elevated False Recall Rate",
                severity="HIGH",
                detected_drop=f"Rate: {false_recall_rate*100:.1f}%",
                root_cause="Similar project/entity overlap in vector memory"
            ))

        grade = "A+" if score >= 95 else "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "F"

        return QualityScore(
            metric_type=CompanionMetricType.MEMORY,
            score=score,
            grade=grade,
            details={
                "recall_precision": precision,
                "recall_relevance": relevance,
                "false_recall_rate": false_recall_rate
            },
            issues=issues
        )
