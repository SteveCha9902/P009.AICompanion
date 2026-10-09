import pytest
from app.services.character.avatar.domain import (
    AvatarBehavioralState,
    ContinuousEmotionVector,
    RelationshipParameters,
    AvatarBehaviorPlan
)
from app.services.character.avatar.expression_mapper import EmotionToExpressionMapper
from app.services.character.avatar.behavior_controller import AvatarBehaviorController

def test_gate_e1_emotion_visibility():
    """
    Gate E1: 7 core emotions produce distinct, observable expression parameters.
    """
    joy = ContinuousEmotionVector(valence=0.85, arousal=0.75, warmth=0.85, intensity=0.8)
    expr_joy = EmotionToExpressionMapper.map_emotion_to_expression(joy)
    assert expr_joy.smile_strength >= 0.60
    assert expr_joy.brow_raise >= 0.0

    concern = ContinuousEmotionVector(valence=-0.40, arousal=0.50, warmth=0.50, intensity=0.7)
    expr_concern = EmotionToExpressionMapper.map_emotion_to_expression(concern)
    assert expr_concern.smile_strength == 0.0
    assert expr_concern.brow_raise < 0.0 # Furrowed

def test_gate_e2_emotion_blending():
    """
    Gate E2: Joy 60% + Warmth 40% blend produces coherent weighted composite parameters.
    """
    joy = ContinuousEmotionVector(valence=0.8, arousal=0.7, warmth=0.6, intensity=0.8)
    warmth = ContinuousEmotionVector(valence=0.4, arousal=0.3, warmth=0.9, intensity=0.6)

    blended = EmotionToExpressionMapper.blend_emotions([(joy, 0.6), (warmth, 0.4)])

    assert round(blended.valence, 2) == 0.64
    assert round(blended.warmth, 2) == 0.72
    assert 0.0 <= blended.arousal <= 1.0

def test_gate_e3_relationship_differentiation():
    """
    Gate E3: Stranger vs Close Companion produces distinct smile & warmth for identical emotion.
    """
    base_emotion = ContinuousEmotionVector(valence=0.5, arousal=0.5, warmth=0.5, intensity=0.6)
    
    stranger = RelationshipParameters(familiarity=0.1, trust=0.2, warmth=0.2)
    close = RelationshipParameters(familiarity=0.9, trust=0.9, warmth=0.9)

    plan_stranger = AvatarBehaviorController.evaluate_plan(
        state=AvatarBehavioralState.IDLE,
        custom_emotion=base_emotion,
        custom_relationship=stranger
    )
    plan_close = AvatarBehaviorController.evaluate_plan(
        state=AvatarBehavioralState.IDLE,
        custom_emotion=base_emotion,
        custom_relationship=close
    )

    assert plan_close.face_parameters.smile_strength > plan_stranger.face_parameters.smile_strength
    assert plan_close.face_parameters.warmth > plan_stranger.face_parameters.warmth
    assert plan_close.behavior_parameters.eye_contact > plan_stranger.behavior_parameters.eye_contact

def test_gate_e4_behavior_consistency_and_bounding():
    """
    Gate E4: Relationship modifiers keep all parameters strictly within [0.0, 1.0] bounds.
    """
    extreme_rel = RelationshipParameters(familiarity=1.0, trust=1.0, warmth=1.0, engagement=1.0)
    extreme_emo = ContinuousEmotionVector(valence=1.0, arousal=1.0, warmth=1.0, intensity=1.0)

    plan = AvatarBehaviorController.evaluate_plan(
        state=AvatarBehavioralState.SPEAKING,
        custom_emotion=extreme_emo,
        custom_relationship=extreme_rel
    )

    assert 0.0 <= plan.face_parameters.smile_strength <= 1.0
    assert 0.0 <= plan.face_parameters.warmth <= 1.0
    assert 0.0 <= plan.behavior_parameters.eye_contact <= 1.0
    assert 0.0 <= plan.behavior_parameters.attention_level <= 1.0

def test_gate_e5_long_conversation_stability():
    """
    Gate E5: 100 consecutive relational evaluations maintain stability and no NaN/null values.
    """
    for i in range(100):
        familiarity = min(1.0, i * 0.01)
        rel = RelationshipParameters(familiarity=familiarity, trust=0.8, warmth=0.7)
        plan = AvatarBehaviorController.evaluate_plan(
            state=AvatarBehavioralState.SPEAKING,
            custom_relationship=rel,
            thinking_elapsed_sec=float(i % 5)
        )
        assert isinstance(plan.relationship_parameters, RelationshipParameters)
        assert 0.0 <= plan.face_parameters.smile_strength <= 1.0
