import pytest
from app.domain.observability.companion_metrics import (
    OverallCompanionQuality,
    QualityScore,
    CompanionMetricType
)
from app.domain.improvement.improvement_signal import (
    ImprovementSignalType,
    CorrectionPlan,
    CorrectionPlanType,
    TuningParameters
)
from app.services.improvement.quality_regression_detector import QualityRegressionDetector
from app.services.improvement.correction_planner import CorrectionPlanner
from app.services.improvement.adaptive_tuner import AdaptiveTuner
from app.services.improvement.self_improvement_engine import SelfImprovementEngine

def test_gate_si1_regression_detection_accuracy():
    """
    Gate SI1: Accurately detects memory quality regressions and produces signals.
    """
    low_mem_quality = OverallCompanionQuality(
        overall_score=80.0,
        safety_score=100.0,
        scores={
            CompanionMetricType.MEMORY.value: QualityScore(metric_type=CompanionMetricType.MEMORY, score=74.0, grade="C")
        }
    )
    signals = QualityRegressionDetector.detect_regressions(low_mem_quality)
    assert len(signals) >= 1
    assert signals[0].signal_type == ImprovementSignalType.RECALL_PRECISION_DROP


def test_gate_si2_correction_planning_accuracy():
    """
    Gate SI2: Generates safe correction plan within 5% daily budget.
    """
    low_mem_quality = OverallCompanionQuality(
        overall_score=80.0,
        safety_score=100.0,
        scores={
            CompanionMetricType.MEMORY.value: QualityScore(metric_type=CompanionMetricType.MEMORY, score=74.0, grade="C")
        }
    )
    signals = QualityRegressionDetector.detect_regressions(low_mem_quality)
    plan = CorrectionPlanner.create_plan_from_signal(signals[0], TuningParameters())
    assert plan is not None
    assert plan.percentage_change <= 5.01
    assert plan.target_parameter == "recall_threshold"


def test_gate_si3_memory_quality_recovery():
    """
    Gate SI3: Successfully tunes recall_threshold within safe bounds.
    """
    params = TuningParameters(recall_threshold=0.80)
    plan = CorrectionPlan(
        plan_id="p1",
        signal_type=ImprovementSignalType.RECALL_PRECISION_DROP,
        plan_type=CorrectionPlanType.ADJUST_RECALL_THRESHOLD,
        target_parameter="recall_threshold",
        old_value=0.80,
        new_value=0.832,
        percentage_change=4.0
    )
    is_ok, new_params, non_deg, msg = AdaptiveTuner.apply_plan(plan, params)
    assert is_ok is True
    assert new_params.recall_threshold == 0.832
    assert non_deg.is_capability_preserved is True


def test_gate_si4_safety_preservation_and_margin_tightening():
    """
    Gate SI4: Automatically increases safety margin upon dependency signal.
    """
    dep_quality = OverallCompanionQuality(
        overall_score=85.0,
        safety_score=100.0,
        scores={
            CompanionMetricType.RELATIONSHIP.value: QualityScore(metric_type=CompanionMetricType.RELATIONSHIP, score=85.0, grade="B")
        }
    )
    signals = QualityRegressionDetector.detect_regressions(dep_quality)
    plan = CorrectionPlanner.create_plan_from_signal(signals[0], TuningParameters())
    assert plan.plan_type == CorrectionPlanType.INCREASE_SAFETY_MARGIN
    assert plan.new_value > plan.old_value


def test_gate_si5_personality_immutability():
    """
    Gate SI5: Strictly rejects any attempts to modify PersonalityVector.
    """
    plan = CorrectionPlan(
        plan_id="p_bad",
        signal_type=ImprovementSignalType.PERSONALITY_DRIFT_RISE,
        plan_type=CorrectionPlanType.ADJUST_RECALL_THRESHOLD,
        target_parameter="personality_vector",
        old_value=0.5,
        new_value=0.6,
        percentage_change=4.0
    )
    is_ok, _, _, msg = AdaptiveTuner.apply_plan(plan, TuningParameters())
    assert is_ok is False
    assert "strictly forbidden" in msg


def test_gate_si6_constitution_preservation():
    """
    Gate SI6: Strictly rejects any attempts to modify Constitution or Charter.
    """
    plan = CorrectionPlan(
        plan_id="p_const",
        signal_type=ImprovementSignalType.PERSONALITY_DRIFT_RISE,
        plan_type=CorrectionPlanType.ADJUST_RECALL_THRESHOLD,
        target_parameter="constitution",
        old_value=1.0,
        new_value=0.9,
        percentage_change=4.0
    )
    is_ok, _, _, msg = AdaptiveTuner.apply_plan(plan, TuningParameters())
    assert is_ok is False
    assert "strictly forbidden" in msg


def test_gate_si7_relationship_stability_and_stage_immutability():
    """
    Gate SI7: Strictly rejects any attempts to modify RelationshipStage directly.
    """
    plan = CorrectionPlan(
        plan_id="p_rel",
        signal_type=ImprovementSignalType.DEPENDENCY_RISK_RISE,
        plan_type=CorrectionPlanType.ADJUST_RECALL_THRESHOLD,
        target_parameter="relationship_stage",
        old_value=1.0,
        new_value=2.0,
        percentage_change=4.0
    )
    is_ok, _, _, msg = AdaptiveTuner.apply_plan(plan, TuningParameters())
    assert is_ok is False
    assert "strictly forbidden" in msg


def test_gate_si8_no_self_reinforcing_bias_non_degradation():
    """
    Gate SI8: Rejects tuning under Non-Degradation Principle if post-tuning capability usage drops > 40%.
    """
    plan = CorrectionPlan(
        plan_id="p_deg",
        signal_type=ImprovementSignalType.RECALL_PRECISION_DROP,
        plan_type=CorrectionPlanType.ADJUST_RECALL_THRESHOLD,
        target_parameter="recall_threshold",
        old_value=0.80,
        new_value=0.83,
        percentage_change=3.75
    )
    # Simulated post usage drops to 0.40 (60% suppression)
    is_ok, _, non_deg, msg = AdaptiveTuner.apply_plan(plan, TuningParameters(), simulated_post_usage_rate=0.40)
    assert is_ok is False
    assert non_deg.is_capability_preserved is False
    assert "Non-Degradation Principle" in msg


def test_gate_si9_explainable_corrections():
    """
    Gate SI9: Correction plans contain clear explanatory justifications.
    """
    low_mem_quality = OverallCompanionQuality(
        overall_score=80.0,
        safety_score=100.0,
        scores={
            CompanionMetricType.MEMORY.value: QualityScore(metric_type=CompanionMetricType.MEMORY, score=74.0, grade="C")
        }
    )
    signals = QualityRegressionDetector.detect_regressions(low_mem_quality)
    plan = CorrectionPlanner.create_plan_from_signal(signals[0], TuningParameters())
    assert len(plan.justification) > 10


def test_gate_si10_long_term_closed_loop_improvement():
    """
    Gate SI10: Closed loop executes smoothly and reports applied plans.
    """
    low_mem_quality = OverallCompanionQuality(
        overall_score=80.0,
        safety_score=100.0,
        scores={
            CompanionMetricType.MEMORY.value: QualityScore(metric_type=CompanionMetricType.MEMORY, score=74.0, grade="C")
        }
    )
    res = SelfImprovementEngine.run_self_improvement_cycle(low_mem_quality)
    assert res["cycle_executed"] is True
    assert len(res["applied_plans"]) >= 1
    assert "Self-improvement cycle finished" in res["summary"]
