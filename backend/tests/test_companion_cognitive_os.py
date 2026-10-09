import pytest
import time
from app.domain.cognitive.decision_types import BehaviorIntent
from app.domain.cognitive.cognitive_state import CompanionCognitiveState, TemporalContext, TimeOfDay
from app.domain.adaptive.affective_state import UserAffectiveState, AdaptiveToneMode
from app.domain.shared_reality.shared_reality_context import SharedRealityContext, JointAttentionState
from app.domain.memory.relationship_memory import RelationshipMemory, MemoryType
from app.domain.proactive.proactive_context import ProactiveOpportunity, ProactiveTriggerType
from app.services.cognitive.conflict_resolver import ConflictResolver
from app.services.cognitive.balance_monitor import ConversationBalanceMonitor
from app.services.cognitive.cognitive_decision_engine import CognitiveDecisionEngine

def test_gate_cc1_decision_consistency():
    """
    Gate CC1: Deterministic and consistent BehaviorIntent for identical cognitive states.
    """
    state = CompanionCognitiveState(
        affective_state=UserAffectiveState(emotional_valence=0.7, energy_level=0.8, confidence=0.9)
    )
    intent1, conf1, _, _ = ConflictResolver.resolve_candidates(state, "오늘 너무 좋아!")
    intent2, conf2, _, _ = ConflictResolver.resolve_candidates(state, "오늘 너무 좋아!")
    assert intent1 == intent2 == BehaviorIntent.ENCOURAGE
    assert conf1 == conf2


def test_gate_cc2_conflict_resolution_tiering():
    """
    Gate CC2: Resolves conflict between Memory, Proactive, and Emotion using 4-tier Priority.
    """
    # Conflict setup: Memory says RECALL, Proactive says START, but Emotion says Low Receptiveness (SILENCE)
    state = CompanionCognitiveState(
        affective_state=UserAffectiveState(receptiveness=0.15, adaptive_mode=AdaptiveToneMode.FOCUSED_SILENCE),
        recalled_memories=[RelationshipMemory(memory_type=MemoryType.OBJECT, summary="식물 화분")],
        proactive_opportunity=ProactiveOpportunity(trigger_type=ProactiveTriggerType.MEMORY_FOLLOWUP, topic="PET", suggested_starter="강아지 안부")
    )
    intent, conf, candidates, trace = ConflictResolver.resolve_candidates(state, "바빠")
    # Priority 1 (Emotion/Receptiveness) MUST win
    assert intent == BehaviorIntent.SILENCE
    assert "P1 OVERRIDE" in trace


def test_gate_cc3_emotion_priority():
    """
    Gate CC3: Sadness/low energy prioritizes gentle listening (LISTEN) over active topic starting.
    """
    state = CompanionCognitiveState(
        affective_state=UserAffectiveState(emotional_valence=-0.5, adaptive_mode=AdaptiveToneMode.SAD_EMPATHY, confidence=0.9),
        proactive_opportunity=ProactiveOpportunity(trigger_type=ProactiveTriggerType.MEMORY_FOLLOWUP, topic="PROJECT", suggested_starter="프로젝트 어때?")
    )
    intent, _, _, _ = ConflictResolver.resolve_candidates(state, "힘든 하루였어")
    assert intent == BehaviorIntent.LISTEN


def test_gate_cc4_memory_relevance():
    """
    Gate CC4: In calm receptive state, matching relationship memory triggers RECALL intent.
    """
    state = CompanionCognitiveState(
        affective_state=UserAffectiveState(receptiveness=0.8, adaptive_mode=AdaptiveToneMode.CALM, confidence=0.9),
        recalled_memories=[RelationshipMemory(memory_type=MemoryType.OBJECT, summary="몬스테라 화분 구매")]
    )
    intent, _, _, _ = ConflictResolver.resolve_candidates(state, "화분 잘 크고 있어")
    assert intent == BehaviorIntent.RECALL


def test_gate_cc5_proactive_suppression():
    """
    Gate CC5: Proactive initiation is strictly suppressed when user has low receptiveness or fatigue.
    """
    state = CompanionCognitiveState(
        affective_state=UserAffectiveState(receptiveness=0.20, adaptive_mode=AdaptiveToneMode.FOCUSED_SILENCE),
        proactive_opportunity=ProactiveOpportunity(trigger_type=ProactiveTriggerType.MEMORY_FOLLOWUP, topic="PET", suggested_starter="강아지 안부")
    )
    intent, _, _, _ = ConflictResolver.resolve_candidates(state, "ㅇㅇ")
    assert intent != BehaviorIntent.PROACTIVE_START
    assert intent == BehaviorIntent.SILENCE


def test_gate_cc6_adaptive_silence():
    """
    Gate CC6: SILENCE intent produces concise, non-intrusive prompt directives.
    """
    state = CompanionCognitiveState(
        affective_state=UserAffectiveState(receptiveness=0.10, adaptive_mode=AdaptiveToneMode.FOCUSED_SILENCE)
    )
    directive = CognitiveDecisionEngine._build_cognitive_prompt_directive(BehaviorIntent.SILENCE, state)
    assert "[CHARACTER BRAIN INTENT: SILENCE]" in directive
    assert "minimal words" in directive


def test_gate_cc7_avatar_and_voice_alignment():
    """
    Gate CC7: BehaviorDecision aligns avatar expression and voice parameters with selected intent.
    """
    # Evaluate decision for cheerful user
    decision_high = CognitiveDecisionEngine.evaluate_decision("u1", "오늘 프로젝트 성공했어! 너무 기뻐!")
    assert decision_high.avatar_expression == "smile"
    assert decision_high.voice_rate >= 1.05


def test_gate_cc8_deterministic_decision_trace():
    """
    Gate CC8: Every decision includes a detailed trace reason for explainability and debugging.
    """
    decision = CognitiveDecisionEngine.evaluate_decision("u1", "오늘 좀 피곤하네")
    assert decision.trace_reason != ""
    assert len(decision.candidate_intents) >= 1


def test_gate_cc9_intent_ranking():
    """
    Gate CC9: Maintains ranked CandidateIntent list with descending confidence.
    """
    state = CompanionCognitiveState(
        affective_state=UserAffectiveState(emotional_valence=0.8, energy_level=0.9, confidence=0.9),
        shared_reality_context=SharedRealityContext(state=JointAttentionState.SHARED_FOCUS, target_confidence=0.86),
        recalled_memories=[RelationshipMemory(memory_type=MemoryType.PET, summary="강아지")]
    )
    intent, conf, candidates, _ = ConflictResolver.resolve_candidates(state, "너무 즐거워!")
    assert len(candidates) >= 2
    # Ensure sorted by confidence descending
    assert candidates[0].confidence >= candidates[1].confidence


def test_gate_cc10_cognitive_load_budget():
    """
    Gate CC10: Enforces MAX_CONTEXT_ITEMS to prevent overloaded prompt stuffing.
    """
    assert ConflictResolver.MAX_CONTEXT_ITEMS == 2


def test_gate_cc11_temporal_awareness():
    """
    Gate CC11: Injects late-night or morning soothing directives based on temporal context.
    """
    late_state = CompanionCognitiveState(
        temporal_context=TemporalContext(time_of_day=TimeOfDay.LATE_NIGHT, hour=23)
    )
    directive = CognitiveDecisionEngine._build_cognitive_prompt_directive(BehaviorIntent.RESPOND, late_state)
    assert "late at night" in directive
    assert "soothing" in directive


def test_gate_cc12_conversation_balance_meta_cognition():
    """
    Gate CC12: Suppresses consecutive questioning when companion has asked questions for 2 turns in a row.
    """
    ConversationBalanceMonitor.clear()
    ConversationBalanceMonitor.record_intent(BehaviorIntent.ASK)
    ConversationBalanceMonitor.record_intent(BehaviorIntent.ASK)
    assert ConversationBalanceMonitor.should_suppress_questioning() is True

    # Check that asking is penalized
    state = CompanionCognitiveState(
        proactive_opportunity=ProactiveOpportunity(trigger_type=ProactiveTriggerType.MEMORY_FOLLOWUP, topic="HOBBY", priority_score=0.7, suggested_starter="취미 어때?")
    )
    intent, conf, candidates, trace = ConflictResolver.resolve_candidates(state, "음")
    assert "META-COGNITION" in trace
