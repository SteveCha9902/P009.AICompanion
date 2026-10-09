import pytest
from app.services.character.avatar.domain import (
    AvatarBehavioralState,
    BehaviorParameters,
    AvatarBehaviorPlan
)
from app.services.character.avatar.behavior_controller import AvatarBehaviorController

def test_gate_b1_listening_visibility():
    """
    Gate B1: LISTENING state generates high attention, eye contact, listening tilt, and nod.
    """
    plan = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.LISTENING)
    b = plan.behavior_parameters

    assert b.attention_level >= 0.90
    assert b.eye_contact == 1.0
    assert b.head_tilt > 0.0
    assert b.nod_intensity >= 0.5
    assert b.curiosity_level >= 0.8

def test_gate_b2_thinking_visibility():
    """
    Gate B2: THINKING state reflects pensive tilt, reduced eye contact, and thinking intensity.
    """
    plan = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.THINKING)
    b = plan.behavior_parameters

    assert b.thinking_intensity >= 0.8
    assert b.eye_contact <= 0.5
    assert b.head_tilt < 0.0
    assert plan.face_parameters.eye_direction_y < 0.0

def test_gate_b3_pre_expression_visibility():
    """
    Gate B3: PRE_EXPRESSION recovers eye contact and blooms smile prior to speaking.
    """
    plan = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.PRE_EXPRESSION)
    b = plan.behavior_parameters

    assert b.eye_contact >= 0.85
    assert plan.face_parameters.smile_strength >= 0.7
    assert plan.speech_sync_ready is True

def test_gate_b4_natural_settling():
    """
    Gate B4: SETTLING state smoothly returns toward neutral without abrupt resets.
    """
    plan = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.SETTLING)
    b = plan.behavior_parameters

    assert plan.speech_parameters.is_speaking is False
    assert plan.speech_parameters.mouth_open == 0.0
    assert 0.0 <= b.head_tilt <= 1.0
    assert b.eye_contact >= 0.8

def test_gate_b5_behavior_continuity():
    """
    Gate B5: 6-stage lifecycle generates continuous, non-null, bounded BehaviorParameters.
    """
    states = [
        AvatarBehavioralState.IDLE,
        AvatarBehavioralState.LISTENING,
        AvatarBehavioralState.THINKING,
        AvatarBehavioralState.PRE_EXPRESSION,
        AvatarBehavioralState.SPEAKING,
        AvatarBehavioralState.SETTLING
    ]
    for s in states:
        plan = AvatarBehaviorController.evaluate_plan(state=s)
        b = plan.behavior_parameters
        assert isinstance(b, BehaviorParameters)
        assert 0.0 <= b.attention_level <= 1.0
        assert 0.0 <= b.eye_contact <= 1.0
        assert -30.0 <= b.head_tilt <= 30.0
        assert 0.0 <= b.nod_intensity <= 1.0
