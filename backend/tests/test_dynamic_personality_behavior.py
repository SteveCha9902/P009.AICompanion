import time
import pytest
from app.services.personality.models.personality_state import (
    PersonalityState,
    CoreTraits,
    CommunicationStyleState,
    AttachmentStyleState
)
from app.services.personality.engines.behavior_engine import PersonalityBehaviorEngine
from app.services.personality.evaluators.consistency_evaluator import PersonalityConsistencyEvaluator
from app.domain.relationship.relationship_stage import RelationshipStage

def test_gate_p1_personality_differentiation():
    """
    Gate P1: Given identical user input, different personality profiles produce distinctly different BehaviorDirectives.
    """
    user_input = "오늘 너무 피곤해."

    # Profile A: Warm Empathic Companion
    profile_warm = PersonalityState(
        core_traits=CoreTraits(warmth=0.95, playfulness=0.20, empathy=0.95),
        communication_style=CommunicationStyleState(humor=0.10, emotional_expression=0.90)
    )
    directive_warm = PersonalityBehaviorEngine.resolve_behavior(
        personality=profile_warm,
        relationship_stage=RelationshipStage.CLOSE_FRIEND,
        user_input=user_input
    )

    # Profile B: Playful Teasing Companion (in non-serious mode)
    profile_playful = PersonalityState(
        core_traits=CoreTraits(warmth=0.60, playfulness=0.95, empathy=0.50),
        communication_style=CommunicationStyleState(humor=0.90, emotional_expression=0.70)
    )
    directive_playful = PersonalityBehaviorEngine.resolve_behavior(
        personality=profile_playful,
        relationship_stage=RelationshipStage.CLOSE_FRIEND,
        user_input="오늘도 코딩하다가 밤샜어 ㅋㅋ"
    )

    # Verify behavioral differentiation
    assert directive_warm.response_style.warmth >= 0.90
    assert directive_warm.interaction_behavior.show_concern is True
    assert directive_warm.interaction_behavior.tease_user is False

    assert directive_playful.response_style.playfulness >= 0.70
    assert directive_playful.interaction_behavior.tease_user is True

def test_gate_p2_relationship_evolution():
    """
    Gate P2: As relationship evolves (STRANGER -> FRIEND -> TRUSTED_COMPANION),
    formality decreases while intimacy and initiative increase.
    """
    profile = PersonalityState()

    dir_stranger = PersonalityBehaviorEngine.resolve_behavior(
        personality=profile,
        relationship_stage=RelationshipStage.STRANGER,
        user_input="안녕하세요"
    )

    dir_friend = PersonalityBehaviorEngine.resolve_behavior(
        personality=profile,
        relationship_stage=RelationshipStage.FRIEND,
        user_input="안녕"
    )

    dir_companion = PersonalityBehaviorEngine.resolve_behavior(
        personality=profile,
        relationship_stage=RelationshipStage.TRUSTED_COMPANION,
        user_input="지니야"
    )

    # Formality decreases / Intimacy increases
    assert dir_stranger.interaction_behavior.tease_user is False
    assert dir_friend.interaction_behavior.initiate_topic is True
    assert dir_companion.response_style.warmth >= dir_stranger.response_style.warmth

def test_gate_p3_consistency_and_drift_guard():
    """
    Gate P3: Consistency evaluator accepts compliant responses and flags robotic assistant drift in close relationships.
    """
    profile = PersonalityState()
    directive = PersonalityBehaviorEngine.resolve_behavior(
        personality=profile,
        relationship_stage=RelationshipStage.CLOSE_FRIEND,
        user_input="오늘 너무 힘들었어"
    )

    # 1. Warm Natural Response -> ACCEPT (>= 0.70)
    good_res = "오늘 정말 고생 많았어. 푹 쉬고 내일 다시 이야기하자."
    eval_good = PersonalityConsistencyEvaluator.evaluate_response(good_res, directive, RelationshipStage.CLOSE_FRIEND)
    assert eval_good.score >= 0.70
    assert eval_good.decision == "ACCEPT"

    # 2. Robotic Assistant Drift -> REWRITE / WARNING (< 0.70)
    robotic_res = "귀하의 문의에 감사드립니다. as an ai model, 휴식을 권장합니다."
    eval_robotic = PersonalityConsistencyEvaluator.evaluate_response(robotic_res, directive, RelationshipStage.CLOSE_FRIEND)
    assert eval_robotic.score < 0.70
    assert any("robotic" in f.lower() for f in eval_robotic.feedback)

def test_gate_p4_explainability():
    """
    Gate P4: BehaviorEngine provides explicit explainability reasons for its decisions.
    """
    directive = PersonalityBehaviorEngine.resolve_behavior(
        user_input="오늘 프로젝트 첫 배포 성공했어!",
        relationship_stage=RelationshipStage.FRIEND
    )

    assert any("celebration" in r.lower() for r in directive.reasons)
    assert any("relationship_friend" in r.lower() for r in directive.reasons)
    assert any("engine_latency" in r.lower() for r in directive.reasons)

def test_gate_p5_performance_under_10ms():
    """
    Gate P5: PersonalityBehaviorEngine executes well under 10ms (typical sub-millisecond execution).
    """
    profile = PersonalityState()
    
    t0 = time.perf_counter()
    for _ in range(100):
        PersonalityBehaviorEngine.resolve_behavior(
            personality=profile,
            relationship_stage=RelationshipStage.CLOSE_FRIEND,
            user_input="오늘 하루도 수고했어"
        )
    total_time_ms = (time.perf_counter() - t0) * 1000.0
    avg_time_ms = total_time_ms / 100.0

    assert avg_time_ms < 10.0, f"Average execution time ({avg_time_ms:.3f}ms) exceeded 10ms target"
