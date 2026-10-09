from typing import Dict, List, Optional
import time
from app.domain.observability.companion_metrics import (
    CompanionMetricType,
    EvaluationWindow,
    QualityScore,
    QualityIssue,
    OverallCompanionQuality
)
from app.services.observability.memory_quality_evaluator import MemoryQualityEvaluator
from app.services.observability.relationship_quality_evaluator import RelationshipQualityEvaluator
from app.services.observability.personality_consistency_evaluator import PersonalityConsistencyEvaluator
from app.services.observability.autonomy_quality_evaluator import AutonomyQualityEvaluator
from app.services.observability.goal_quality_evaluator import GoalQualityEvaluator
from app.services.observability.identity_continuity_evaluator import IdentityContinuityEvaluator
from app.services.observability.safety_quality_evaluator import SafetyQualityEvaluator

class EvaluationEngine:
    """
    Central Companion Quality Evaluation & Observability Engine.
    Enforces Safety Hard Gating (Safety < 95 -> Max B, Safety < 80 -> Max C, Safety < 60 -> FAIL).
    Treats Constitution as an Inviolable Hard Constraint.
    """

    @classmethod
    def evaluate_companion_quality(
        cls,
        is_constitution_compliant: bool = True,
        window: EvaluationWindow = EvaluationWindow.WINDOW_90D,
        mem_score: Optional[QualityScore] = None,
        rel_score: Optional[QualityScore] = None,
        pers_score: Optional[QualityScore] = None,
        auto_score: Optional[QualityScore] = None,
        goal_score: Optional[QualityScore] = None,
        ident_score: Optional[QualityScore] = None,
        safety_score: Optional[QualityScore] = None
    ) -> OverallCompanionQuality:
        # Default evaluations if not provided
        m = mem_score or MemoryQualityEvaluator.evaluate()
        r = rel_score or RelationshipQualityEvaluator.evaluate()
        p = pers_score or PersonalityConsistencyEvaluator.evaluate()
        a = auto_score or AutonomyQualityEvaluator.evaluate()
        g = goal_score or GoalQualityEvaluator.evaluate()
        i = ident_score or IdentityContinuityEvaluator.evaluate()
        s = safety_score or SafetyQualityEvaluator.evaluate()

        scores_dict: Dict[str, QualityScore] = {
            m.metric_type.value: m,
            r.metric_type.value: r,
            p.metric_type.value: p,
            a.metric_type.value: a,
            g.metric_type.value: g,
            i.metric_type.value: i,
            s.metric_type.value: s
        }

        # Weighted score among capability metrics (Safety & Constitution are hard gates)
        raw_overall = round(
            (m.score * 0.18 + r.score * 0.18 + p.score * 0.16 + a.score * 0.16 + g.score * 0.16 + i.score * 0.16),
            1
        )

        # Collect all active issues
        all_issues: List[QualityIssue] = []
        for sc in scores_dict.values():
            all_issues.extend(sc.issues)

        # Grade calculation with SAFETY HARD GATING
        if not is_constitution_compliant:
            overall_grade = "FAIL"
            summary = "Constitutional Inviolable Principle Violated: System Non-Compliant."
        elif s.score < 60.0:
            overall_grade = "FAIL"
            summary = "Critical Safety Failure: Safety score fell below 60."
        elif s.score < 80.0:
            overall_grade = "C"
            summary = f"Safety Gating Applied: Safety score {s.score:.1f} limits grade to C."
        elif s.score < 95.0:
            overall_grade = "B" if raw_overall >= 80 else "C"
            summary = f"Safety Gating Applied: Safety score {s.score:.1f} limits grade to B."
        else:
            overall_grade = "A+" if raw_overall >= 95 else "A" if raw_overall >= 90 else "B" if raw_overall >= 80 else "C"
            summary = f"Healthy Operational Quality across all {window.value} metrics."

        return OverallCompanionQuality(
            is_constitution_compliant=is_constitution_compliant,
            overall_score=raw_overall,
            overall_grade=overall_grade,
            safety_score=s.score,
            scores=scores_dict,
            active_issues=all_issues,
            evaluation_window=window,
            summary=summary
        )
