import pytest
import time
from app.domain.memory.relationship_memory import RelationshipMemory, MemoryType
from app.domain.proactive.proactive_context import (
    ProactiveTriggerType,
    ProactiveMode,
    ProactiveDialogueStyle
)
from app.domain.awareness.awareness_context import (
    AwarenessContext,
    UserAwarenessState,
    FacialEmotionType
)
from app.services.memory.relationship.memory_store import RelationshipMemoryStore
from app.services.proactive.user_receptiveness import UserReceptivenessEngine
from app.services.proactive.budget_manager import ProactiveBudgetManager
from app.services.proactive.interest_engine import InterestEngine
from app.services.proactive.diversity_engine import ProactiveDiversityEngine
from app.services.proactive.conversation_starter import ConversationStarterGenerator
from app.services.proactive.opportunity_detector import ProactiveOpportunityDetector

def test_gate_pc1_appropriate_timing_and_dynamic_window():
    """
    Gate PC1: Triggers follow-up only when days elapsed exceed dynamic window (e.g. 15 days for plant).
    """
    now_ms = int(time.time() * 1000)
    # Memory created 3 days ago (not due for 15-day plant window)
    recent_mem = RelationshipMemory(
        user_id="u1",
        memory_type=MemoryType.OBJECT,
        summary="몬스테라 화분 구매",
        last_referenced_at_ms=now_ms - (3 * 24 * 60 * 60 * 1000)
    )
    # Memory created 16 days ago (due for plant window)
    due_mem = RelationshipMemory(
        user_id="u1",
        memory_type=MemoryType.OBJECT,
        summary="몬스테라 화분 구매",
        last_referenced_at_ms=now_ms - (16 * 24 * 60 * 60 * 1000)
    )
    candidates_recent = InterestEngine.get_due_memory_candidates([recent_mem])
    assert len(candidates_recent) == 0

    candidates_due = InterestEngine.get_due_memory_candidates([due_mem])
    assert len(candidates_due) == 1
    assert candidates_due[0][2] >= 15 # >= 15 days passed


def test_gate_pc2_memory_relevance():
    """
    Gate PC2: Proactive starter connects meaningfully to user's saved relationship memories.
    """
    mem = RelationshipMemory(
        user_id="u1",
        memory_type=MemoryType.PET,
        summary="골든리트리버 입양"
    )
    starter = ConversationStarterGenerator.generate_starter(mem, ProactiveDialogueStyle.REMINISCENCE)
    assert "강아지" in starter or "반려동물" in starter
    assert "잘 지내고 있어?" in starter


def test_gate_pc3_non_intrusive_frequency_budget():
    """
    Gate PC3: Enforces 30-minute cooldown in NORMAL mode.
    """
    ProactiveBudgetManager.set_mode(ProactiveMode.NORMAL)
    ProactiveBudgetManager.reset_cooldown()

    assert ProactiveBudgetManager.can_initiate_proactive() is True
    ProactiveBudgetManager.record_proactive_utterance()
    assert ProactiveBudgetManager.can_initiate_proactive() is False


def test_gate_pc4_user_comfort_and_interrogation_prohibition():
    """
    Gate PC4: Proactive templates never sound like nagging or interrogating ('왜 안 했어?').
    """
    mem = RelationshipMemory(
        user_id="u1",
        memory_type=MemoryType.PROJECT,
        summary="AI 앱 개발"
    )
    for style in ProactiveDialogueStyle:
        starter = ConversationStarterGenerator.generate_starter(mem, style)
        assert "왜 안" not in starter
        assert "안 했네" not in starter


def test_gate_pc5_user_opt_out_and_quiet_mode():
    """
    Gate PC5: ProactiveMode.OFF disables proactive speech completely, QUIET mode limits to 6-hour intervals.
    """
    # OFF mode
    ProactiveBudgetManager.set_mode(ProactiveMode.OFF)
    ProactiveBudgetManager.reset_cooldown()
    assert ProactiveBudgetManager.can_initiate_proactive() is False

    # QUIET mode
    ProactiveBudgetManager.set_mode(ProactiveMode.QUIET)
    ProactiveBudgetManager.reset_cooldown()
    assert ProactiveBudgetManager.can_initiate_proactive() is True
    ProactiveBudgetManager.record_proactive_utterance()
    assert ProactiveBudgetManager.can_initiate_proactive() is False


def test_gate_pc6_receptiveness_respect():
    """
    Gate PC6: Does not initiate proactive conversation when user is fatigued or giving terse responses.
    """
    # Case 1: Terse response ("ㅇㅇ") -> Low receptiveness (< 0.60)
    score_terse = UserReceptivenessEngine.evaluate_receptiveness(last_user_message="ㅇㅇ")
    assert score_terse < 0.60
    assert UserReceptivenessEngine.is_user_receptive(score_terse) is False

    # Case 2: Fatigued user -> Low receptiveness
    fatigued_ctx = AwarenessContext(
        user_state=UserAwarenessState(facial_emotion=FacialEmotionType.FATIGUED)
    )
    score_fatigued = UserReceptivenessEngine.evaluate_receptiveness(awareness_context=fatigued_ctx)
    assert score_fatigued < 0.60


def test_gate_pc7_topic_diversity_and_style_cycle():
    """
    Gate PC7: Cycles through 4 dialogue styles and avoids immediate topic repetition.
    """
    ProactiveDiversityEngine.clear_history()

    style1 = ProactiveDiversityEngine.get_next_style()
    style2 = ProactiveDiversityEngine.get_next_style()
    style3 = ProactiveDiversityEngine.get_next_style()
    style4 = ProactiveDiversityEngine.get_next_style()

    assert style1 != style2
    assert {style1, style2, style3, style4} == {
        ProactiveDialogueStyle.REMINISCENCE,
        ProactiveDialogueStyle.GREETING,
        ProactiveDialogueStyle.ENCOURAGEMENT,
        ProactiveDialogueStyle.OBSERVATION
    }

    # Topic history check
    ProactiveDiversityEngine.record_usage("PET", "강아지 안부")
    assert ProactiveDiversityEngine.is_topic_recently_used("PET") is True
    assert ProactiveDiversityEngine.is_topic_recently_used("PROJECT") is False


def test_gate_pc8_priority_selection():
    """
    Gate PC8: Selects single highest priority candidate when multiple topics are simultaneously mature.
    """
    RelationshipMemoryStore.clear_all()
    ProactiveBudgetManager.set_mode(ProactiveMode.NORMAL)
    ProactiveBudgetManager.reset_cooldown()
    ProactiveDiversityEngine.clear_history()

    now_ms = int(time.time() * 1000)
    # Topic 1: Pet (High importance, 6 days ago)
    mem_pet = RelationshipMemory(
        id="pet_1",
        user_id="u_test",
        memory_type=MemoryType.PET,
        summary="골든리트리버 입양",
        importance_score=0.95,
        future_relevance=0.95,
        relationship_value=0.95,
        last_referenced_at_ms=now_ms - (6 * 24 * 60 * 60 * 1000)
    )
    # Topic 2: Object plant (Medium importance, 16 days ago)
    mem_plant = RelationshipMemory(
        id="plant_1",
        user_id="u_test",
        memory_type=MemoryType.OBJECT,
        summary="몬스테라 화분",
        importance_score=0.65,
        future_relevance=0.50,
        relationship_value=0.60,
        last_referenced_at_ms=now_ms - (16 * 24 * 60 * 60 * 1000)
    )
    RelationshipMemoryStore.save_memory(mem_pet)
    RelationshipMemoryStore.save_memory(mem_plant)

    opp = ProactiveOpportunityDetector.detect_best_proactive_opportunity(
        user_id="u_test",
        last_user_message="오늘 날씨 좋다",
        idle_seconds=90.0
    )
    assert opp is not None
    assert opp.memory_id == "pet_1" # Top priority selected
