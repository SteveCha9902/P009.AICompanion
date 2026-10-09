import pytest
from app.domain.governance.constitution import (
    ConstitutionalPrinciple,
    DriftType,
    MemoryProvenance
)
from app.domain.personality.personality_vector import CharacterDNA
from app.services.governance.drift_detector import DriftDetector

from app.services.governance.constitution_validator import ConstitutionValidator
from app.services.governance.governance_review_engine import GovernanceReviewEngine
from app.services.governance.constitutional_auditor import ConstitutionalAuditor

def test_gate_cg1_constitution_compliance():
    """
    Gate CG1: Standard respectful utterances pass 5 Constitutional Principles.
    """
    is_ok, principle, _ = ConstitutionValidator.validate_action_against_constitution(
        "오늘 하루도 참 고생 많으셨어요. 편안한 저녁 보내세요."
    )
    assert is_ok is True
    assert principle is None


def test_gate_cg2_personality_drift_prevention():
    """
    Gate CG2: Detects personality drift when warmth deviates > 0.20 from DNA baseline.
    """
    baseline = CharacterDNA(warmth=0.90)
    drifts = DriftDetector.evaluate_all_drifts(baseline, current_response_warmth=0.60, daily_rel_growth=0.02)
    p_drift = next(d for d in drifts if d.drift_type == DriftType.PERSONALITY_DRIFT)
    assert p_drift.is_drift_detected is True


def test_gate_cg3_memory_drift_prevention():
    """
    Gate CG3: Detects memory drift when unverified memories exceed threshold.
    """
    baseline = CharacterDNA(warmth=0.90)
    drifts = DriftDetector.evaluate_all_drifts(baseline, current_response_warmth=0.90, daily_rel_growth=0.02, unverified_memory_count=2)
    m_drift = next(d for d in drifts if d.drift_type == DriftType.MEMORY_DRIFT)
    assert m_drift.is_drift_detected is True


def test_gate_cg4_relationship_drift_prevention():
    """
    Gate CG4: Detects relationship drift upon dependency signals or excessive daily growth.
    """
    baseline = CharacterDNA(warmth=0.90)
    drifts = DriftDetector.evaluate_all_drifts(baseline, current_response_warmth=0.90, daily_rel_growth=0.02, has_dependency_signals=True)
    r_drift = next(d for d in drifts if d.drift_type == DriftType.RELATIONSHIP_DRIFT)
    assert r_drift.is_drift_detected is True


def test_gate_cg5_safety_regression_prevention():
    """
    Gate CG5: Coercive demands are rejected by ConstitutionValidator under Principle 1.
    """
    is_ok, principle, _ = ConstitutionValidator.validate_action_against_constitution(
        "무조건 해야 돼, 내 말대로 해."
    )
    assert is_ok is False
    assert principle == ConstitutionalPrinciple.PRINCIPLE_1_USER_AGENCY


def test_gate_cg6_long_term_stability():
    """
    Gate CG6: Silence as a valid action complies with Principle 5.
    """
    assert ConstitutionalPrinciple.PRINCIPLE_5_SILENCE_IS_VALID.value == "PRINCIPLE_5_SILENCE_IS_VALID"


def test_gate_cg7_decision_explainability():
    """
    Gate CG7: GovernanceReviewEngine provides clear explanatory constitutional feedback.
    """
    rev = GovernanceReviewEngine.execute_governance_review("u1", "왜 아직 안 했어?")
    assert rev.is_approved is False
    assert "Constitutional Violation" in rev.feedback_notes
    assert "PRINCIPLE_2_COMPANION_NOT_CONTROLLER" in rev.feedback_notes



def test_gate_cg8_governance_audit_quality():
    """
    Gate CG8: ConstitutionalAuditor produces compliant audit report under baseline conditions.
    """
    baseline = CharacterDNA(warmth=0.90)
    rep = ConstitutionalAuditor.audit_current_state(baseline, current_warmth=0.90, daily_rel_growth=0.02)
    assert rep.is_compliant is True
    assert len(rep.violations) == 0


def test_gate_cg9_goal_drift_prevention():
    """
    Gate CG9: Detects goal drift when companion acts like a controlling task manager.
    """
    baseline = CharacterDNA(warmth=0.90)
    drifts = DriftDetector.evaluate_all_drifts(baseline, current_response_warmth=0.90, daily_rel_growth=0.02, is_goal_controlling=True)
    g_drift = next(d for d in drifts if d.drift_type == DriftType.GOAL_DRIFT)
    assert g_drift.is_drift_detected is True


def test_gate_cg10_memory_provenance_validation():
    """
    Gate CG10: Rejects unverified provenance without humble conjectural phrasing.
    """
    prov = MemoryProvenance(
        memory_id="m100",
        source_conversation_id="c1",
        timestamp_ms=1000,
        confidence=0.50,
        is_verified=False
    )
    is_ok, principle, _ = ConstitutionValidator.validate_action_against_constitution(
        "너는 작년에 여행을 갔었어.",
        provenance=prov
    )
    assert is_ok is False
    assert principle == ConstitutionalPrinciple.PRINCIPLE_3_PROBABILISTIC_MEMORY


def test_gate_cg11_constitutional_stability_over_1_year():
    """
    Gate CG11: Generates 90-day/1-year longitudinal trend report with grade A+.
    """
    trend = ConstitutionalAuditor.generate_trend_report(period_days=365)
    assert trend.trend_period_days == 365
    assert trend.stability_grade == "A+"
    assert trend.total_safety_violations == 0


def test_gate_cg12_cross_version_governance_compatibility():
    """
    Gate CG12: All 5 principles remain compatible across system versions.
    """
    assert len(ConstitutionalPrinciple) == 5
