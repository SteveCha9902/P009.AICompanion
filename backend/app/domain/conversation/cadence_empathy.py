import re
import enum
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

logger = logging.getLogger(__name__)


class ConversationMode(str, enum.Enum):
    NORMAL = "normal"
    EMOTIONAL_SUPPORT = "emotional_support"
    QUIET_EMPATHY = "quiet_empathy"
    INFORMATION = "information"
    PLAYFUL = "playful"
    DEEP_CONVERSATION = "deep_conversation"
    CLOSING = "closing"


class ResponsePolicy(BaseModel):
    """
    Cadence and Empathy policy passed to context builder and quality gate.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    mode: ConversationMode = ConversationMode.NORMAL
    max_preferred_sentences: int = Field(default=3, description="Target sentence count")
    question_allowed: bool = Field(default=True, description="Whether questions are allowed")
    empathy_priority: str = Field(default="normal", description="'low', 'normal', 'high', 'highest'")
    explanation_priority: str = Field(default="normal", description="'low', 'normal', 'high'")
    pressure_level: str = Field(default="normal", description="'none', 'low', 'normal'")
    user_cadence_tier: str = Field(default="normal", description="'short', 'normal', 'long'")


class ConversationFatigueTracker:
    """
    Tracks conversational fatigue and cadences deterministically.
    """
    FATIGUE_KEYWORDS = {
        "힘들", "지쳤", "피곤", "그냥", "몰라", "됐어", "귀찮", "아무것도", "우울", "한숨"
    }
    CLOSING_KEYWORDS = {
        "잘게", "자러", "쉬어야", "그만", "내일 봐", "안녕히", "졸려"
    }
    INFO_KEYWORDS = {
        "얼마", "어떻게", "언제", "왜", "설명", "알려줘", "뭐야", "크기", "스펙"
    }

    @classmethod
    def calculate_fatigue(
        cls,
        user_message: str,
        user_emotion: Optional[str] = None,
        recent_turn_lengths: Optional[List[int]] = None
    ) -> float:
        score = 0.0
        msg = user_message.lower()

        # Keyword match
        if any(kw in msg for kw in cls.FATIGUE_KEYWORDS):
            score += 0.5

        # Short response (e.g. <= 5 chars)
        if len(user_message.strip()) <= 6:
            score += 0.2

        if user_emotion in ["SADNESS", "FRUSTRATION", "EXHAUSTION"]:
            score += 0.3

        return min(1.0, score)


class QuestionBudgetTracker:
    """
    Manages sliding window question budget to prevent question storms.
    """
    def __init__(self, max_questions_per_3_turns: int = 2):
        self.max_questions = max_questions_per_3_turns
        self.recent_questions: List[int] = [] # 1 if question asked, 0 if not

    def record_turn(self, asked_question: bool):
        self.recent_questions.append(1 if asked_question else 0)
        if len(self.recent_questions) > 3:
            self.recent_questions.pop(0)

    def is_question_allowed(self) -> bool:
        return sum(self.recent_questions) < self.max_questions


class ConversationModeResolver:
    """
    Deterministic Mode Resolver mapping user inputs and states to ConversationMode.
    """
    @staticmethod
    def resolve_mode(
        user_message: str,
        user_emotion: Optional[str] = None,
        fatigue_score: float = 0.0,
        question_budget_ok: bool = True
    ) -> ResponsePolicy:
        msg = user_message.lower().strip()

        # 1. Closing Check
        if any(kw in msg for kw in ConversationFatigueTracker.CLOSING_KEYWORDS):
            return ResponsePolicy(
                mode=ConversationMode.CLOSING,
                max_preferred_sentences=1,
                question_allowed=False,
                empathy_priority="normal",
                explanation_priority="low",
                pressure_level="none",
                user_cadence_tier="short"
            )

        # 2. Quiet Empathy Check (High fatigue or explicit exhaustion)
        if fatigue_score >= 0.5 or any(kw in msg for kw in ["힘들", "지쳐", "그냥", "몰라", "우울"]):
            # If user explicitly asked a question or for analysis, allow support
            if "?" in user_message or "생각해줘" in msg or "어떡" in msg:
                return ResponsePolicy(
                    mode=ConversationMode.EMOTIONAL_SUPPORT,
                    max_preferred_sentences=2,
                    question_allowed=True,
                    empathy_priority="highest",
                    explanation_priority="low",
                    pressure_level="low",
                    user_cadence_tier="normal"
                )
            return ResponsePolicy(
                mode=ConversationMode.QUIET_EMPATHY,
                max_preferred_sentences=2,
                question_allowed=False,
                empathy_priority="highest",
                explanation_priority="low",
                pressure_level="none",
                user_cadence_tier="short"
            )

        # 3. Information Mode Check
        if any(kw in msg for kw in ConversationFatigueTracker.INFO_KEYWORDS):
            return ResponsePolicy(
                mode=ConversationMode.INFORMATION,
                max_preferred_sentences=4,
                question_allowed=question_budget_ok,
                empathy_priority="low",
                explanation_priority="high",
                pressure_level="normal",
                user_cadence_tier="long"
            )

        # 4. Emotional Support
        if user_emotion in ["SADNESS", "JOY", "EMPATHY"]:
            return ResponsePolicy(
                mode=ConversationMode.EMOTIONAL_SUPPORT,
                max_preferred_sentences=2,
                question_allowed=question_budget_ok,
                empathy_priority="high",
                explanation_priority="low",
                pressure_level="low",
                user_cadence_tier="normal"
            )

        # 5. Default Normal Mode (Concise by default)
        user_tier = "short" if len(user_message) < 10 else ("long" if len(user_message) > 60 else "normal")
        max_sentences = 1 if user_tier == "short" else (3 if user_tier == "long" else 2)

        return ResponsePolicy(
            mode=ConversationMode.NORMAL,
            max_preferred_sentences=max_sentences,
            question_allowed=question_budget_ok,
            empathy_priority="normal",
            explanation_priority="normal",
            pressure_level="normal",
            user_cadence_tier=user_tier
        )


class ResponseQualityGate:
    """
    Validates and deterministically trims LLM responses to ensure cadence and zero-question policy.
    """
    @staticmethod
    def enforce_policy(response_text: str, policy: ResponsePolicy) -> str:
        text = response_text.strip()
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return response_text

        # 1. Zero-question enforcement for QUIET_EMPATHY and CLOSING
        if not policy.question_allowed or policy.mode in [ConversationMode.QUIET_EMPATHY, ConversationMode.CLOSING]:
            filtered_sentences = [s for s in sentences if not s.endswith("?")]
            if filtered_sentences:
                sentences = filtered_sentences
            else:
                # If all were questions, replace with gentle acknowledgement
                sentences = ["응, 지금은 편안하게 쉬어요."]

        # 2. Sentence count trimming
        if len(sentences) > policy.max_preferred_sentences:
            sentences = sentences[:policy.max_preferred_sentences]

        final_text = " ".join(sentences)
        return final_text
