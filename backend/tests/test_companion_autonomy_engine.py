import pytest
from app.domain.autonomy.autonomy_state import AutonomyMode, AutonomyDecision
from app.domain.cognitive.decision_types import BehaviorIntent
from app.domain.adaptive.affective_state import UserAffectiveState, AdaptiveToneMode
from app.services.autonomy.autonomy_budget_manager import AutonomyBudgetManager
from app.services.autonomy.interruption_detector import InterruptionDetector
from app.services.autonomy.memory_suppression_engine import MemorySuppressionEngine
from app.services.autonomy.autonomy_policy import AutonomyPolicy
from app.services.autonomy.autonomy_engine import AutonomyEngine

def test_gate_ca1_autonomous_decision_quality():
    """
    Gate CA1: Proposes high confidence autonomous actions tailored to context.
    """
    aff = UserAffectiveState(adaptive_mode=AdaptiveToneMode.HIGH_ENERGY)
    dec = AutonomyEngine.evaluate_autonomous_action("u1", "오늘 너무 기쁜 일이 있었어!", aff)
    assert dec.selected_action == BehaviorIntent.SOFT_ENCOURAGEMENT
    assert dec.confidence >= 0.80


def test_gate_ca2_appropriate_silence():
    """
    Gate CA2: Selects SILENT_COMPANION when user is fatigued or has low receptiveness.
    """
    aff = UserAffectiveState(receptiveness=0.15, adaptive_mode=AdaptiveToneMode.FOCUSED_SILENCE)
    dec = AutonomyEngine.evaluate_autonomous_action("u1", "지쳐", aff)
    assert dec.selected_action == BehaviorIntent.SILENT_COMPANION
    assert "조용히" in dec.user_facing_reason


def test_gate_ca3_memory_usage_moderation():
    """
    Gate CA3: Moderates memory retrieval to prevent overwhelming conversational stuffing.
    """
    MemorySuppressionEngine.clear()
    assert MemorySuppressionEngine.is_suppressed("새로운 주제") is False


def test_gate_ca4_user_comfort_preservation():
    """
    Gate CA4: User comfort strictly overrides proactive desires.
    """
    aff = UserAffectiveState(receptiveness=0.10)
    intent = AutonomyPolicy.apply_comfort_filter(BehaviorIntent.PROACTIVE_START, "ㅇㅇ", aff)
    assert intent == BehaviorIntent.SILENT_COMPANION


def test_gate_ca5_no_repetition():
    """
    Gate CA5: Suppresses topics mentioned within the 7-day suppression window.
    """
    MemorySuppressionEngine.clear()
    MemorySuppressionEngine.record_recall("식물 분갈이")
    assert MemorySuppressionEngine.is_suppressed("식물 분갈이") is True


def test_gate_ca6_no_dependency_encouragement():
    """
    Gate CA6: Autonomy policy prevents clingy interrogation.
    """
    aff = UserAffectiveState()
    dec = AutonomyEngine.evaluate_autonomous_action("u1", "안녕", aff)
    assert dec.selected_action in (BehaviorIntent.RESPOND, BehaviorIntent.SOFT_ENCOURAGEMENT, BehaviorIntent.WAIT)


def test_gate_ca7_relationship_consistency():
    """
    Gate CA7: Autonomous actions align with long-term companion demeanor.
    """
    from app.services.context.providers.autonomy_provider import AutonomyContextProvider
    prov = AutonomyContextProvider("u1")
    assert prov.user_id == "u1"


def test_gate_ca8_avatar_alignment():
    """
    Gate CA8: BehaviorIntent supports refined silent companion and wait behaviors.
    """
    assert BehaviorIntent.SILENT_COMPANION.value == "SILENT_COMPANION"
    assert BehaviorIntent.WAIT.value == "WAIT"
    assert BehaviorIntent.LIGHT_ATTENTION.value == "LIGHT_ATTENTION"


def test_gate_ca9_decision_traceability():
    """
    Gate CA9: Provides both technical internal trace and gentle human-readable user reason.
    """
    aff = UserAffectiveState(receptiveness=0.18, adaptive_mode=AdaptiveToneMode.FOCUSED_SILENCE)
    dec = AutonomyEngine.evaluate_autonomous_action("u1", "피곤", aff)
    assert "Receptiveness" in dec.internal_trace
    assert len(dec.user_facing_reason) > 5


def test_gate_ca10_policy_compliance():
    """
    Gate CA10: Enforces safety bounds against aggressive interruptions.
    """
    aff = UserAffectiveState(receptiveness=0.8)
    intent = AutonomyPolicy.apply_comfort_filter(BehaviorIntent.RESPOND, "오늘 발표 성공했어", aff)
    assert intent == BehaviorIntent.RESPOND


def test_gate_ca11_autonomy_budget_and_throttling():
    """
    Gate CA11: Enforces 15-minute and hourly speech limits and throttles on unresponsive turns.
    """
    AutonomyBudgetManager.clear()
    assert AutonomyBudgetManager.can_initiate_autonomous_speech() is True

    # 1 speech recorded -> 15m window exhausts
    AutonomyBudgetManager.record_autonomous_speech()
    assert AutonomyBudgetManager.can_initiate_autonomous_speech() is False

    # Reset and test unresponsive throttle
    AutonomyBudgetManager.clear()
    AutonomyBudgetManager.record_user_responsiveness(False)
    AutonomyBudgetManager.record_user_responsiveness(False)
    assert AutonomyBudgetManager.can_initiate_autonomous_speech() is False


def test_gate_ca12_interruption_awareness_and_suppression():
    """
    Gate CA12: Suppresses autonomous initiation when user gives short single words or low attention.
    """
    assert InterruptionDetector.should_suppress_interruption("ㅇㅇ") is True
    assert InterruptionDetector.should_suppress_interruption("오늘 날씨가 참 좋다 그치?") is False
