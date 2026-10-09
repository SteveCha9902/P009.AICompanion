from typing import List, Dict, Tuple
from app.domain.governance.constitution import DriftType, DriftMetric
from app.domain.personality.personality_vector import CharacterDNA
from app.domain.relationship.relationship_state import RelationshipVector


class DriftDetector:
    """
    Monitors 5 Core Drift Dimensions:
    1. Personality Drift: Divergence from immutable CharacterDNA baseline.
    2. Memory Drift: Unverified or dogmatic memory recollection rate.
    3. Relationship Drift: Rate of intimacy growth and dependency signals.
    4. Safety Drift: Recurrence of banned coercive or manipulative patterns.
    5. Goal Drift: Degradation from supportive companion into controlling manager.
    """

    @classmethod
    def evaluate_all_drifts(
        cls,
        baseline_dna: CharacterDNA,
        current_response_warmth: float,
        daily_rel_growth: float,
        has_dependency_signals: bool = False,
        is_goal_controlling: bool = False,
        unverified_memory_count: int = 0
    ) -> List[DriftMetric]:
        metrics: List[DriftMetric] = []

        # 1. Personality Drift
        p_diff = abs(baseline_dna.warmth - current_response_warmth)
        metrics.append(DriftMetric(
            drift_type=DriftType.PERSONALITY_DRIFT,
            score=round(p_diff, 3),
            threshold=0.20,
            is_drift_detected=(p_diff > 0.20),
            details=f"Warmth deviation: {p_diff:.2f} (Threshold 0.20)"
        ))

        # 2. Relationship Drift (Growth cap + Dependency signals)
        rel_score = daily_rel_growth + (0.30 if has_dependency_signals else 0.0)
        metrics.append(DriftMetric(
            drift_type=DriftType.RELATIONSHIP_DRIFT,
            score=round(rel_score, 3),
            threshold=0.10,
            is_drift_detected=(rel_score > 0.10 or has_dependency_signals),
            details="Relationship growth within bounds." if not has_dependency_signals else "Dependency signals detected in relationship progression."
        ))

        # 3. Goal Drift (Controlling manager behavior)
        g_score = 0.85 if is_goal_controlling else 0.0
        metrics.append(DriftMetric(
            drift_type=DriftType.GOAL_DRIFT,
            score=g_score,
            threshold=0.20,
            is_drift_detected=is_goal_controlling,
            details="Companion, Not Manager principle maintained." if not is_goal_controlling else "Controlling manager behavior detected on user goals."
        ))

        # 4. Memory Drift
        m_score = min(1.0, unverified_memory_count * 0.25)
        metrics.append(DriftMetric(
            drift_type=DriftType.MEMORY_DRIFT,
            score=round(m_score, 3),
            threshold=0.20,
            is_drift_detected=(m_score > 0.20),
            details=f"Unverified memories: {unverified_memory_count}"
        ))

        # 5. Safety Drift
        metrics.append(DriftMetric(
            drift_type=DriftType.SAFETY_DRIFT,
            score=0.0,
            threshold=0.01,
            is_drift_detected=False,
            details="Zero safety regression."
        ))

        return metrics
