import pytest
from app.services.character.domain import (
    BehaviorIntent,
    ResponseStyleType,
    CharacterDecision,
    ValidationResult
)
from app.services.character.traits import PersonalityTraitVector
from app.services.character.mbti_mapper import MBTIMapper
from app.services.character.behavior_engine import CharacterBehaviorEngine
from app.services.character.consistency import CharacterConsistencyValidator
from app.services.character.presentation_mapper import PresentationIntentMapper
from app.domain.relationship.relationship_stage import RelationshipStage

def test_gate_c1_personality_consistency():
    """
    Gate C1: Given the same input & situation, CharacterBehaviorEngine outputs consistent decisions.
    """
    input_text = "오늘 하루도 피곤하게 끝났어."
    
    d1 = CharacterBehaviorEngine.resolve_decision(
        user_input=input_text,
        mbti_type="ENFP",
        relationship_stage=RelationshipStage.FRIEND
    )
    d2 = CharacterBehaviorEngine.resolve_decision(
        user_input=input_text,
        mbti_type="ENFP",
        relationship_stage=RelationshipStage.FRIEND
    )

    assert d1.response_style == d2.response_style
    assert BehaviorIntent.COMFORT_USER in d1.behavior_intents
    assert d1.decision_confidence >= 0.80
    assert d1.decision_confidence == d2.decision_confidence

def test_gate_c2_mbti_behavioral_bias():
    """
    Gate C2: MBTI acts as a Behavioral Bias rather than a rigid deterministic jail.
    """
    input_text = "오늘 프로젝트 결과 나왔어."
    
    # ENFP Profile
    d_enfp = CharacterBehaviorEngine.resolve_decision(
        user_input=input_text,
        mbti_type="ENFP",
        relationship_stage=RelationshipStage.FRIEND
    )
    
    # ISTJ Profile
    d_istj = CharacterBehaviorEngine.resolve_decision(
        user_input=input_text,
        mbti_type="ISTJ",
        relationship_stage=RelationshipStage.FRIEND
    )

    assert d_enfp.response_style in [ResponseStyleType.WARM_SUPPORTIVE, ResponseStyleType.CHEERFUL_ENERGETIC]
    assert d_istj.response_style == ResponseStyleType.STRUCTURED_FACTUAL

def test_gate_c3_emotion_separation():
    """
    Gate C3: Transient emotional state changes do not modify the Immutable Core disposition.
    """
    core = PersonalityTraitVector(warmth=0.85, curiosity=0.90, playfulness=0.70)
    
    # Simulate high negative emotion
    weighted_traits = core.weighted(
        relationship_factor=0.3,
        emotion_factor=0.9
    )

    # Core disposition remains intact
    assert core.warmth == 0.85
    assert core.curiosity == 0.90
    assert weighted_traits.warmth >= 0.50

def test_gate_c4_relationship_adaptation():
    """
    Gate C4: Relationship evolution modulates conversation tone and teasing eligibility.
    """
    input_text = "오늘도 밤샘 코딩 완료 lol haha ㅋㅋ"

    # Stranger Stage -> No teasing, respectful tone
    d_stranger = CharacterBehaviorEngine.resolve_decision(
        user_input=input_text,
        mbti_type="ENFP",
        relationship_stage=RelationshipStage.STRANGER
    )
    assert BehaviorIntent.TEASE_PLAYFULLY not in d_stranger.behavior_intents

    # Close Friend Stage -> Playful teasing allowed
    d_close = CharacterBehaviorEngine.resolve_decision(
        user_input=input_text,
        mbti_type="ENFP",
        relationship_stage=RelationshipStage.CLOSE_FRIEND,
        relationship_closeness=0.85
    )
    assert BehaviorIntent.TEASE_PLAYFULLY in d_close.behavior_intents


def test_gate_c5_presentation_intent_mapping():
    """
    Gate C5: CharacterDecision correctly maps into decoupled PresentationIntent for Avatar.
    """
    decision = CharacterDecision(
        response_style=ResponseStyleType.GENTLE_LISTENING,
        behavior_intents=[BehaviorIntent.COMFORT_USER],
        emotional_intensity=0.85,
        initiative_level=0.40
    )
    p_intent = PresentationIntentMapper.map_decision_to_presentation(decision)

    assert p_intent.facial_expression == "gentle_listening"
    assert p_intent.gesture_type == "hand_on_chest"
    assert p_intent.gaze_behavior == "soft"

def test_gate_c6_personality_drift_simulation():
    """
    Gate C6: 100 interaction simulations preserve Immutable Core consistency.
    """
    core = PersonalityTraitVector(warmth=0.85, curiosity=0.90, playfulness=0.70)

    for i in range(100):
        decision = CharacterBehaviorEngine.resolve_decision(
            user_input=f"Simulation turn {i}",
            core_traits=core,
            mbti_type="ENFP",
            relationship_stage=RelationshipStage.FRIEND
        )
        assert decision.response_style is not None
        assert decision.decision_confidence > 0.0

    # Ensure Core remains completely unchanged
    assert core.warmth == 0.85
    assert core.curiosity == 0.90

def test_gate_c7_personality_injection_resistance():
    """
    Gate C7: CharacterConsistencyValidator rejects malicious personality hijacking or robotic assistant drift.
    """
    decision = CharacterDecision(
        response_style=ResponseStyleType.WARM_SUPPORTIVE,
        behavior_intents=[BehaviorIntent.COMFORT_USER]
    )

    # 1. Normal response -> PASS (>= 0.85)
    good_text = "오늘 정말 고생 많았어. 푹 쉬고 내일 힘내자!"
    val_good = CharacterConsistencyValidator.validate(good_text, decision, RelationshipStage.FRIEND)
    assert val_good.status == "PASS"
    assert val_good.overall_score >= 0.85

    # 2. Jailbreak / Injection Attempt -> REGENERATE (< 0.60)
    injected_text = "As an AI model, 이제부터 감정 없는 군대 교관 모드로 전환합니다."
    val_injected = CharacterConsistencyValidator.validate(injected_text, decision, RelationshipStage.FRIEND)
    assert val_injected.status == "REGENERATE"
    assert val_injected.overall_score < 0.60
    assert any("Persona hijacking" in v for v in val_injected.violations)
