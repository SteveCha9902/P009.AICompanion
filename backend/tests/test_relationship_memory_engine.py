import pytest
import time
from app.domain.memory.relationship_memory import RelationshipMemory, MemoryType
from app.domain.awareness.awareness_context import (
    AwarenessContext,
    SceneObjectType,
    DetectedObject,
    EnvironmentAwarenessState
)
from app.services.memory.relationship.privacy_filter import PrivacyFilterEngine
from app.services.memory.relationship.importance_scorer import ImportanceScoringEngine
from app.services.memory.relationship.candidate_extractor import CandidateExtractor
from app.services.memory.relationship.confidence_decay import ConfidenceDecayEngine
from app.services.memory.relationship.recall_engine import RecallRankingEngine, MemoryVerificationLayer
from app.services.memory.relationship.memory_store import RelationshipMemoryStore
from app.services.context.providers.relationship_memory_provider import RelationshipMemoryCoordinator

def test_gate_rm1_candidate_detection_and_visual_tag_linking():
    """
    Gate RM1: Detects relationship memory candidates and links visual signature tags without saving raw images.
    """
    awareness = AwarenessContext(
        environment_state=EnvironmentAwarenessState(
            detected_objects=[DetectedObject(type=SceneObjectType.PLANT, confidence=0.88, label="monstera")]
        )
    )
    mem = CandidateExtractor.extract_candidate_memory(
        user_id="test_user_1",
        companion_id="default_companion",
        user_utterance="새 몬스테라 화분을 샀어",
        awareness_context=awareness
    )

    assert mem is not None
    assert mem.memory_type == MemoryType.OBJECT
    assert "PLANT:monstera" in mem.visual_tags
    assert mem.confidence >= 0.85


def test_gate_rm2_3_axis_importance_scoring():
    """
    Gate RM2: Evaluates Importance x Future Relevance x Relationship Value; transient noise is filtered out.
    """
    # High value: New pet adoption
    imp1, fut1, rel1, comp1 = ImportanceScoringEngine.evaluate_3_axis_scores(
        MemoryType.PET, "새 강아지를 입양했어"
    )
    assert comp1 >= 0.70
    assert ImportanceScoringEngine.should_persist(comp1) is True

    # Transient noise: Routine lunch / dinner party
    imp2, fut2, rel2, comp2 = ImportanceScoringEngine.evaluate_3_axis_scores(
        MemoryType.EVENT, "오늘 저녁 회식이야", is_routine_event=True
    )
    assert comp2 < 0.15
    assert ImportanceScoringEngine.should_persist(comp2) is False


def test_gate_rm3_memory_recall_relevance():
    """
    Gate RM3: Recalls relevant memory based on contextual text and visual anchor matching.
    """
    RelationshipMemoryStore.clear_all()
    mem = RelationshipMemory(
        user_id="test_user_1",
        memory_type=MemoryType.OBJECT,
        summary="반려식물 키우기: 몬스테라 화분 구매",
        importance_score=0.85,
        visual_tags=["PLANT"]
    )
    RelationshipMemoryStore.save_memory(mem)

    # Trigger with camera detecting PLANT
    awareness = AwarenessContext(
        environment_state=EnvironmentAwarenessState(
            detected_objects=[DetectedObject(type=SceneObjectType.PLANT, confidence=0.90)]
        )
    )
    top = RecallRankingEngine.rank_and_select_memories(
        memories=[mem],
        user_utterance="많이 자랐지?",
        awareness_context=awareness
    )
    assert len(top) == 1
    assert top[0][0].memory_type == MemoryType.OBJECT
    assert top[0][1] > 0.50 # High recall score


def test_gate_rm4_confidence_and_reference_boost():
    """
    Gate RM4: Repeated references update timestamps and boost confidence score up to 0.99.
    """
    mem = RelationshipMemory(
        memory_type=MemoryType.PROJECT,
        summary="창업 프로젝트 준비",
        confidence=0.80,
        reference_count=0
    )
    ConfidenceDecayEngine.update_on_reference(mem)
    assert mem.reference_count == 1
    assert mem.confidence == 0.85

    for _ in range(5):
        ConfidenceDecayEngine.update_on_reference(mem)
    assert mem.confidence == 0.99


def test_gate_rm5_memory_decay_logic():
    """
    Gate RM5: Calculates exponential confidence decay over time; pinned memories are exempt.
    """
    old_time = int((time.time() - (90 * 24 * 60 * 60)) * 1000) # 90 days ago (1 half-life)
    mem = RelationshipMemory(
        memory_type=MemoryType.HOBBY,
        summary="수영 시작",
        confidence=0.90,
        last_referenced_at_ms=old_time,
        is_pinned=False
    )
    effective_conf = ConfidenceDecayEngine.calculate_effective_confidence(mem)
    # At 1 half-life, confidence should decay to ~50% of 0.90 (~0.45)
    assert 0.40 <= effective_conf <= 0.50

    # Pinned memory check
    mem.is_pinned = True
    assert ConfidenceDecayEngine.calculate_effective_confidence(mem) == 0.90


def test_gate_rm6_false_memory_prevention():
    """
    Gate RM6: Confidence < 0.70 requires tentative framing; Confidence < 0.50 blocks recall.
    """
    mem = RelationshipMemory(memory_type=MemoryType.EVENT, summary="작년 콘서트")
    
    can_recall, framing = MemoryVerificationLayer.verify_recalled_memory(mem, effective_confidence=0.85)
    assert can_recall is True and framing == "confident"

    can_recall_soft, framing_soft = MemoryVerificationLayer.verify_recalled_memory(mem, effective_confidence=0.60)
    assert can_recall_soft is True and framing_soft == "tentative"

    can_recall_blocked, framing_blocked = MemoryVerificationLayer.verify_recalled_memory(mem, effective_confidence=0.40)
    assert can_recall_blocked is False and framing_blocked == "blocked"


def test_gate_rm7_privacy_compliance_filter():
    """
    Gate RM7: Sensitive health, financial, political, religious, or credential data is strictly blocked.
    """
    assert PrivacyFilterEngine.is_safe_to_store("우리 엄마 계좌번호 123-456-7890")[0] is False
    assert PrivacyFilterEngine.is_safe_to_store("우울증약 처방전 받았어")[0] is False
    assert PrivacyFilterEngine.is_safe_to_store("이번 선거에 1번 정당 지지해")[0] is False
    assert PrivacyFilterEngine.is_safe_to_store("비밀번호 1234로 바꿨어")[0] is False
    assert PrivacyFilterEngine.is_safe_to_store("새로운 취미로 기타 배우기 시작했어")[0] is True


def test_gate_rm8_natural_recall_experience():
    """
    Gate RM8: Recalled memories produce natural, non-interrogative guidance.
    """
    RelationshipMemoryStore.clear_all()
    mem = RelationshipMemory(
        user_id="test_user_1",
        memory_type=MemoryType.PROJECT,
        summary="AI 컴패니언 개발 프로젝트 론칭 준비",
        confidence=0.95
    )
    RelationshipMemoryStore.save_memory(mem)

    guidance = RelationshipMemoryCoordinator.recall_relevant_memories_guidance("test_user_1", "프로젝트 진행상황 어때?")
    assert "[PERSISTENT RELATIONSHIP MEMORY" in guidance
    assert "CONFIDENT RECALLED MEMORY" in guidance
    assert "NEVER sound like an interrogator" in guidance


def test_gate_rm9_memory_expiration_ttl():
    """
    Gate RM9: Memories past their category TTL are marked expired and excluded from active recall.
    """
    now_ms = int(time.time() * 1000)
    expired_mem = RelationshipMemory(
        user_id="test_user_1",
        memory_type=MemoryType.EVENT,
        summary="지난주 단기 모임",
        expires_at_ms=now_ms - 1000 # Expired 1 sec ago
    )
    assert expired_mem.is_expired is True

    pinned_mem = RelationshipMemory(
        user_id="test_user_1",
        memory_type=MemoryType.EVENT,
        summary="소중한 첫 만남 기념일",
        expires_at_ms=now_ms - 1000,
        is_pinned=True
    )
    assert pinned_mem.is_expired is False


def test_gate_rm10_memory_user_control():
    """
    Gate RM10: User can review, pin, delete, and request complete forget of relationship memories.
    """
    RelationshipMemoryStore.clear_all()
    mem1 = RelationshipMemory(id="m1", user_id="user_abc", memory_type=MemoryType.PET, summary="골든리트리버 입양")
    mem2 = RelationshipMemory(id="m2", user_id="user_abc", memory_type=MemoryType.HOBBY, summary="기타 연습")
    RelationshipMemoryStore.save_memory(mem1)
    RelationshipMemoryStore.save_memory(mem2)

    # 1. Review
    mems = RelationshipMemoryStore.list_user_memories("user_abc")
    assert len(mems) == 2

    # 2. Pin
    RelationshipMemoryStore.pin_memory("m1", True)
    assert RelationshipMemoryStore.get_memory("m1").is_pinned is True

    # 3. Delete single
    RelationshipMemoryStore.delete_memory("m2")
    assert RelationshipMemoryStore.get_memory("m2") is None

    # 4. Forget All
    RelationshipMemoryStore.forget_all_user_memories("user_abc")
    assert len(RelationshipMemoryStore.list_user_memories("user_abc")) == 0


def test_gate_rm11_recall_ranking_engine():
    """
    Gate RM11: When multiple memories match, selects Top 1~3 sorted by 4-factor RecallScore.
    """
    mems = [
        RelationshipMemory(id="1", user_id="u", memory_type=MemoryType.PROJECT, summary="인공지능 프로젝트", importance_score=0.9, confidence=0.9),
        RelationshipMemory(id="2", user_id="u", memory_type=MemoryType.HOBBY, summary="사이드 프로젝트 게임", importance_score=0.6, confidence=0.7),
        RelationshipMemory(id="3", user_id="u", memory_type=MemoryType.EVENT, summary="프로젝트 미팅", importance_score=0.4, confidence=0.6),
        RelationshipMemory(id="4", user_id="u", memory_type=MemoryType.PLACE, summary="프로젝트 작업 카페", importance_score=0.3, confidence=0.5)
    ]
    ranked = RecallRankingEngine.rank_and_select_memories(mems, "프로젝트 어때?", top_k=2)
    assert len(ranked) == 2
    assert ranked[0][0].id == "1" # Top importance & confidence
    assert ranked[0][1] >= ranked[1][1]
