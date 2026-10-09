from typing import List
from app.domain.cognitive.decision_types import BehaviorIntent

class ConversationBalanceMonitor:
    """
    Meta-Cognition Layer:
    Monitors companion's conversational balance over recent turns.
    If companion has been asking too many questions consecutively,
    nudges decision towards listening (LISTEN) or gentle response (RESPOND).
    """

    _recent_intents: List[BehaviorIntent] = []

    @classmethod
    def record_intent(cls, intent: BehaviorIntent) -> None:
        cls._recent_intents.append(intent)
        if len(cls._recent_intents) > 10:
            cls._recent_intents.pop(0)

    @classmethod
    def should_suppress_questioning(cls) -> bool:
        """
        Returns True if last 2 turns were both ASK or PROACTIVE_START
        """
        if len(cls._recent_intents) < 2:
            return False
        last_two = cls._recent_intents[-2:]
        return all(i in (BehaviorIntent.ASK, BehaviorIntent.PROACTIVE_START) for i in last_two)

    @classmethod
    def get_recent_intents(cls) -> List[BehaviorIntent]:
        return list(cls._recent_intents)

    @classmethod
    def clear(cls) -> None:
        cls._recent_intents.clear()
