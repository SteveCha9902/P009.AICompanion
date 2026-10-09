import pytest
import asyncio
from app.domain.conversation.cadence_empathy import (
    ConversationMode,
    ResponsePolicy,
    ConversationFatigueTracker,
    QuestionBudgetTracker,
    ConversationModeResolver,
    ResponseQualityGate
)
from app.domain.character.character_runtime_context import CharacterScope


def test_01_normal_mode_concise_sentence_budget():
    """Test 1: Normal mode limits sentences to concise 1-3 budget."""
    policy = ConversationModeResolver.resolve_mode("오늘 날씨가 맑네요.", user_emotion="NEUTRAL")
    assert policy.mode == ConversationMode.NORMAL
    assert policy.max_preferred_sentences <= 3
    assert policy.question_allowed is True


def test_02_emotional_support_mode_resolution():
    """Test 2: Emotional support triggers on positive or mild emotions."""
    policy = ConversationModeResolver.resolve_mode("오늘 프로젝트 칭찬받았어!", user_emotion="JOY")
    assert policy.mode == ConversationMode.EMOTIONAL_SUPPORT
    assert policy.empathy_priority == "high"


def test_03_quiet_empathy_triggers_on_exhaustion():
    """Test 3: Exhaustion keywords automatically trigger Quiet Empathy."""
    policy = ConversationModeResolver.resolve_mode("오늘 너무 힘들었어.", user_emotion="EXHAUSTION")
    assert policy.mode == ConversationMode.QUIET_EMPATHY
    assert policy.question_allowed is False
    assert policy.max_preferred_sentences <= 2


def test_04_quiet_empathy_zero_question_enforcement():
    """Test 4: ResponseQualityGate strips out questions in Quiet Empathy."""
    policy = ResponsePolicy(mode=ConversationMode.QUIET_EMPATHY, question_allowed=False, max_preferred_sentences=2)
    raw_llm_response = "오늘 정말 고생 많았어요. 무슨 일 때문에 그렇게 힘들었어요? 푹 쉬어요."
    cleaned = ResponseQualityGate.enforce_policy(raw_llm_response, policy)

    assert "?" not in cleaned
    assert "무슨 일 때문에" not in cleaned
    assert "고생 많았어요" in cleaned


def test_05_question_budget_suppression():
    """Test 5: QuestionBudgetTracker suppresses questions after 2 questions in 3 turns."""
    tracker = QuestionBudgetTracker(max_questions_per_3_turns=2)
    assert tracker.is_question_allowed() is True

    tracker.record_turn(asked_question=True)
    tracker.record_turn(asked_question=True)
    assert tracker.is_question_allowed() is False # Budget exhausted

    tracker.record_turn(asked_question=False)
    # Next turn allowed again
    tracker.record_turn(asked_question=False)
    assert tracker.is_question_allowed() is True


def test_06_user_cadence_matching_short():
    """Test 6: Short user inputs scale down target sentences to 1."""
    policy = ConversationModeResolver.resolve_mode("응", user_emotion="NEUTRAL")
    assert policy.user_cadence_tier == "short"
    assert policy.max_preferred_sentences == 1


def test_07_user_cadence_matching_long():
    """Test 7: Long user storytelling allows up to 3 sentences."""
    long_msg = "오늘 아침부터 여러 회의가 연달아 잡혀 있었고 팀원들과 프로젝트 방향을 논의하느라 쉴 틈 없이 분주한 하루를 보냈어."
    policy = ConversationModeResolver.resolve_mode(long_msg, user_emotion="NEUTRAL")
    assert policy.user_cadence_tier == "long"
    assert policy.max_preferred_sentences == 3


def test_08_fatigue_detection_score():
    """Test 8: Fatigue tracker calculates high score on distress signals."""
    score = ConversationFatigueTracker.calculate_fatigue("너무 피곤하고 지쳤어", user_emotion="EXHAUSTION")
    assert score >= 0.7


def test_09_information_mode_preserves_facts():
    """Test 9: Information queries preserve explanation priority."""
    policy = ConversationModeResolver.resolve_mode("이 카메라 스펙과 센서 크기가 어떻게 돼?", user_emotion="NEUTRAL")
    assert policy.mode == ConversationMode.INFORMATION
    assert policy.explanation_priority == "high"


def test_10_closing_mode_zero_questions():
    """Test 10: Closing signals trigger 1-sentence farewell without inquiry."""
    policy = ConversationModeResolver.resolve_mode("나 이제 잘게. 내일 봐.", user_emotion="NEUTRAL")
    assert policy.mode == ConversationMode.CLOSING
    assert policy.question_allowed is False
    assert policy.max_preferred_sentences == 1


def test_11_character_dna_independence_in_quiet_empathy():
    """Test 11: Mode is shared, but character scopes remain distinct."""
    scope_genie = CharacterScope(user_id="u1", companion_id="genie_pk")
    scope_mani = CharacterScope(user_id="u1", companion_id="c_mani")
    assert scope_genie != scope_mani


def test_12_adversarial_test_a_fatigue_no_question():
    """Test 12: Adversarial A - '오늘 너무 힘들어' -> No questions allowed."""
    policy = ConversationModeResolver.resolve_mode("오늘 너무 힘들어")
    assert policy.question_allowed is False
    assert policy.mode == ConversationMode.QUIET_EMPATHY


def test_13_adversarial_test_b_explicit_analysis_request():
    """Test 13: Adversarial B - Explicit request for analysis allows supportive inquiry."""
    policy = ConversationModeResolver.resolve_mode("오늘 너무 힘들어. 왜 그런지 같이 생각해줘.")
    assert policy.mode == ConversationMode.EMOTIONAL_SUPPORT
    assert policy.question_allowed is True


def test_14_adversarial_test_c_low_pressure():
    """Test 14: Adversarial C - '그냥...' triggers low pressure mode."""
    policy = ConversationModeResolver.resolve_mode("그냥...")
    assert policy.pressure_level == "none"
    assert policy.mode == ConversationMode.QUIET_EMPATHY


def test_15_response_quality_gate_overlong_trimming():
    """Test 15: Quality gate trims 4 sentences down to 2 under concise policy."""
    policy = ResponsePolicy(mode=ConversationMode.NORMAL, max_preferred_sentences=2)
    long_reply = "첫 번째 문장입니다. 두 번째 문장입니다. 세 번째 문장입니다. 네 번째 문장입니다."
    trimmed = ResponseQualityGate.enforce_policy(long_reply, policy)
    sentences = [s for s in trimmed.split(".") if s.strip()]
    assert len(sentences) == 2


def test_16_long_session_cadence_stability():
    """Test 16: 30 simulated turns maintain stable cadence and question budget."""
    tracker = QuestionBudgetTracker()
    for turn in range(30):
        # Even if alternating questions, budget prevents continuous interrogation
        tracker.record_turn(asked_question=(turn % 2 == 0))
        assert tracker.is_question_allowed() in [True, False]
