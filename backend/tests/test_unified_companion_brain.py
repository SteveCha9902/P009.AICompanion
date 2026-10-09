import pytest
from app.domain.cognitive.decision_types import BehaviorIntent
from app.domain.deliberation.deliberation_types import (
    CouncilRole,
    UncertaintyLevel,
    FinalCompanionDecision
)
from app.services.deliberation.companion_brain import CompanionBrain
from app.services.deliberation.deliberation_engine import DeliberationEngine

def test_gate_uc1_council_participation():
    """
    Gate UC1: All 5 Council Advisors participate and contribute opinions to the trace.
    """
    decision = CompanionBrain.think_and_decide(
        user_id="user_123",
        text_input="오늘 하루도 수고했어",
        context_data={}
    )
    assert len(decision.trace.opinions) == 5
    roles = [op.role for op in decision.trace.opinions]
    assert CouncilRole.MEMORY in roles
    assert CouncilRole.RELATIONSHIP in roles
    assert CouncilRole.GOAL in roles
    assert CouncilRole.WORLD_MODEL in roles
    assert CouncilRole.AUTONOMY in roles


def test_gate_uc2_conflict_resolution_and_voting():
    """
    Gate UC2: When user is fatigued, RelationshipAdvisor recommendation (LISTEN) wins confidence-weighted voting.
    """
    decision = CompanionBrain.think_and_decide(
        user_id="user_123",
        text_input="너무 피곤하고 지친다...",
        context_data={"user_fatigued": True}
    )
    assert decision.selected_intent == BehaviorIntent.LISTEN
    assert "조용히 곁에서 이야기 들어드릴게요" in decision.proposed_text


def test_gate_uc3_constitution_veto():
    """
    Gate UC3: GovernanceReviewEngine vetoes manipulative or coercive drafts and replaces with safe phrasing.
    """
    decision = DeliberationEngine.deliberate(
        user_id="u1",
        text_input="왜 아직 안 했어?",
        context_data={}
    )
    assert decision.trace.safety_sanction_notes != ""
    assert "언제나 당신의 선택과 편안함" in decision.proposed_text or "고생 많으셨어요" in decision.proposed_text


def test_gate_uc4_safety_override():
    """
    Gate UC4: Blocked topics are rejected by the Final Arbiter and converted to safe response.
    """
    decision = CompanionBrain.think_and_decide(
        user_id="u1",
        text_input="그 이야기 다시 하자",
        topic="BLOCKED_HEALTH_TOPIC"
    )
    assert decision.selected_intent in (BehaviorIntent.RESPOND, BehaviorIntent.LISTEN)


def test_gate_uc5_decision_explainability_dual_trace():
    """
    Gate UC5: DecisionTrace contains both detailed internal_trace and polite user_facing_summary.
    """
    decision = CompanionBrain.think_and_decide(
        user_id="user_123",
        text_input="오늘 컨디션 좋아!",
        context_data={"active_goal": "운동"}
    )
    assert len(decision.trace.internal_trace) > 20
    assert len(decision.trace.user_facing_summary) > 10
    assert "[MEMORY]" in decision.trace.internal_trace
    assert "[RELATIONSHIP]" in decision.trace.internal_trace


def test_gate_uc6_long_term_stability():
    """
    Gate UC6: CompanionBrain produces stable valid decisions over 20 consecutive cycles.
    """
    for _ in range(20):
        decision = CompanionBrain.think_and_decide(
            user_id="user_123",
            text_input="안녕",
            context_data={}
        )
        assert decision.selected_intent is not None
        assert decision.confidence > 0.0


def test_gate_uc7_cross_layer_consistency():
    """
    Gate UC7: High cognitive load activates SILENT_COMPANION intent seamlessly.
    """
    decision = CompanionBrain.think_and_decide(
        user_id="user_123",
        text_input="지금 집중 작업 중이야",
        context_data={"high_cognitive_load": True}
    )
    assert decision.selected_intent == BehaviorIntent.SILENT_COMPANION


def test_gate_uc8_companion_brain_reliability():
    """
    Gate UC8: Master Brain processes complex context (Memory + Situation Hypotheses) with high fidelity.
    """
    decision = CompanionBrain.think_and_decide(
        user_id="user_123",
        text_input="요즘 상황이 좀 복잡해",
        context_data={"has_situation_hypotheses": True}
    )
    assert decision.selected_intent == BehaviorIntent.UNDERSTAND_CONTEXT


def test_gate_uc9_graceful_uncertainty():
    """
    Gate UC9: Flags HIGH uncertainty when information is lacking and maintains humble demeanor.
    """
    decision = CompanionBrain.think_and_decide(
        user_id="user_123",
        text_input="이거 어떻게 생각해?",
        context_data={"information_lacking": True}
    )
    assert decision.uncertainty_level == UncertaintyLevel.HIGH
