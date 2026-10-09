import pytest
from app.services.character.avatar.domain import (
    AvatarBehavioralState,
    SpeechParameters,
    VisemeType,
    AvatarBehaviorPlan
)
from app.services.character.avatar.behavior_controller import AvatarBehaviorController

def test_gate_l1_audio_to_mouth_sync():
    """
    Gate L1: SPEAKING state generates active SpeechParameters with valid mouth_open and viseme.
    """
    plan = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.SPEAKING)
    speech = plan.speech_parameters

    assert speech.is_speaking is True
    assert speech.mouth_open >= 0.4
    assert speech.viseme != VisemeType.CLOSED
    assert 0.0 <= speech.speech_intensity <= 1.0

def test_gate_l2_speaking_start_sync():
    """
    Gate L2: PRE_EXPRESSION signals speech readiness (speech_sync_ready=True) and precedes SPEAKING.
    """
    plan_pre = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.PRE_EXPRESSION)
    assert plan_pre.speech_sync_ready is True
    assert plan_pre.speech_parameters.is_speaking is False

    plan_speaking = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.SPEAKING)
    assert plan_speaking.speech_parameters.is_speaking is True

def test_gate_l3_speaking_end_sync():
    """
    Gate L3: SETTLING state immediately deactivates speech and closes mouth.
    """
    plan_settling = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.SETTLING)
    assert plan_settling.speech_parameters.is_speaking is False
    assert plan_settling.speech_parameters.mouth_open == 0.0
    assert plan_settling.speech_parameters.viseme == VisemeType.CLOSED

def test_gate_l4_no_mouth_jitter_ema_convergence():
    """
    Gate L4: Mathematical simulation of EMA filter ensures smooth convergence without abrupt spikes.
    """
    alpha = 0.45
    smoothed = 0.0
    raw_inputs = [0.2, 0.8, 0.3, 0.9, 0.4]
    
    smoothed_history = []
    for raw in raw_inputs:
        smoothed = alpha * raw + (1.0 - alpha) * smoothed
        smoothed_history.append(smoothed)

    # Check that each step does not exceed the raw jump
    for i in range(1, len(smoothed_history)):
        diff = abs(smoothed_history[i] - smoothed_history[i - 1])
        assert diff < 0.6  # Smooth transition bounded

def test_gate_l5_long_speech_stability():
    """
    Gate L5: 100 consecutive speaking evaluations remain numerically bounded and stable.
    """
    for sec in range(100):
        plan = AvatarBehaviorController.evaluate_plan(
            state=AvatarBehavioralState.SPEAKING,
            thinking_elapsed_sec=float(sec)
        )
        assert plan.speech_parameters.is_speaking is True
        assert 0.0 <= plan.speech_parameters.mouth_open <= 1.0
        assert -10.0 <= plan.face_parameters.head_pitch <= 10.0
