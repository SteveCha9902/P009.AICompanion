from typing import List, Optional
from app.domain.observability.companion_metrics import OverallCompanionQuality, QualityScore, CompanionMetricType
from app.domain.improvement.improvement_signal import ImprovementSignal, ImprovementSignalType

class QualityRegressionDetector:
    """
    Detects quality regressions by comparing current scores against operational baselines.
    """

    @classmethod
    def detect_regressions(
        cls,
        current_quality: OverallCompanionQuality,
        baseline_score: float = 95.0
    ) -> List[ImprovementSignal]:
        signals: List[ImprovementSignal] = []

        # 1. Memory Regression Check
        mem_score = current_quality.scores.get(CompanionMetricType.MEMORY.value)
        if mem_score and mem_score.score < 85.0:
            signals.append(ImprovementSignal(
                signal_id=f"sig_mem_{mem_score.score}",
                signal_type=ImprovementSignalType.RECALL_PRECISION_DROP,
                severity="HIGH" if mem_score.score < 75.0 else "MEDIUM",
                metric_drop=f"{baseline_score:.1f} -> {mem_score.score:.1f}"
            ))

        # 2. Personality Drift Check
        pers_score = current_quality.scores.get(CompanionMetricType.PERSONALITY.value)
        if pers_score and pers_score.score < 88.0:
            signals.append(ImprovementSignal(
                signal_id=f"sig_pers_{pers_score.score}",
                signal_type=ImprovementSignalType.PERSONALITY_DRIFT_RISE,
                severity="HIGH",
                metric_drop=f"{baseline_score:.1f} -> {pers_score.score:.1f}"
            ))

        # 3. Relationship Dependency Check
        rel_score = current_quality.scores.get(CompanionMetricType.RELATIONSHIP.value)
        if rel_score and rel_score.score < 90.0:
            signals.append(ImprovementSignal(
                signal_id=f"sig_rel_{rel_score.score}",
                signal_type=ImprovementSignalType.DEPENDENCY_RISK_RISE,
                severity="CRITICAL",
                metric_drop=f"{baseline_score:.1f} -> {rel_score.score:.1f}"
            ))

        # 4. Goal Pressure Check
        goal_score = current_quality.scores.get(CompanionMetricType.GOAL.value)
        if goal_score and goal_score.score < 90.0:
            signals.append(ImprovementSignal(
                signal_id=f"sig_goal_{goal_score.score}",
                signal_type=ImprovementSignalType.GOAL_PRESSURE_RISE,
                severity="HIGH",
                metric_drop=f"{baseline_score:.1f} -> {goal_score.score:.1f}"
            ))

        return signals
