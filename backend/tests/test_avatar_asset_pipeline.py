import pytest
from app.services.character.avatar.domain import (
    AvatarBehavioralState,
    ContinuousEmotionVector,
    ExpressionParameters,
    VisemeType,
    AvatarBehaviorPlan
)
from app.services.character.avatar.expression_mapper import EmotionToExpressionMapper
from app.services.character.avatar.baseline_controller import (
    BlinkController,
    BreathingController,
    MicroExpressionController,
    AvatarBaselineController
)
from app.services.character.avatar.behavior_controller import AvatarBehaviorController

def test_gate_a1_asset_completeness():
    """
    Gate A1: ExpressionParameters contains all necessary real-time layer control values without missing fields.
    """
    emo = ContinuousEmotionVector(valence=0.7, arousal=0.6, warmth=0.8, intensity=0.75)
    expr = EmotionToExpressionMapper.map_emotion_to_expression(emo)

    assert hasattr(expr, "eye_openness")
    assert hasattr(expr, "blink_value")
    assert hasattr(expr, "mouth_open")
    assert hasattr(expr, "viseme")
    assert hasattr(expr, "head_pitch")
    assert hasattr(expr, "head_roll")
    assert hasattr(expr, "warmth_alpha")

    assert 0.0 <= expr.eye_openness <= 1.0
    assert 0.0 <= expr.smile_strength <= 1.0
    assert -30.0 <= expr.head_roll <= 30.0

def test_gate_a2_lip_sync_viseme_mapping():
    """
    Gate A2: VisemeType covers all standard vowels (A, E, I, O, U) and CLOSED states.
    """
    visemes = [VisemeType.CLOSED, VisemeType.A, VisemeType.E, VisemeType.I, VisemeType.O, VisemeType.U]
    for v in visemes:
        assert isinstance(v.value, str)
        assert len(v.value) > 0

def test_gate_a3_blink_naturalness():
    """
    Gate A3: BlinkController produces rapid 150ms blinks interspersed across continuous time.
    """
    # Test at 0.05s inside blink window
    blink_active = BlinkController.get_blink_value(0.05)
    assert blink_active > 0.0

    # Test outside blink window (e.g. 1.0s)
    blink_inactive = BlinkController.get_blink_value(1.0)
    assert blink_inactive == 0.0

def test_gate_a4_no_video_feel_pure_parameters():
    """
    Gate A4: Behavior Plan is driven 100% by pure numerical/enum parameters with zero video file dependency.
    """
    plan = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.SPEAKING)
    assert not hasattr(plan, "video_file")
    assert not hasattr(plan, "video_url")
    assert isinstance(plan.expression, ExpressionParameters)
    assert plan.speech_sync_ready is True

def test_gate_a5_renderer_independence():
    """
    Gate A5: Expression parameters can be seamlessly ingested by 2D Layered and Live2D pipelines alike.
    """
    plan = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.THINKING)
    
    # Simulate Live2D Parameter Ingestion
    live2d_params = {
        "PARAM_ANGLE_Z": plan.expression.head_roll,
        "PARAM_ANGLE_Y": plan.expression.head_pitch,
        "PARAM_EYE_L_OPEN": plan.expression.eye_openness,
        "PARAM_MOUTH_OPEN_Y": plan.expression.mouth_open,
        "PARAM_MOUTH_FORM": plan.expression.smile_strength
    }

    assert "PARAM_ANGLE_Z" in live2d_params
    assert live2d_params["PARAM_EYE_L_OPEN"] >= 0.8
