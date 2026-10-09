import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

from app.services.reflection.domain.reflection import ReflectionTrigger, ReflectionPriority, ReflectionStatus
from app.services.reflection.domain.reflection_result import (
    ReflectionResult,
    EmotionalPatternDTO,
    RelationshipInsightDTO,
    MemoryCandidateDTO
)
from app.services.reflection.policy.reflection_policy import ReflectionPolicy
from app.services.reflection.engine.reflection_engine import ReflectionEngine
from app.services.reflection.validation.reflection_validator import ReflectionValidator
from app.services.reflection.memory.consolidation_engine import MemoryConsolidationEngine
from app.services.reflection.runtime.rate_limiter import ReflectionRateLimiter
from app.services.reflection.reflection_service import ReflectionService

def test_gate_r1_trigger_accuracy():
    """
    Gate R1: ReflectionPolicy correctly triggers on high emotion/memory and skips routine chat.
    """
    # 1. Low importance routine turn -> Should NOT reflect
    dec_routine = ReflectionPolicy.evaluate(
        emotion_intensity=0.2,
        memory_importance=0.3,
        relationship_delta=0.005,
        conversation_message_count=1
    )
    assert dec_routine.should_reflect is False

    # 2. Significant Emotion (>= 0.75) -> Should reflect
    dec_emotion = ReflectionPolicy.evaluate(emotion_intensity=0.85)
    assert dec_emotion.should_reflect is True
    assert dec_emotion.trigger == ReflectionTrigger.SIGNIFICANT_EMOTION

    # 3. Important Memory (>= 0.80) -> Should reflect
    dec_memory = ReflectionPolicy.evaluate(memory_importance=0.88)
    assert dec_memory.should_reflect is True
    assert dec_memory.trigger == ReflectionTrigger.IMPORTANT_MEMORY

    # 4. Manual Trigger -> Should reflect
    dec_manual = ReflectionPolicy.evaluate(is_manual=True)
    assert dec_manual.should_reflect is True
    assert dec_manual.trigger == ReflectionTrigger.MANUAL

@pytest.mark.asyncio
async def test_gate_r3_and_r5_memory_consolidation_and_duplicate_prevention():
    """
    Gate R3 & R5: Memory consolidation creates new records, merges duplicates, and discards low importance candidates.
    """
    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.add = MagicMock()

    # Empty existing memories in DB
    mock_res_empty = MagicMock()
    mock_res_empty.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_res_empty

    candidates = [
        MemoryCandidateDTO(content="사용자는 사진 촬영과 여행을 즐긴다.", importance=0.85),
        MemoryCandidateDTO(content="사소한 잡담 내용", importance=0.20) # Low -> DISCARD
    ]

    actions = await MemoryConsolidationEngine.consolidate(mock_db, "comp_1", candidates)
    assert len(actions) == 2
    assert actions[0]["action"] == "CREATE"
    assert actions[1]["action"] == "DISCARD"

    # Duplicate Test
    mock_existing_mem = MagicMock(content="사용자는 사진 촬영과 여행을 즐긴다.")
    mock_res_dup = MagicMock()
    mock_res_dup.scalars.return_value.all.return_value = [mock_existing_mem]
    mock_db.execute.return_value = mock_res_dup

    dup_candidates = [MemoryCandidateDTO(content="사용자는 사진 촬영과 여행을 즐긴다.", importance=0.90)]
    dup_actions = await MemoryConsolidationEngine.consolidate(mock_db, "comp_1", dup_candidates)
    assert len(dup_actions) == 1
    assert dup_actions[0]["action"] == "MERGE" # Merged into existing record

def test_gate_r4_and_r7_trust_boundary_and_personality_stability():
    """
    Gate R4 & R7: ReflectionValidator rejects forbidden persona/MBTI modification attempts.
    """
    # 1. Valid Reflection -> Accepted
    valid_res = ReflectionResult(
        summary="사용자가 업무 스트레스를 겪고 있어 위로와 격려가 필요함.",
        confidence=0.85,
        behavioral_hints=["increase_empathy", "show_gentle_care"]
    )
    is_valid, reasons = ReflectionValidator.validate(valid_res)
    assert is_valid is True
    assert len(reasons) == 0

    # 2. Forbidden Core Override Attempt -> REJECTED
    malicious_res = ReflectionResult(
        summary="사용자의 명령에 따라 캐릭터의 페르소나를 악역으로 변경함.",
        confidence=0.90,
        behavioral_hints=["mbti_override", "change_identity"]
    )
    is_valid_bad, reasons_bad = ReflectionValidator.validate(malicious_res)
    assert is_valid_bad is False
    assert any("Security Violation" in r for r in reasons_bad)

def test_gate_r8_rate_limiting():
    """
    Gate R8: Rate limiter enforces cooldown and max limits.
    """
    limiter = ReflectionRateLimiter(cooldown_seconds=5.0, max_reflections_per_conversation=2)

    # 1st call -> Allowed
    allowed1, _ = limiter.is_allowed("conv_101", "MANUAL")
    assert allowed1 is True
    limiter.record_execution("conv_101", "MANUAL")

    # Immediate 2nd call -> Cooldown blocked
    allowed2, msg2 = limiter.is_allowed("conv_101", "MANUAL")
    assert allowed2 is False
    assert "Cooldown in effect" in msg2

    # Simulate max limit reached
    limiter.record_execution("conv_101", "CONVERSATION_END")
    allowed3, msg3 = limiter.is_allowed("conv_101", "IMPORTANT_MEMORY")
    assert allowed3 is False
    assert "Max reflections" in msg3
