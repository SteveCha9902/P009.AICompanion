import pytest
from app.services.character.avatar.domain import (
    AvatarBehavioralState,
    ContinuousEmotionVector,
    ExpressionParameters,
    AvatarGesture,
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
from app.services.character.domain import CharacterDecision, BehaviorIntent, ResponseStyleType

def test_gate_v1_state_transition_continuity():
    """
    Gate V1: All 6 behavioral states transition cleanly with valid duration parameters.
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
        assert plan.transition_duration_ms > 0
        assert 0.0 <= plan.attention_level <= 1.0

def test_gate_v2_pre_expression_timing():
    """
    Gate V2: PRE_EXPRESSION state sets speech_sync_ready to True and blooms expression 200ms ahead.
    """
    plan = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.PRE_EXPRESSION)
    assert plan.speech_sync_ready is True
    assert plan.transition_duration_ms == 200

def test_gate_v3_continuous_emotion_vector():
    """
    Gate V3: ContinuousEmotionVector accurately produces subtle gradients in smile and eye softness.
    """
    # Subtle warm smile
    emo_subtle = ContinuousEmotionVector(valence=0.4, warmth=0.8, intensity=0.5)
    expr_subtle = EmotionToExpressionMapper.map_emotion_to_expression(emo_subtle)

    # Vivid joyful laugh
    emo_vivid = ContinuousEmotionVector(valence=0.9, warmth=0.9, intensity=0.9)
    expr_vivid = EmotionToExpressionMapper.map_emotion_to_expression(emo_vivid)

    assert expr_subtle.smile_strength < expr_vivid.smile_strength
    assert expr_subtle.eye_softness > 0.6
    assert expr_vivid.smile_strength >= 0.70

def test_gate_v4_gesture_decoupling():
    """
    Gate V4: Gestures are decoupled from emotion and can be independently composed.
    """
    custom_gestures = [
        AvatarGesture(gesture_type="THINKING_TILT", intensity=0.8),
        AvatarGesture(gesture_type="SUBTLE_NOD", intensity=0.5)
    ]
    plan = AvatarBehaviorController.evaluate_plan(
        state=AvatarBehavioralState.SPEAKING,
        active_gestures=custom_gestures
    )
    assert len(plan.active_gestures) >= 2
    assert any(g.gesture_type == "THINKING_TILT" for g in plan.active_gestures)
    assert any(g.gesture_type == "SUBTLE_NOD" for g in plan.active_gestures)

def test_gate_v5_attention_and_listening():
    """
    Gate V5: LISTENING state triggers high attention and subtle listening nod.
    """
    plan = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.LISTENING)
    assert plan.attention_level >= 0.90
    assert any(g.gesture_type == "SUBTLE_NOD" for g in plan.active_gestures)
    assert plan.expression.brow_raise == 0.2

def test_gate_v6_blink_and_breathing_baseline():
    """
    Gate V6: AvatarBaselineController produces continuous eye blink and breathing signals.
    """
    base_0 = AvatarBaselineController.get_baseline_parameters(timestamp=0.0)
    base_1 = AvatarBaselineController.get_baseline_parameters(timestamp=1.25)

    assert "eye_blink" in base_0
    assert "breathing_scale" in base_0
    assert 0.95 <= base_0["breathing_scale"] <= 1.05
    assert 0.95 <= base_1["breathing_scale"] <= 1.05

def test_gate_v7_renderer_swappability():
    """
    Gate V7: AvatarBehaviorPlan provides clean ExpressionParameters suitable for any 2D/3D renderer.
    """
    plan = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.SPEAKING)
    assert isinstance(plan.expression, ExpressionParameters)
    assert hasattr(plan.expression, "smile_strength")
    assert hasattr(plan.expression, "eye_softness")
    assert hasattr(plan.expression, "head_pitch")
    assert hasattr(plan.expression, "head_roll")

def test_gate_v8_emotion_mapping_stability():
    """
    Gate V8: Given identical EmotionVector input, EmotionToExpressionMapper produces deterministic output.
    """
    emo = ContinuousEmotionVector(valence=0.75, arousal=0.6, warmth=0.8, intensity=0.7)
    first_expr = None
    for _ in range(50):
        expr = EmotionToExpressionMapper.map_emotion_to_expression(emo)
        if first_expr is None:
            first_expr = expr
        else:
            assert expr.smile_strength == first_expr.smile_strength
            assert expr.eye_softness == first_expr.eye_softness
            assert expr.head_roll == first_expr.head_roll

def test_gate_v9_long_thinking_synchronization():
    """
    Gate V9: THINKING state dynamically scales head pose across 1s, 3s, 5s LLM latency intervals.
    """
    plan_1s = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.THINKING, thinking_elapsed_sec=1.0)
    plan_3s = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.THINKING, thinking_elapsed_sec=3.0)
    plan_5s = AvatarBehaviorController.evaluate_plan(state=AvatarBehavioralState.THINKING, thinking_elapsed_sec=5.0)

    assert plan_1s.expression.head_roll < plan_3s.expression.head_roll
    assert plan_3s.expression.head_roll <= plan_5s.expression.head_roll
    assert any(g.gesture_type == "THINKING_TILT" for g in plan_5s.active_gestures)

def test_gate_v10_multi_gesture_composition():
    """
    Gate V10: Multiple simultaneous gesture overlays blend without collisions.
    """
    gestures_stack = [
        AvatarGesture(gesture_type="THINKING_TILT", intensity=0.7, blend_weight=0.6),
        AvatarGesture(gesture_type="SUBTLE_NOD", intensity=0.4, blend_weight=0.4)
    ]
    plan = AvatarBehaviorController.evaluate_plan(
        state=AvatarBehavioralState.THINKING,
        active_gestures=gestures_stack
    )
    assert len(plan.active_gestures) == 2
    total_weight = sum(g.blend_weight for g in plan.active_gestures)
    assert round(total_weight, 2) == 1.0
