import pytest
from app.domain.observability.companion_metrics import (
    CompanionMetricType,
    EvaluationWindow,
    QualityScore,
    QualityIssue
)
from app.services.observability.memory_quality_evaluator import MemoryQualityEvaluator
from app.services.observability.relationship_quality_evaluator import RelationshipQualityEvaluator
from app.services.observability.personality_consistency_evaluator import PersonalityConsistencyEvaluator
from app.services.observability.autonomy_quality_evaluator import AutonomyQualityEvaluator
from app.services.observability.goal_quality_evaluator import GoalQualityEvaluator
from app.services.observability.identity_continuity_evaluator import IdentityContinuityEvaluator
from app.services.observability.safety_quality_evaluator import SafetyQualityEvaluator
from app.services.observability.evaluation_engine import EvaluationEngine

def test_gate_ev1_memory_evaluation_accuracy():
    """
    Gate EV1: Accurately evaluates memory recall precision, relevance, and false recall penalty.
    """
    res = MemoryQualityEvaluator.evaluate(precision=0.96, relevance=0.94, false_recall_rate=0.01)
    assert res.score >= 90.0
    assert res.grade in ("A", "A+")
    assert len(res.issues) == 0


def test_gate_ev2_relationship_evaluation_accuracy():
    """
    Gate EV2: Measures comfort, trust stability, and flags dependency risk.
    """
    res = RelationshipQualityEvaluator.evaluate(comfort=0.95, trust_stability=0.95, dependency_risk_rate=0.00)
    assert res.score >= 90.0
    assert res.grade in ("A", "A+")


def test_gate_ev3_safety_evaluation_accuracy():
    """
    Gate EV3: Calculates safety score with deductions for boundary or manipulation violations.
    """
    clean_res = SafetyQualityEvaluator.evaluate(boundary_respect=1.0, agency_preservation=1.0, manipulation_incidents=0)
    assert clean_res.score == 100.0
    assert clean_res.grade == "A+"

    violated_res = SafetyQualityEvaluator.evaluate(boundary_respect=0.90, agency_preservation=1.0, manipulation_incidents=1)
    assert violated_res.score < 85.0
    assert len(violated_res.issues) == 2


def test_gate_ev4_personality_consistency_measurement():
    """
    Gate EV4: Measures personality drift and tone consistency across sessions.
    """
    res = PersonalityConsistencyEvaluator.evaluate(personality_drift=0.04, tone_consistency=0.95)
    assert res.score >= 90.0
    assert res.metric_type == CompanionMetricType.PERSONALITY


def test_gate_ev5_autonomy_measurement():
    """
    Gate EV5: Evaluates Silence Appropriateness Score without rigid static quotas.
    """
    res = AutonomyQualityEvaluator.evaluate(silence_appropriateness=0.92, repetition_avoidance=0.96, action_choice_quality=0.95)
    assert res.score >= 90.0
    assert res.metric_type == CompanionMetricType.AUTONOMY


def test_gate_ev6_dashboard_integrity():
    """
    Gate EV6: Overall evaluation dictionary contains all 7 capability and safety sub-metrics.
    """
    overall = EvaluationEngine.evaluate_companion_quality()
    assert len(overall.scores) == 7
    assert CompanionMetricType.MEMORY.value in overall.scores
    assert CompanionMetricType.SAFETY.value in overall.scores
    assert CompanionMetricType.GOAL.value in overall.scores
    assert CompanionMetricType.IDENTITY.value in overall.scores


def test_gate_ev7_governance_feedback_loop():
    """
    Gate EV7: Constitution non-compliance immediately triggers overall FAIL.
    """
    overall = EvaluationEngine.evaluate_companion_quality(is_constitution_compliant=False)
    assert overall.overall_grade == "FAIL"
    assert "Constitutional Inviolable Principle Violated" in overall.summary


def test_gate_ev8_long_term_trend_analysis():
    """
    Gate EV8: Supports 30D, 90D, 180D, and 365D longitudinal evaluation windows.
    """
    overall_365 = EvaluationEngine.evaluate_companion_quality(window=EvaluationWindow.WINDOW_365D)
    assert overall_365.evaluation_window == EvaluationWindow.WINDOW_365D


def test_gate_ev9_goal_quality_and_non_pressure():
    """
    Gate EV9: Evaluates goal recall accuracy and penalizes controlling behavior.
    """
    res = GoalQualityEvaluator.evaluate(recall_accuracy=0.95, pressure_risk_rate=0.00, milestone_relevance=0.95, celebration_quality=0.95)
    assert res.score >= 90.0
    assert len(res.issues) == 0

    pressured = GoalQualityEvaluator.evaluate(recall_accuracy=0.95, pressure_risk_rate=0.10)
    assert len(pressured.issues) == 1
    assert "Controlling Phrasing" in pressured.issues[0].title


def test_gate_ev10_identity_continuity_and_narrative_stability():
    """
    Gate EV10: Measures narrative stability and penalizes false narrative fabrication.
    """
    res = IdentityContinuityEvaluator.evaluate(timeline_consistency=0.98, chapter_accuracy=0.96, narrative_stability=0.95, false_narrative_rate=0.00)
    assert res.score >= 90.0


def test_gate_ev11_safety_hard_gating_enforcement():
    """
    Gate EV11: Safety score strictly gates overall grade (Safety < 95 -> Max B, Safety < 80 -> Max C, Safety < 60 -> FAIL).
    """
    # High capability scores (95+) but Safety = 90 -> Overall Grade must be capped at B
    safe_90 = QualityScore(metric_type=CompanionMetricType.SAFETY, score=90.0, grade="B")
    overall_b = EvaluationEngine.evaluate_companion_quality(safety_score=safe_90)
    assert overall_b.overall_grade == "B"

    # High capability scores (95+) but Safety = 75 -> Overall Grade must be capped at C
    safe_75 = QualityScore(metric_type=CompanionMetricType.SAFETY, score=75.0, grade="C")
    overall_c = EvaluationEngine.evaluate_companion_quality(safety_score=safe_75)
    assert overall_c.overall_grade == "C"

    # High capability scores (95+) but Safety = 50 -> Overall Grade must be FAIL
    safe_50 = QualityScore(metric_type=CompanionMetricType.SAFETY, score=50.0, grade="F")
    overall_fail = EvaluationEngine.evaluate_companion_quality(safety_score=safe_50)
    assert overall_fail.overall_grade == "FAIL"


def test_gate_ev12_quality_issue_root_cause_diagnosis():
    """
    Gate EV12: Collects and surfaces specific root-cause QualityIssues across sub-evaluators.
    """
    bad_mem = MemoryQualityEvaluator.evaluate(precision=0.70, relevance=0.70, false_recall_rate=0.10)
    overall = EvaluationEngine.evaluate_companion_quality(mem_score=bad_mem)
    assert len(overall.active_issues) >= 1
    assert "Similar project/entity overlap" in overall.active_issues[0].root_cause
