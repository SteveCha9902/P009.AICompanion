from typing import List, Optional
from app.domain.proactive.proactive_context import ProactiveDialogueStyle

class ProactiveDiversityEngine:
    """
    Guarantees conversational diversity by cycling through 4 core dialogue styles
    and avoiding repetition of recently used topics and starter templates.
    """

    STYLE_CYCLE = [
        ProactiveDialogueStyle.REMINISCENCE,
        ProactiveDialogueStyle.GREETING,
        ProactiveDialogueStyle.ENCOURAGEMENT,
        ProactiveDialogueStyle.OBSERVATION
    ]

    _recent_topics: List[str] = []
    _recent_starters: List[str] = []
    _style_index: int = 0

    @classmethod
    def get_next_style(cls) -> ProactiveDialogueStyle:
        style = cls.STYLE_CYCLE[cls._style_index % len(cls.STYLE_CYCLE)]
        cls._style_index += 1
        return style

    @classmethod
    def is_topic_recently_used(cls, topic: str) -> bool:
        return topic in cls._recent_topics[-3:] # Check last 3 topics

    @classmethod
    def record_usage(cls, topic: str, starter: str) -> None:
        cls._recent_topics.append(topic)
        if len(cls._recent_topics) > 10:
            cls._recent_topics.pop(0)

        cls._recent_starters.append(starter)
        if len(cls._recent_starters) > 10:
            cls._recent_starters.pop(0)

    @classmethod
    def clear_history(cls) -> None:
        cls._recent_topics.clear()
        cls._recent_starters.clear()
        cls._style_index = 0
