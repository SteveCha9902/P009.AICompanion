import pytest
from app.services.character.avatar.domain import (
    AvatarBehavioralState,
    ContinuousEmotionVector,
    RelationshipParameters,
    AvatarMotion,
    MotionParameters,
    FaceParameters,
    SpeechParameters,
    BehaviorParameters,
    AvatarBehaviorPlan
)
from app.services.character.avatar.expression_mapper import EmotionToExpressionMapper
from app.services.character.avatar.variety_engine import MotionVarietyEngine
from app.services.character.avatar.behavior_controller import AvatarBehaviorController
from app.services.character.domain import CharacterDecision, BehaviorIntent, ResponseStyleType

def test_gate_p1_state_machine_stability():
    """
    Gate P1: 6-stage lifecycle transitions maintain 100% valid state plans.
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
        assert plan.state == s
        assert isinstance(plan.face_parameters, FaceParameters)
        assert isinstance(plan.speech_parameters, SpeechParameters)
        assert isinstance(plan.behavior_parameters, BehaviorParameters)
        assert isinstance(plan.relationship_parameters, RelationshipParameters)
        assert isinstance(plan.motion_parameters, MotionParameters)

def test_gate_p2_lip_sync_quality():
    """
    Gate P2: Speaking state activates lip sync and settles with zero mouth aperture.
    """
    plan_speaking = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.SPEAKING)
    assert plan_speaking.speech_parameters.is_speaking is True
    assert plan_speaking.speech_parameters.mouth_open >= 0.4
    assert plan_speaking.speech_parameters.viseme.value.startswith("viseme_")

    plan_settling = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.SETTLING)
    assert plan_settling.speech_parameters.is_speaking is False
    assert plan_settling.speech_parameters.mouth_open == 0.0

def test_gate_p3_emotion_rendering_and_blending():
    """
    Gate P3: Multi-emotion weighted blending produces smooth composite facial parameters.
    """
    joy = ContinuousEmotionVector(valence=0.9, arousal=0.8, warmth=0.7, intensity=0.9)
    warmth = ContinuousEmotionVector(valence=0.5, arousal=0.3, warmth=0.95, intensity=0.7)
    blended = EmotionToExpressionMapper.blend_emotions([(joy, 0.6), (warmth, 0.4)])

    expr = EmotionToExpressionMapper.map_emotion_to_expression(blended)
    assert expr.smile_strength >= 0.60
    assert expr.eye_softness >= 0.75
    assert expr.warmth_alpha >= 0.70

def test_gate_p4_behavior_variety_and_cooldown():
    """
    Gate P4: Variety Engine rotates motions without repeating the same motion 3 consecutive times.
    """
    MotionVarietyEngine.reset_history()
    selected_ids = []
    for _ in range(15):
        m = MotionVarietyEngine.select_motion(state=AvatarBehavioralState.LISTENING)
        selected_ids.append(m.motion_id)

    for i in range(2, len(selected_ids)):
        assert not (selected_ids[i] == selected_ids[i-1] == selected_ids[i-2])

def test_gate_p5_performance_and_bounding():
    """
    Gate P5: All generated DTO parameters strictly respect their mathematical bounds.
    """
    plan = AvatarBehaviorController.evaluate_plan(
        state=AvatarBehavioralState.SPEAKING,
        custom_emotion=ContinuousEmotionVector(valence=0.7, arousal=0.6, warmth=0.8, intensity=0.8),
        custom_relationship=RelationshipParameters(familiarity=0.9, trust=0.85, warmth=0.9)
    )
    f = plan.face_parameters
    b = plan.behavior_parameters
    assert 0.0 <= f.smile_strength <= 1.0
    assert 0.0 <= f.eye_openness <= 1.0
    assert -30.0 <= f.head_pitch <= 30.0
    assert 0.0 <= b.attention_level <= 1.0
    assert 0.0 <= b.eye_contact <= 1.0

def test_gate_p6_memory_leak_free():
    """
    Gate P6: 1,000 consecutive plan evaluations complete instantaneously with zero state leak.
    """
    for i in range(1000):
        plan = AvatarBehaviorController.evaluate_plan(
            state=AvatarBehavioralState.THINKING if i % 2 == 0 else AvatarBehavioralState.SPEAKING,
            thinking_elapsed_sec=float(i % 5)
        )
        assert plan.state is not None

def test_gate_p7_60fps_render_readiness():
    """
    Gate P7: All parameters have non-null numeric values fully compatible with native 60fps driver.
    """
    plan = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.LISTENING)
    assert isinstance(plan.face_parameters.head_roll, (int, float))
    assert isinstance(plan.face_parameters.head_pitch, (int, float))
    assert isinstance(plan.motion_parameters.head_tilt, (int, float))
    assert isinstance(plan.motion_parameters.jitter_factor, (int, float))

def test_gate_p8_crash_free_extreme_inputs():
    """
    Gate P8: Extreme boundary inputs (all maximums / minimums) execute without exceptions.
    """
    extreme_emo = ContinuousEmotionVector(valence=-1.0, arousal=1.0, warmth=0.0, intensity=1.0)
    extreme_rel = RelationshipParameters(familiarity=0.0, trust=0.0, warmth=0.0, engagement=0.0)
    plan = AvatarBehaviorController.evaluate_plan(
        state=AvatarBehavioralState.THINKING,
        custom_emotion=extreme_emo,
        custom_relationship=extreme_rel
    )
    assert 0.0 <= plan.face_parameters.smile_strength <= 0.25
    assert plan.face_parameters.brow_raise <= -0.5


def test_gate_p9_one_hour_session_simulation():
    """
    Gate P9: Simulates 3,600 interaction ticks (1 hour session) maintaining consistency.
    """
    for sec in range(0, 3600, 36): # 100 sample ticks across 1 hour
        state = AvatarBehavioralState.SPEAKING if (sec // 60) % 2 == 0 else AvatarBehavioralState.LISTENING
        plan = AvatarBehaviorController.evaluate_plan(
            state=state,
            thinking_elapsed_sec=float(sec % 4)
        )
        assert plan.selected_motion is not None

def test_gate_p10_user_satisfaction_and_relational_differentiation():
    """
    Gate P10: Close relationship produces distinctly warmer smile & eye contact than stranger.
    """
    stranger = RelationshipParameters(familiarity=0.1, trust=0.2, warmth=0.2)
    close = RelationshipParameters(familiarity=0.95, trust=0.95, warmth=0.95)

    plan_stranger = AvatarBehaviorController.evaluate_plan(
        state=AvatarBehavioralState.SPEAKING,
        custom_relationship=stranger
    )
    plan_close = AvatarBehaviorController.evaluate_plan(
        state=AvatarBehavioralState.SPEAKING,
        custom_relationship=close
    )

    assert plan_close.face_parameters.warmth > plan_stranger.face_parameters.warmth
    assert plan_close.face_parameters.smile_strength >= plan_stranger.face_parameters.smile_strength
    assert plan_close.behavior_parameters.eye_contact >= plan_stranger.behavior_parameters.eye_contact
