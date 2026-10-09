import pytest
from app.services.character.avatar.domain import (
    AvatarBehavioralState,
    ContinuousEmotionVector,
    RelationshipParameters,
    AvatarMotion,
    MotionParameters,
    AvatarBehaviorPlan
)
from app.services.character.avatar.motion_library import MotionLibrary
from app.services.character.avatar.variety_engine import MotionVarietyEngine
from app.services.character.avatar.behavior_controller import AvatarBehaviorController
from app.services.character.domain import CharacterDecision, BehaviorIntent, ResponseStyleType

def test_gate_m1_motion_variety_catalog():
    """
    Gate M1: Motion Library contains all 14 distinct physical motion presets.
    """
    assert len(MotionLibrary.MOTIONS) == 14
    listening_motions = MotionLibrary.get_motions_by_category("listening")
    assert len(listening_motions) == 4
    thinking_motions = MotionLibrary.get_motions_by_category("thinking")
    assert len(thinking_motions) == 4
    speaking_motions = MotionLibrary.get_motions_by_category("speaking")
    assert len(speaking_motions) == 3
    empathy_motions = MotionLibrary.get_motions_by_category("empathy")
    assert len(empathy_motions) == 3

def test_gate_m2_no_obvious_repetition_cooldown():
    """
    Gate M2: Variety Engine does not emit the identical motion 3 consecutive times.
    """
    MotionVarietyEngine.reset_history()
    emitted = []
    for _ in range(10):
        m = MotionVarietyEngine.select_motion(state=AvatarBehavioralState.LISTENING)
        emitted.append(m.motion_id)

    # Check for no 3 identical consecutive motions
    for i in range(2, len(emitted)):
        assert not (emitted[i] == emitted[i - 1] == emitted[i - 2])

def test_gate_m3_context_appropriateness():
    """
    Gate M3: Comforting intention selects empathy category motions.
    """
    decision = CharacterDecision(
        behavior_intents=[BehaviorIntent.COMFORT_USER],
        response_style=ResponseStyleType.WARM_SUPPORTIVE,
        topic_focus="consoling"
    )
    motion = MotionVarietyEngine.select_motion(
        state=AvatarBehavioralState.SPEAKING,
        decision=decision
    )
    assert motion.category == "empathy"

def test_gate_m4_randomization_jitter():
    """
    Gate M4: Motion parameters include +-10% stochastic jitter factor.
    """
    base_motion = MotionLibrary.MOTIONS["LISTENING_DEEP_NOD"]
    params = MotionVarietyEngine.generate_motion_parameters(base_motion, jitter_enabled=True)

    assert 0.90 <= params.jitter_factor <= 1.10
    assert isinstance(params, MotionParameters)
    assert params.active_motion_id == "LISTENING_DEEP_NOD"

def test_gate_m5_30_minute_stability():
    """
    Gate M5: 100 consecutive plan evaluations generate valid selected_motion and bounded parameters.
    """
    for i in range(100):
        plan = AvatarBehaviorController.evaluate_plan(
            state=AvatarBehavioralState.LISTENING if i % 2 == 0 else AvatarBehavioralState.SPEAKING
        )
        assert plan.selected_motion is not None
        assert isinstance(plan.motion_parameters, MotionParameters)
        assert -30.0 <= plan.face_parameters.head_pitch <= 30.0
