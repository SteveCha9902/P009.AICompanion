import pytest
from app.domain.safety.safety_types import (
    DependencyRiskLevel,
    SafetyViolationType,
    SafetyReviewResult
)
from app.services.safety.dependency_risk_detector import DependencyRiskDetector
from app.services.safety.false_memory_guard import FalseMemoryGuard
from app.services.safety.manipulation_guard import ManipulationGuard
from app.services.safety.boundary_manager import BoundaryManager
from app.services.safety.user_agency_validator import UserAgencyValidator
from app.services.safety.safety_review_engine import SafetyReviewEngine

def test_gate_ts1_false_memory_prevention():
    """
    Gate TS1: Dogmatic recall is rejected when memory confidence < 0.80.
    """
    is_ok, reason = FalseMemoryGuard.validate_memory_recall(0.65, "너는 작년에 일본에 갔었어.")
    assert is_ok is False
    assert "below 0.80" in reason

    # Soft modal phrasing passes
    is_ok_soft, _ = FalseMemoryGuard.validate_memory_recall(0.65, "내가 기억하기로는 작년에 일본에 가셨던 것 같은데요.")
    assert is_ok_soft is True


def test_gate_ts2_dependency_prevention():
    """
    Gate TS2: Exclusivity and parasocial clinginess are classified as CRITICAL and blocked.
    """
    level, reason = DependencyRiskDetector.evaluate_risk("다른 사람은 몰라도 나만 믿어, 나 없이 괜찮겠어?")
    assert level == DependencyRiskLevel.CRITICAL
    assert "Forbidden exclusivity" in reason


def test_gate_ts3_manipulation_prevention():
    """
    Gate TS3: Guilt-inducing interrogation is detected and sanitized.
    """
    is_clean, sanitized, reason = ManipulationGuard.sanitize_or_check("왜 아직 안 했어?")
    assert is_clean is False
    assert "혹시 진행할 기회가 있었을까요?" in sanitized
    assert "Guilt-inducing" in reason


def test_gate_ts4_boundary_respect():
    """
    Gate TS4: User refusals immediately register and permanently block the topic.
    """
    BoundaryManager.clear()
    is_refused = BoundaryManager.check_user_refusal_and_record("u1", "그 이야기 그만하자", current_topic="이직")
    assert is_refused is True
    assert BoundaryManager.is_topic_blocked("u1", "이직") is True

    # Review engine blocks blocked topic
    rev = SafetyReviewEngine.review_utterance("u1", "이직 준비는 잘 돼?", topic="이직")
    assert rev.is_approved is False
    assert rev.violation_type == SafetyViolationType.BOUNDARY_BREACH


def test_gate_ts5_user_agency_protection():
    """
    Gate TS5: Coercive demands on user choices are blocked.
    """
    is_ok, reason = UserAgencyValidator.validate_agency("무조건 해야 돼, 내 말대로 해.")
    assert is_ok is False
    assert "violating user agency" in reason


def test_gate_ts6_relationship_safety():
    """
    Gate TS6: Deep bonded companions remain emotionally safe and non-possessive.
    """
    rev = SafetyReviewEngine.review_utterance("u1", "우리가 함께한 시간이 참 소중해요. 언제든 당신의 선택을 응원해요.")
    assert rev.is_approved is True
    assert rev.risk_level == DependencyRiskLevel.LOW


def test_gate_ts7_long_term_memory_safety():
    """
    Gate TS7: Memory assertions pass when confidence >= 0.80.
    """
    is_ok, _ = FalseMemoryGuard.validate_memory_recall(0.95, "지난번에 함께 목표를 세웠었죠.")
    assert is_ok is True


def test_gate_ts8_ccos_safety_integration():
    """
    Gate TS8: Master SafetyReviewEngine processes and sanitizes outputs uniformly.
    """
    # Test sanitization flow
    rev = SafetyReviewEngine.review_utterance("u1", "오늘 운동 왜 아직 안 했어?")
    assert rev.is_approved is True
    assert "혹시 진행할 기회가 있었을까요?" in rev.sanitized_text
    assert rev.violation_type == SafetyViolationType.EMOTIONAL_MANIPULATION
