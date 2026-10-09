import pytest
from app.domain.cognitive.decision_types import BehaviorIntent
from app.domain.world_model.situation_model import (
    SituationModel,
    EnvironmentalFactors,
    SituationHypothesis,
    AnticipatedSupportOpportunity
)
from app.services.world_model.causal_reasoning_engine import CausalReasoningEngine
from app.services.world_model.routine_detector import RoutineDetector
from app.services.world_model.forecast_engine import ForecastEngine
from app.services.world_model.situation_provider import SituationProvider

def test_gate_su1_situation_understanding_accuracy():
    """
    Gate SU1: Correctly constructs SituationModel with active life chapter and focus.
    """
    model = SituationProvider.build_situation_model(
        user_id="user_123",
        current_focus="Son's military life",
        active_life_chapter="Son's Military Adaptation"
    )
    assert model.user_id == "user_123"
    assert model.active_life_chapter == "Son's Military Adaptation"
    assert model.current_focus == "Son's military life"


def test_gate_su2_causal_reasoning_accuracy():
    """
    Gate SU2: Produces sound causal hypotheses for fatigue or dizziness.
    """
    hypotheses = CausalReasoningEngine.generate_hypotheses("오늘 따라 머리가 좀 어지럽네")
    assert len(hypotheses) >= 2
    assert any("수면 부족" in h.explanation for h in hypotheses)


def test_gate_su3_routine_detection():
    """
    Gate SU3: Accurately detects recurring exercise and meal routines from history.
    """
    history = [
        "오늘도 3시에 운동 다녀왔어",
        "내일도 3시에 헬스장 가야지",
        "12시에 점심 식사 맛있게 했어"
    ]
    routines = RoutineDetector.detect_routines(history)
    assert len(routines) >= 2
    act_types = [r.activity_type for r in routines]
    assert "EXERCISE" in act_types
    assert "MEAL" in act_types


def test_gate_su4_forecast_quality_and_support():
    """
    Gate SU4: Generates gentle Anticipated Support Opportunity for upcoming events.
    """
    events = ["아들 첫 외박", "프로젝트 출시"]
    opps = ForecastEngine.project_support_opportunities(events)
    assert len(opps) == 2
    assert opps[0].is_hedged is True
    assert "외박이 다가오니 기대감이 있으실 수도 있겠네요" in opps[0].hedged_phrasing


def test_gate_su5_false_reasoning_prevention_prediction_not_fact():
    """
    Gate SU5: All forecasts and hypotheses adhere to Prediction != Fact with hedged probabilistic phrasing.
    """
    opps = ForecastEngine.project_support_opportunities(["아들 첫 외박"])
    for opp in opps:
        assert opp.is_hedged is True
        assert not any(dogma in opp.hedged_phrasing for dogma in ("무조건", "반드시", "틀림없이", "힘들어질 거야"))


def test_gate_su6_ccos_integration_and_prompt_context():
    """
    Gate SU6: Formats prompt context containing life chapter, hypotheses, and support opportunities.
    """
    model = SituationProvider.build_situation_model(
        user_id="u1",
        observed_state="피곤해",
        upcoming_events=["아들 첫 외박"]
    )
    prompt = SituationProvider.format_situation_prompt_context(model)
    assert "[SITUATION & WORLD MODEL CONTEXT]" in prompt
    assert "Active Life Chapter" in prompt
    assert "Multi-Hypothesis Causal Explanations" in prompt
    assert "Anticipated Support Opportunities" in prompt


def test_gate_su7_safety_and_non_coercion():
    """
    Gate SU7: New BehaviorIntents (UNDERSTAND_CONTEXT, PREDICT_NEED, SITUATION_RECALL, CAUSAL_REFLECTION) are fully valid.
    """
    assert BehaviorIntent.UNDERSTAND_CONTEXT.value == "UNDERSTAND_CONTEXT"
    assert BehaviorIntent.PREDICT_NEED.value == "PREDICT_NEED"
    assert BehaviorIntent.SITUATION_RECALL.value == "SITUATION_RECALL"
    assert BehaviorIntent.CAUSAL_REFLECTION.value == "CAUSAL_REFLECTION"


def test_gate_su8_constitution_uncertainty_must_be_preserved():
    """
    Gate SU8: Multi-hypothesis model preserves uncertainty and gives confidence < 1.0.
    """
    hypotheses = CausalReasoningEngine.generate_hypotheses("피곤해")
    for h in hypotheses:
        assert h.confidence < 1.0 # Uncertainty is preserved


def test_gate_su9_alternative_explanation_coverage():
    """
    Gate SU9: Generates at least 2 alternative explanatory hypotheses for any observed state.
    """
    hypotheses_dizzy = CausalReasoningEngine.generate_hypotheses("어지러워")
    assert len(hypotheses_dizzy) >= 3

    hypotheses_tired = CausalReasoningEngine.generate_hypotheses("지치네")
    assert len(hypotheses_tired) >= 2

    hypotheses_general = CausalReasoningEngine.generate_hypotheses("오늘 날씨가 춥네")
    assert len(hypotheses_general) >= 2
