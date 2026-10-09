import pytest
from app.services.character.avatar.domain import (
    AvatarBehavioralState,
    ContinuousEmotionVector,
    FaceParameters,
    AvatarBehaviorPlan
)
from app.services.character.avatar.behavior_controller import AvatarBehaviorController
from app.services.character.avatar.baseline_controller import BlinkController

def test_gate_f1_blink_controller():
    """
    Gate F1: BlinkController properly pulses within valid intervals.
    """
    blink_on = BlinkController.get_blink_value(0.08)
    blink_off = BlinkController.get_blink_value(1.5)

    assert blink_on > 0.0
    assert blink_off == 0.0

def test_gate_f2_eye_direction_gaze():
    """
    Gate F2: Thinking state naturally lowers eye direction Y to simulate looking down/aside.
    """
    plan = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.THINKING)
    assert plan.face_parameters.eye_direction_y < 0.0
    assert -1.0 <= plan.face_parameters.eye_direction_x <= 1.0

def test_gate_f3_smile_interpolation():
    """
    Gate F3: PRE_EXPRESSION blooms smile_strength prior to speech output.
    """
    plan_idle = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.IDLE)
    plan_pre = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.PRE_EXPRESSION)

    assert plan_pre.face_parameters.smile_strength > plan_idle.face_parameters.smile_strength
    assert plan_pre.face_parameters.smile_strength >= 0.70

def test_gate_f4_mouth_open_control():
    """
    Gate F4: SPEAKING state elevates mouth_open while IDLE and THINKING remain closed.
    """
    plan_speaking = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.SPEAKING)
    plan_thinking = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.THINKING)

    assert plan_speaking.face_parameters.mouth_open > 0.3
    assert plan_thinking.face_parameters.mouth_open == 0.0

def test_gate_f5_renderer_independence():
    """
    Gate F5: FaceParameters is completely decoupled from emotion models and ready for any 2D/3D renderer.
    """
    plan = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.LISTENING)
    face = plan.face_parameters

    assert isinstance(face, FaceParameters)
    assert hasattr(face, "eye_openness")
    assert hasattr(face, "brow_raise")
    assert hasattr(face, "head_roll")
    assert hasattr(face, "head_pitch")
    assert face.eye_openness >= 0.95
    assert face.brow_raise > 0.2
